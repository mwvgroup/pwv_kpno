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
from pathlib import Path
from warnings import catch_warnings, simplefilter

import requests

from .gps_pwv import GPSReceiver
from .types import PathLike


def find_data_dir() -> Path:
    """Return the directory where local SuomiNet data files are stored

    Returns the path indicated by the environmental variable ``SUOMINET_DIR``.
    If ``SUOMINET_DIR`` is not set, return a path in the installation directory.
    """

    if 'SUOMINET_DIR' in os.environ:
        return Path(os.environ['SUOMINET_DIR']).resolve()

    return Path(__file__).resolve().parent / 'suomi_data'


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

    GPSReceiver._reload_from_download[0] = True


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


def download_combined_data(receiver_id: str, year: int, timeout: float = None):
    """Download all available SuomiNet data for a given year and SuomiNet id

    Convenience function for downloading any available data from the CONUS
    daily, CONUS hourly, and global daily data releases.

    Args:
        receiver_id: Id of the SuomiNet GPS receiver to download data for
        year: Year to download data for
        timeout: How long to wait before the request times out

    Raises:
        HTTPError, TimeoutError, ConnectionError
    """

    download_conus_daily(receiver_id, year, timeout)
    download_conus_hourly(receiver_id, year, timeout)
    download_global_daily(receiver_id, year, timeout)