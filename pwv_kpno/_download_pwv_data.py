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

"""This module downloads precipitable water vapor measurements from
suominet.ucar.edu.
"""

import os
from datetime import datetime, timedelta
from warnings import catch_warnings, simplefilter, warn

import numpy as np
import requests
from astropy.table import Table, join, unique, vstack

from .package_settings import settings

__authors__ = ['Daniel Perrefort']
__copyright__ = 'Copyright 2016, Daniel Perrefort'
__credits__ = ['Jessica Kroboth']

__license__ = 'GPL V3'
__email__ = 'djperrefort@pitt.edu'
__status__ = 'Release'


def _suomi_date_to_timestamp(year, days_str):
    """Convert the SuomiNet date format into UTC timestamp

    SuomiNet dates are stored as decimal days in a given year. For example,
    February 1st, 00:15 would be 36.01042.

    Args:
        year     (int): The year of the desired timestamp
        days_str (str): The number of days that have passed since january 1st

    Returns:
        The seconds from UTC epoch to the provided date as a float
    """

    jan_1st = datetime(year=year, month=1, day=1)
    date = jan_1st + timedelta(days=float(days_str) - 1)

    # Correct for round off error in SuomiNet date format
    date = date.replace(second=0, microsecond=0)
    while date.minute % 5:
        date += timedelta(minutes=1)

    timestamp = (date - datetime(1970, 1, 1)).total_seconds()
    return timestamp


def _apply_data_cuts(data, site_id):
    """Apply data cuts from settings to a table of SuomiNet measurements

    Args:
        data  (Table): Table containing data from a SuomiNet data file
        site_id (str): The site to apply data cuts for
    """

    data = data[data[site_id] > 0]

    # SuomiNet rounds their error and can report an error of zero
    # We compensate by adding an error of 0.025
    data[site_id + '_err'] = np.round(data[site_id + '_err'] + 0.025, 3)

    data_cuts = settings.data_cuts
    if site_id not in data_cuts:
        return data

    for param_name, cut_list in data_cuts[site_id].items():
        for start, end in cut_list:
            indices = (start < data[param_name]) & (data[param_name] < end)

            # Data cuts on dates specify what data to ignore
            # All others specify what data to include
            if param_name == 'date':
                indices = ~indices

            data = data[indices]

    return data


def _read_file(path, apply_cuts=True, pwv_only=True):
    """Return PWV measurements from a SuomiNet data file as an astropy table

    Expects data files from http://www.suominet.ucar.edu/data.html under the
    "Specific station - All year hourly" section. Datetimes are expressed as
    UNIX timestamps and PWV is measured in millimeters.

    Data is removed from the array for dates where:
        1. The PWV level is negative (the GPS receiver is offline)
        2. Dates are duplicates with unequal measurements

    Args:
        path        (str): File path to be read
        apply_cuts (bool): Whether to apply data cuts from the package settings

    Returns:
        An astropy Table with data from path
    """

    # Credit goes to Jessica Kroboth for identifying conditions 1 and 2 above
    site_id = path[-15:-11]
    names = ['date', site_id, site_id + '_err', 'ZenithDelay',
             'SrfcPress', 'SrfcTemp', 'SrfcRH']

    data = np.genfromtxt(path,
                         names=names,
                         usecols=range(0, len(names)),
                         dtype=[float for _ in names])

    data = Table(data)
    if data:
        data = unique(data, keys='date', keep='none')
        year = int(path[-8: -4])
        to_timestamp_vectorized = np.vectorize(_suomi_date_to_timestamp)
        data['date'] = to_timestamp_vectorized(year, data['date'])

    if apply_cuts:
        # Important: _apply_data_cuts expects column 'date' to have already
        # been converted from the suominet format to timestamps
        data = _apply_data_cuts(data, site_id)

    if pwv_only:
        data = data['date', site_id, site_id + '_err']

    return data


