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
water vapor measurements from SuomiNet onto the local machine.
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Union
from warnings import catch_warnings, simplefilter

import numpy as np
import requests
from requests.exceptions import HTTPError, ConnectionError

from .types import PathLike


def find_data_dir() -> Path:
    """Return the directory where local SuomiNet data files are stored

    Returns the path indicated by the environmental variable ``SUOMINET_DIR``.
    If ``SUOMINET_DIR`` is not set, return a path in the installation directory.
    """

    if 'SUOMINET_DIR' in os.environ:
        directory = Path(os.environ['SUOMINET_DIR']).resolve()

    else:
        directory = Path(__file__).resolve().parent / 'suomi_data'

    directory.mkdir(exist_ok=True, parents=True)
    return directory


def _download_suomi_data(url: str, path: PathLike, timeout: float = None):
    """Download SuomiNet data from a URL

    Args:
        url: The url of the data file to download
        path: The path to download to
        timeout: How long to wait before the request times out

    Raises:
        HTTPError, TimeoutError, ConnectionError
    """

    with catch_warnings():
        simplefilter('ignore')
        response = requests.get(url, timeout=timeout, verify=False)

    # 404 error code means SuomiNet has no data file to download
    if response.status_code != 404:
        response.raise_for_status()
        with open(path, 'wb') as ofile:
            ofile.write(response.content)


def download_conus_daily(receiver_id: str, year: int, timeout=None):
    """Download CONUS data from the SuomiNet daily data releases

    Args:
        receiver_id: Id of the SuomiNet GPS receiver to download data for
        year: Year to download data for
        timeout: How long to wait before the request times out

    Raises:
        HTTPError, TimeoutError, ConnectionError
    """

    path = find_data_dir() / '{}dy_{}.plt'.format(receiver_id, year)
    url = 'https://www.suominet.ucar.edu/data/staYrDay/{}pp_{}.plt'.format(receiver_id, year)
    _download_suomi_data(url, path, timeout)


def download_conus_hourly(receiver_id: str, year: int, timeout=None):
    """Download CONUS data from the SuomiNet hourly data releases

    Args:
        receiver_id: Id of the SuomiNet GPS receiver to download data for
        year: Year to download data for
        timeout: How long to wait before the request times out

    Raises:
        HTTPError, TimeoutError, ConnectionError
    """

    path = find_data_dir() / '{}hr_{}.plt'.format(receiver_id, year)
    url = 'https://www.suominet.ucar.edu/data/staYrHr/{}nrt_{}.plt'.format(receiver_id, year)
    _download_suomi_data(url, path, timeout)


def download_global_daily(receiver_id: str, year: int, timeout=None):
    """Download global data from the SuomiNet daily data releases

    Args:
        receiver_id: Id of the SuomiNet GPS receiver to download data for
        year: Year to download data for
        timeout: How long to wait before the request times out

    Raises:
        HTTPError, TimeoutError, ConnectionError
    """

    path = find_data_dir() / '{}gl_{}.plt'.format(receiver_id, year)
    url = 'https://www.suominet.ucar.edu/data/staYrDayGlob/{}nrt_{}.plt'.format(receiver_id, year)
    _download_suomi_data(url, path, timeout)


def download_available_data(receiver_id: str, year: Union[int, List] = None, timeout: float = None) -> List:
    """Download all available SuomiNet data for a given year and SuomiNet id

    Convenience function for downloading any available data from the CONUS
    daily, CONUS hourly, and global daily data releases. If no year is
    specified, all available data is downloaded for years 2010 onward.

    Args:
        receiver_id: Id of the SuomiNet GPS receiver to download data for
        year: Year to download data for
        timeout: How long to wait before the request times out

    Returns:
        List of downloaded years

    Raises:
        HTTPError, TimeoutError, ConnectionError
    """

    download_operations = (
        download_conus_hourly,
        download_conus_daily,
        download_global_daily
    )

    if year is None:
        year = np.arange(2010, datetime.now().year + 1)

    successful_years = set()
    for yr in np.array(year):  # Typecasting to array ensures argument is iterable
        for download_func in download_operations:
            try:
                download_func(receiver_id, yr, timeout)

            except (TimeoutError, HTTPError, ConnectionError):
                continue

            successful_years.add(yr)

    return sorted(successful_years)


def check_downloaded_receivers() -> List[str]:
    """Return a list of receiver Id's that have data downloaded to the current environment

    Returns:
        A list of Id's for SuomiNet GPS receivers
    """

    return sorted(set(fpath.stem[:4] for fpath in find_data_dir().glob(f'*.plt')))


def check_downloaded_data(receiver_id: str) -> Dict[str, List[int]]:
    """Determine which data files have been downloaded for a given receiver Id

    Args:
        receiver_id: Id of a SuomiNet GPS receiver to check for downloaded data

    Returns:
        A dictionary of the form {<release type>: <list of years>}
    """

    data_dir = find_data_dir()
    available_years = {'global': [], 'daily': [], 'hourly': []}
    release_type = {'gl': 'global', 'dy': 'daily', 'hr': 'hourly'}
    for fpath in data_dir.glob(f'{receiver_id}*.plt'):
        year = int(fpath.stem[-4:])
        data_type = release_type[fpath.stem[4:6]]
        available_years[data_type].append(year)

    available_years['global'] = sorted(available_years['global'])
    available_years['daily'] = sorted(available_years['daily'])
    available_years['hourly'] = sorted(available_years['hourly'])
    return available_years


def delete_local_data(receiver_id: str, years: list = None, release_type: str = None, verbose=False):
    """Delete downloaded SuomiNet data from the current environment

     Args:
         receiver_id: Id of a SuomiNet GPS receiver to check for downloaded data
         years: List of years to delete data from (defaults to all available years)
         release_type: Release type to delete data for (defaults to all available types)
         verbose: Print deleted file paths to system output
     """

    # Default to a file pattern that includes all data types and years
    years = years if years else ['*']
    release_type = release_type if release_type else '*'
    path_pattern = f'{receiver_id}{release_type}_{{}}.plt'

    # Delete all data matching the file pattern
    data_dir = find_data_dir()
    for year in years:
        for file in data_dir.glob(path_pattern.format(year)):
            if verbose:
                print(f'Deleting {file.resolve()}')

            file.unlink()
