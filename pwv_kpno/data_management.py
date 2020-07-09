#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

#    This file is part of the pwv_kpno software package.
#
#    The pwv_kpno package is free software: you can redistribute it and/or
#    modify it under the terms of the GNU General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    The pwv_kpno package is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General
#    Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with pwv_kpno.  If not, see <http://www.gnu.org/licenses/>.

"""The ``data_management`` module is responsible for downloading precipitable
water vapor measurements from SuomiNet data servers onto the local machine.
"""

import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Union
from warnings import catch_warnings, simplefilter

import numpy as np
import requests
from astropy.table import Table, unique

PathLike = Union[str, Path]


def find_data_dir() -> Path:
    """Return the directory where local SuomiNet data files are stored

    Returns the path indicated by the environmental variable ``SUOMINET_DIR``.
    If ``SUOMINET_DIR`` is not set, return a path in the installation directory.
    """

    if 'SUOMINET_DIR' in os.environ:
        return Path(os.environ['SUOMINET_DIR']).resolve()

    return Path(__file__).resolve().parent / 'data'


class SuomiDownloader:
    """Handles data downloading from SuomiNet servers to a local directory"""

    def __init__(self, data_dir: Path = None):
        """Handles data downloading from SuomiNet servers to a local directory

        Args:
            data_dir: Optional directory to use instead of package default directory
        """

        self.data_dir = Path(data_dir) if data_dir else find_data_dir()

    @staticmethod
    def _download_suomi_data(url: str, path: PathLike, timeout: float = None):
        """Download SuomiNet data from a URL

        Args:
            url: The url of the data file to download
            path: The path to download to
            timeout: How long to wait before the request times out

        Raises:
            HTTPError
        """

        with catch_warnings():
            simplefilter('ignore')
            response = requests.get(url, timeout=timeout, verify=False)

        # 404 error code means SuomiNet has no data file to download
        if response.status_code != 404:
            response.raise_for_status()
            with open(path, 'wb') as ofile:
                ofile.write(response.content)

    def download_conus_daily(self, receiver_id: str, year: int, timeout=None):
        """Download CONUS data from the SuomiNet daily data releases

        Args:
            receiver_id: Id of the SuomiNet GPS receiver to download data for
            year: Year to download data for
            timeout: How long to wait before the request times out

        Raises:
            HTTPError
        """

        path = self.data_dir / '{}dy_{}.plt'.format(receiver_id, year)
        url = 'https://www.suominet.ucar.edu/data/staYrDay/{}pp_{}.plt'.format(receiver_id, year)
        self._download_suomi_data(url, path, timeout)

    def download_conus_hourly(self, receiver_id: str, year: int, timeout=None):
        """Download CONUS data from the SuomiNet hourly data releases

        Args:
            receiver_id: Id of the SuomiNet GPS receiver to download data for
            year: Year to download data for
            timeout: How long to wait before the request times out

        Raises:
            HTTPError
        """

        path = self.data_dir / '{}hr_{}.plt'.format(receiver_id, year)
        url = 'https://www.suominet.ucar.edu/data/staYrHr/{}nrt_{}.plt'.format(receiver_id, year)
        self._download_suomi_data(url, path, timeout)

    def download_global_daily(self, receiver_id: str, year: int, timeout=None):
        """Download global data from the SuomiNet daily data releases

        Args:
            receiver_id: Id of the SuomiNet GPS receiver to download data for
            year: Year to download data for
            timeout: How long to wait before the request times out

        Raises:
            HTTPError
        """

        path = self.data_dir / '{}gl_{}.plt'.format(receiver_id, year)
        url = 'https://www.suominet.ucar.edu/data/staYrDayGlob/{}nrt_{}.plt'.format(receiver_id, year)
        self._download_suomi_data(url, path, timeout)

    def download_combined_data(self, receiver_id: str, year: int, timeout: float = None):
        """Download SuomiNet data for a given year and SuomiNet id

        Convenience function for downloading any available data from the CONUS
        daily, CONUS hourly, and global daily data releases.

        Args:
            receiver_id: Id of the SuomiNet GPS receiver to download data for
            year: Year to download data for
            timeout: How long to wait before the request times out

        Raises:
            HTTPError
        """

        self.download_conus_daily(receiver_id, year, timeout)
        self.download_conus_hourly(receiver_id, year, timeout)
        self.download_global_daily(receiver_id, year, timeout)


class SuomiFileParser:
    """Callable parser for reading SuomiNet data files"""

    @np.vectorize
    def _suomi_date_to_timestamp(self, year: int, days: Union[str, float]) -> float:
        """Convert the SuomiNet date format into UTC timestamp

        SuomiNet dates are stored as decimal days in a given year. For example,
        February 1st, 00:15 would be 36.01042.

        Args:
            year: The year of the desired timestamp
            days: The number of days that have passed since january 1st

        Returns:
            The seconds from UTC epoch to the provided date as a float
        """

        jan_1st = datetime(year=year, month=1, day=1)
        date = jan_1st + timedelta(days=float(days) - 1)

        # Correct for round off error in SuomiNet date format
        date = date.replace(second=0, microsecond=0)
        while date.minute % 5:
            date += timedelta(minutes=1)

        timestamp = (date - datetime(1970, 1, 1)).total_seconds()
        return timestamp

    @staticmethod
    def _apply_data_cuts(data: Table, data_cuts: dict) -> Table:
        """Apply data cuts from settings to a table of SuomiNet measurements

        Args:
            data: A table containing data from a SuomiNet data file
            data_cuts: Dict of tuples with (upper, lower) bounds for each column

        Returns:
            A copy of the data with applied data cuts
        """

        for param_name, cut_list in data_cuts.items():
            for start, end in cut_list:
                indices = (start < data[param_name]) & (data[param_name] < end)

                # Data cuts on dates specify what data to ignore
                # All others specify what data to include
                if param_name == 'date':
                    indices = ~indices

                data = data[indices]

        return data

    def __call__(self, path: str, data_cuts: dict = None) -> Table:
        """Return PWV measurements from a SuomiNet data file as an astropy table

        Datetimes are expressed as UNIX timestamps and PWV is measured
        in millimeters.

        Data is removed from the array for dates where:
            1. The PWV level is negative (the GPS receiver is offline)
            2. Dates are duplicates with unequal measurements

        Args:
            path: File path to be read
            data_cuts: Dict of tuples with (upper, lower) bounds for each column

        Returns:
            An astropy Table with data from path
        """

        receiver_id = path[-15:-11]
        names = ['date', receiver_id, receiver_id + '_err', 'ZenithDelay',
                 'SrfcPress', 'SrfcTemp', 'SrfcRH']

        data = np.genfromtxt(
            path,
            names=names,
            usecols=range(0, len(names)),
            dtype=[float for _ in names])

        data = Table(data)
        data = data[data[receiver_id] > 0]

        # SuomiNet rounds their error and can report an error of zero
        # We compensate by adding an error of 0.025
        data[receiver_id + '_err'] = np.round(data[receiver_id + '_err'] + 0.025, 3)

        if data:
            data = unique(data, keys='date', keep='none')
            year = int(path[-8: -4])
            data['date'] = self._suomi_date_to_timestamp(year, data['date'])

        if data_cuts:
            # _apply_data_cuts expects column 'date' to have already
            # been converted from the suominet format to timestamps
            data = self._apply_data_cuts(data, data_cuts)

        return data
