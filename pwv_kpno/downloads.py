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

"""The ``downloads`` module is responsible for downloading precipitable
water vapor measurements from SuomiNet servers onto the local machine.
Data files are stored on the local machine in one of the following locations:

1. If a specific directory is specified at the time of download,
   data files are downloaded to that directory.
2. If the variable ``SUOMINET_DIR`` is set in the working environment, data is
   downloaded to the directory assigned to that variable.
3. If neither of the above cases are satisfied, data is downloaded into the
   installation directory of ``pwv_kpno`` package.

Module API
----------
"""

import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Collection, List, Union
from warnings import catch_warnings, simplefilter

import numpy as np
import requests
from requests.exceptions import ConnectionError, HTTPError
from tqdm import tqdm

from .types import PathLike


class URLDownload:
    """Handles the downloading of SuomiNet data files from arbitrary URLs"""

    def __init__(self, data_dir: PathLike = None):
        """Handles the downloading of data files from arbitrary URLs

        Data is downloaded to which ever of the following directories is
        resolved first:
            1. The location specified by the ``data_dir`` variable at innit
            2. The location defined by the ``SUOMINET_DIR`` environmental variable
            3. Internally within the package's installation directory

        Args:
            data_dir: Overrides the default path to download data to
        """

        self._data_dir = Path(data_dir) if data_dir else self._find_default_data_dir()

    @property
    def data_dir(self) -> Path:
        """Location of SuomiNet data on the local machine"""

        return self._data_dir

    @staticmethod
    def _find_default_data_dir() -> Path:
        """Return the directory where local SuomiNet data files are stored

        Return the path indicated by the environmental variable
        ``SUOMINET_DIR``. If ``SUOMINET_DIR`` is not set, return a path in the
        installation directory.
        """

        if 'SUOMINET_DIR' in os.environ:
            directory = Path(os.environ['SUOMINET_DIR']).resolve()

        else:
            directory = Path(__file__).resolve().parent / 'suomi_data'

        directory.mkdir(exist_ok=True, parents=True)
        return directory

    def download_suomi_url(self, url: str, fname: str, timeout: float = None,
                           force: bool = False, verbose: bool = True):
        """Download data from a URL

        Args:
            url: The url of the data file to download
            fname: The name of the file to write to
            timeout: How long to wait before the request times out
            force: Execute download even if local data already exists
            verbose: Display a progress bar

        Raises:
            HTTPError, TimeoutError, ConnectionError
        """

        out_path = self._data_dir / fname
        if out_path.exists() and not force:
            return

        with catch_warnings():
            simplefilter('ignore')
            response = requests.get(url, stream=True, timeout=timeout, verify=False)

        # 404 error code means SuomiNet has no data file to download
        if response.status_code != 404:
            response.raise_for_status()

            chunk_size = 1024
            with open(out_path, 'wb') as ofile:
                with tqdm(
                        unit='B',
                        unit_scale=True,
                        unit_divisor=chunk_size,
                        file=sys.stdout,
                        desc=out_path.stem,
                        disable=not verbose,
                        total=int(response.headers.get('content-length', 0)),
                ) as pbar:
                    for data in response.iter_content(chunk_size=chunk_size):
                        pbar.update(ofile.write(data))

    def __repr__(self) -> str:
        return "URLDownload('{}')".format(self._data_dir)


class ReleaseDownloader(URLDownload):
    """Handles the downloading of specific SuomiNet data releases"""

    def __init__(self, receiver_id: str, data_dir: PathLike = None):
        """Handles the downloading of specific SuomiNet data releases

        Args:
            receiver_id: Id of the SuomiNet GPS receiver to download data for
            data_dir: Overrides the default path to download data to
        """

        super().__init__(data_dir)
        self.receiver_id = receiver_id.upper()

    def download_conus_daily(self, year: int, timeout=None, force: bool = False, verbose: bool = True):
        """Download CONUS data from the SuomiNet daily data releases

        Args:
            year: Year to download data for
            timeout: How long to wait before the request times out
            force: Execute download even if local data already exists
            verbose: Display a progress bar

        Raises:
            HTTPError, TimeoutError, ConnectionError
        """

        fname = '{}dy_{}.plt'.format(self.receiver_id.upper(), year)
        url = 'https://www.suominet.ucar.edu/data/staYrDay/{}pp_{}.plt'.format(self.receiver_id, year)
        self.download_suomi_url(url, fname, timeout, force, verbose)

    def download_conus_hourly(self, year: int, timeout=None, force: bool = False, verbose: bool = True):
        """Download CONUS data from the SuomiNet hourly data releases

        Args:
            year: Year to download data for
            timeout: How long to wait before the request times out
            force: Execute download even if local data already exists
            verbose: Display a progress bar

        Raises:
            HTTPError, TimeoutError, ConnectionError
        """

        fname = '{}hr_{}.plt'.format(self.receiver_id.upper(), year)
        url = 'https://www.suominet.ucar.edu/data/staYrHr/{}nrt_{}.plt'.format(self.receiver_id, year)
        self.download_suomi_url(url, fname, timeout, force, verbose)

    def download_global_daily(self, year: int, timeout=None, force: bool = False, verbose: bool = True):
        """Download global data from the SuomiNet daily data releases

        Args:
            year: Year to download data for
            timeout: How long to wait before the request times out
            force: Execute download even if local data already exists
            verbose: Display a progress bar

        Raises:
            HTTPError, TimeoutError, ConnectionError
        """

        fname = '{}_{}global.plt'.format(self.receiver_id.upper(), year)
        url = 'https://www.suominet.ucar.edu/data/staYrDayGlob/{}_{}global.plt'.format(self.receiver_id, year)
        self.download_suomi_url(url, fname, timeout, force, verbose)

    def __repr__(self) -> str:
        return "ReleaseDownloader('{}', '{}')".format(self.receiver_id, self._data_dir)