def _download_data_for_site(year, site_id, timeout=None):
    """Download SuomiNet data for a given year and SuomiNet id

    For a given year and SuomiNet id, download data from the corresponding GPS
    receiver. Files are downloaded from both the daily and hourly data
    releases. Any existing data files are overwritten.

    Args:
        year      (int): A year to download data for
        site_id   (str): A SuomiNet receiver id code (eg. KITT)
        timeout (float): Optional seconds to wait while connecting to SuomiNet

    Returns:
        A list of file paths containing downloaded data
    """

    # CONUS daily data releases:
    day_path = os.path.join(settings._suomi_dir, '{0}dy_{1}.plt')
    day_url = 'https://www.suominet.ucar.edu/data/staYrDay/{0}pp_{1}.plt'

    # CONUS hourly data releases:
    hour_path = os.path.join(settings._suomi_dir, '{0}hr_{1}.plt')
    hour_url = 'https://www.suominet.ucar.edu/data/staYrHr/{0}nrt_{1}.plt'

    # Global daily releases:
    globl_day_path = os.path.join(settings._suomi_dir, '{0}gl_{1}.plt')
    globl_day_url = 'https://www.suominet.ucar.edu/data/staYrDayGlob/{0}_{1}global.plt'

    # The preferred data should be first in the iteration
    download_data = (
        (globl_day_path, globl_day_url),
        (day_path, day_url),
        (hour_path, hour_url)
    )

    downloaded_paths = []
    for general_path, url in download_data:
        with catch_warnings():
            simplefilter('ignore')
            response = requests.get(url.format(site_id, year),
                                    timeout=timeout, verify=False)

        # 404 error code means SuomiNet has no data file to download
        if response.status_code != 404:
            response.raise_for_status()
            path = general_path.format(site_id, year)
            with open(path, 'wb') as ofile:
                ofile.write(response.content)

            downloaded_paths.append(path)

    return downloaded_paths


def _download_data_for_year(yr, timeout=None):
    """Download and return data for a given year from each SuomiNet receiver

    Downloaded data for each SuomiNet receiver. Return this data as an
    astropy table with all available data from the daily data releases
    supplemented by any hourly release data.

    Args:
        yr        (int): The year of the desired data
        timeout (float): Optional seconds to wait while connecting to SuomiNet

    Returns:
        An astropy Table of the combined downloaded data for the given year.
    """

    combined_data = []
    for site_id in settings.receivers:
        file_paths = _download_data_for_site(yr, site_id, timeout)
        if file_paths:
            site_data = vstack([_read_file(path) for path in file_paths])

            if site_data:
                unique_data = unique(site_data, keys=['date'], keep='first')
                combined_data.append(unique_data)

    if not combined_data:
        warn('No SuomiNet data found for year {}'.format(yr), RuntimeWarning)
        return Table()

    out_data = combined_data.pop()
    while combined_data:
        out_data = join(out_data, combined_data.pop(),
                        join_type='outer', keys=['date'])

    return out_data


def _get_local_data():
    """Return an astropy table containing any local PWV measurements

    Data is returned for the current site set in the package settings
    """

    if os.path.exists(settings._pwv_measured_path):
        return Table.read(settings._pwv_measured_path)

    else:
        col_names = ['date']
        for rec in settings.receivers:
            col_names.append(rec)
            col_names.append(rec + '_err')

        return Table(names=col_names)


def update_local_data(year, timeout=None):
    # type: (int, float) -> bool
    """Download data from SuomiNet for a given year and update the master table

    Args:
        year      (int): The year to update data for
        timeout (float): Optional seconds to wait while connecting to SuomiNet

    Returns:
        A boolean representing whether any data was downloaded
    """

    # Determine what years to download
    if year > datetime.now().year:
        raise ValueError(
            'Cannot download data for years greater than the current year.'
        )

    # Get any local data that has already been downloaded
    local_data = _get_local_data()

    # Download new data from SuomiNet
    new_data = _download_data_for_year(year, timeout)
    stacked_tables = vstack([local_data, new_data])
    if stacked_tables:
        updated_data = unique(stacked_tables, keys=['date'], keep='last')

        # Update local files
        updated_data.write(settings._pwv_measured_path, overwrite=True)
        return True

    else:
        return False
