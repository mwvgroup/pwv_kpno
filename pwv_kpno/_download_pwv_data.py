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

"""This code downloads precipitable water vapor (PWV) measurements from
suominet.ucar.edu for Kitt Peak and other nearby locations. Data is added to a
master table located at PWV_TAB_DIR/measured.csv.
"""

from datetime import datetime, timedelta
import os
from warnings import warn

from astropy.table import Table, join, vstack, unique
import numpy as np
import requests

from ._settings import settings

__authors__ = ['Daniel Perrefort']
__copyright__ = 'Copyright 2016, Daniel Perrefort'
__credits__ = ['Jessica Kroboth']

__license__ = 'GPL V3'
__email__ = 'djperrefort@pitt.edu'
__status__ = 'Development'


def _suomi_date_to_timestamp(year, days_str):
    """Convert the SuomiNet date format to UTC timestamp

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


def _read_file(path):
    """Return PWV measurements from a SuomiNet data file as an astropy table

    Expects data files from http://www.suominet.ucar.edu/data.html under the
    "Specific station - All year hourly" section. Datetimes are expressed as
    UNIX timestamps and PWV is measured in millimeters.

    Data is removed from the array for dates where:
        1. The PWV level is negative (the GPS receiver is offline)
        2. Dates are duplicates with unequal measurements

    Args:
        path (str): File path to be read

    Returns:
        An astropy Table with data from path
    """

    # Credit goes to Jessica Kroboth for identifying conditions 1 and 2

    site_id = path[-15:-11]
    names = ['date', site_id, site_id + '_err', 'ZenithDelay',
             'SrfcPress', 'SrfcTemp', 'SrfcRH']

    data = np.genfromtxt(path,
                         names=names,
                         usecols=range(0, len(names)),
                         dtype=[float for col in names])

    data = data[data[site_id] > 0]
    data[site_id + '_err'] = np.round(data[site_id + '_err'] + 0.025, 3)
    for key, (start, end) in settings._data_cuts(site_id).items():
        indices = (data[key] > start) & (data[key] < end)
        data = data[indices]

    data = Table(data)['date', site_id, site_id + '_err']
    if data:
        data = unique(data, keys='date', keep='none')
        year = int(path[-8: -4])
        to_timestamp_vectorized = np.vectorize(_suomi_date_to_timestamp)
        data['date'] = to_timestamp_vectorized(year, data['date'])

    for start_time, end_time in settings._date_cuts(site_id):
        indices = (data['date'] < start_time) | (data['date'] > end_time)
        data = data[indices]

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

    downloaded_paths = []
    day_path = os.path.join(settings._suomi_dir, '{0}dy_{1}.plt')
    day_url = 'http://www.suominet.ucar.edu/data/staYrDay/{0}pp_{1}.plt'
    hour_path = os.path.join(settings._suomi_dir, '{0}hr_{1}.plt')
    hour_url = 'http://www.suominet.ucar.edu/data/staYrHr/{0}nrt_{1}.plt'

    for general_path, url in ((day_path, day_url), (hour_path, hour_url)):
        response = requests.get(url.format(site_id, year), timeout=timeout)

        if response.status_code != 404:
            response.raise_for_status()

            path = general_path.format(site_id, year)
            with open(path, 'wb') as ofile:
                ofile.write(response.content)

            # The preferred data file should be first in the list
            downloaded_paths.append(path)

    return downloaded_paths


def _download_data_for_year(yr, timeout=None):
    """Download and return data for a given year from available SuomiNet sites

    Downloaded data for each enabled SuomiNet sites. Return this data as an
    astropy table with all available data from the daily data releases
    supplemented by the hourly release data.

    Args:
        yr        (int): The year of the desired data
        timeout (float): Optional seconds to wait while connecting to SuomiNet

    Returns:
        An astropy Table of the combined downloaded data for the given year.
    """

    combined_data = []
    for site_id in settings.receivers:
        file_paths = _download_data_for_site(yr, site_id, timeout)

        try:
            site_data = vstack([_read_file(path) for path in file_paths])
            site_data = unique(site_data, keys=['date'], keep='first')
            combined_data.append(site_data)

        except (TypeError, IndexError):
            continue  # Data files had no unmasked data

    if not combined_data:
        warn('No SuomiNet data found for year {}'.format(yr), RuntimeWarning)
        return Table()

    out_data = combined_data.pop()
    while combined_data:
        out_data = join(out_data, combined_data.pop(),
                        join_type='outer', keys=['date'])

    return out_data


def update_local_data(year=None, timeout=None):
    """Download data from SuomiNet and update PWV_TAB_DIR/measured_pwv.csv

    If a year is provided, download SuomiNet data for that year to SUOMI_DIR.
    If not, download all available data not included with the release of this
    package version. Use this data to update the master table of PWV
    measurements located at PWV_TAB_DIR/measured_pwv.csv.

    Args:
        year      (int): The year to update data for
        timeout (float): Optional seconds to wait while connecting to SuomiNet

    Returns:
        A list of years for which data was updated
    """

    # Get any local data that has already been downloaded
    local_data = Table.read(settings._pwv_measred_path)

    # Determine what years to download
    current_years = settings.available_years
    if year is None:
        all_years = range(2010, datetime.now().year + 1)
        years = [yr for yr in all_years if yr not in current_years]
        years.append(max(current_years))

    else:
        years = {year}

    # Download new data from SuomiNet
    new_years = []
    for yr in years:
        new_data = _download_data_for_year(yr, timeout)
        stacked_tables = vstack([local_data, new_data])
        local_data = unique(stacked_tables, keys=['date'], keep='last')
        new_years.append(yr)

    # Update local files
    local_data.write(settings._pwv_measred_path, overwrite=True)
    current_years.extend(new_years)
    settings._replace_years(current_years)

    return new_years