class DownloadManager(URLDownload):
    """Manages SuomiNet data accessible from the current environment"""

    def check_downloaded_receivers(self) -> List[str]:
        """Return a list of receiver Id's that have data downloaded to the current environment

        Returns:
            A list of Id's for SuomiNet GPS receivers
        """

        return sorted(set(fpath.stem[:4] for fpath in self._data_dir.glob(f'*.plt')))

    def check_downloaded_data(self, receiver_id: str) -> Dict[str, List[int]]:
        """Determine which data files have been downloaded for a given receiver Id

        Args:
            receiver_id: Id of a SuomiNet GPS receiver to check for downloaded data

        Returns:
            A dictionary of the form {<release type>: <list of years>}
        """

        available_years = {'global': [], 'daily': [], 'hourly': []}
        release_type = {'gl': 'global', 'dy': 'daily', 'hr': 'hourly'}
        for fpath in self._data_dir.glob('{}*.plt'.format(receiver_id.upper())):
            year = int(fpath.stem[-4:])
            data_type = release_type[fpath.stem[4:6]]
            available_years[data_type].append(year)

        available_years['global'] = sorted(available_years['global'])
        available_years['daily'] = sorted(available_years['daily'])
        available_years['hourly'] = sorted(available_years['hourly'])
        return available_years

    def delete_local_data(self, receiver_id: str, years: Collection[int] = None,
                          dry_run: bool = False) -> List[Path]:
        """Delete downloaded SuomiNet data from the current environment

         Args:
             receiver_id: Id of a SuomiNet GPS receiver to check for downloaded data
             years: List of years to delete data from (defaults to all available years)
             dry_run: Returns a list of files that would be deleted without actually deleting them

         Returns:
             - A list of file paths that were deleted
         """

        # Default to a file pattern that includes all data types and years
        years = years if years else ['*']
        release_type = '*'
        path_pattern = '{}{}_{{}}.plt'.format(receiver_id.upper(), release_type)

        # Delete all data matching the file pattern
        out_files = []
        for year in years:
            for file in self._data_dir.glob(path_pattern.format(year)):
                out_files.append(file)

                if not dry_run:
                    file.unlink()

        return out_files

    @staticmethod
    def download_available_data(
            receiver_id: str, year: Union[int, Collection[int]] = None,
            timeout: float = None, force: bool = False, verbose: bool = True):
        """Download all available SuomiNet data for a given year and SuomiNet id

        Convenience function for downloading any available data from the CONUS
        daily, CONUS hourly, and global daily data releases. If no year is
        specified, all available data is downloaded for years 2010 onward.

        Args:
            receiver_id: Id of the SuomiNet GPS receiver to download data for
            year: Year to download data for
            timeout: How long to wait before the request times out
            force: Execute download even if local data already exists
            verbose: Display progress bars for the downloading files
        """

        release_downloader = ReleaseDownloader(receiver_id)
        download_operations = (
            release_downloader.download_conus_hourly,
            release_downloader.download_conus_daily,
            release_downloader.download_global_daily
        )

        if year is None:
            year = np.arange(datetime.now().year - 5, datetime.now().year + 1)

        for yr in np.atleast_1d(year):  # Typecasting to array ensures argument is iterable
            for download_func in download_operations:
                try:
                    # noinspection PyArgumentList
                    download_func(yr, timeout, force, verbose)

                except (TimeoutError, HTTPError, ConnectionError):
                    continue

    def __repr__(self) -> str:
        return "DownloadManager('{}')".format(self._data_dir)
