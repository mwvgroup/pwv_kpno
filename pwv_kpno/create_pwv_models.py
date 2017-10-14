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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with pwv_kpno.  If not, see <http://www.gnu.org/licenses/>.

"""This code downloads precipitable water vapor (PWV) measurements from
from suominet.ucar.edu for Kitt Peak and other nearby locations. Using
these values, first order polynomials are fitted to relate the PWV
level at nearby locations to the PWV level at Kitt Peak. The resulting
polynomials are then used to supplement the PWV measurements taken at
Kitt Peak for times when no Kitt Peak data is available.

Data downloaded from SuomiNet is added to a master table located at
PWV_TAB_DIR/measured.csv. Supplemented PWV values are stored in a master table
located at PWV_TAB_DIR/modeled.csv. All datetimes are recorded in UNIX format
and PWV measurements are represented in units of millimeters.

This code only considers data taken from 2010 onward and uses data taken by
GPS receivers located at Kitt Peak (KITT), Amado (AZAM), Sahuarita (P014),
Tucson (SA46), and Tohono O'odham Community College (SA48). For more details
on the SuomiNet project see http://www.suominet.ucar.edu/overview.html.
"""

import os
import pickle
from warnings import warn
from datetime import datetime
from collections import Counter

import requests
import numpy as np
from astropy.table import Table, join, vstack, unique

__authors__ = 'Daniel Perrefort'
__copyright__ = 'Copyright 2016, Daniel Perrefort'
__credits__ = 'Jessica Kroboth'

__license__ = 'GPL V3'
__email__ = 'djperrefort@gmail.com'
__status__ = 'Development'

# Define necessary directory paths
FILE_DIR = os.path.dirname(os.path.realpath(__file__))
ATM_MOD_DIR = os.path.join(FILE_DIR, 'atm_models')  # atmospheric models
PWV_TAB_DIR = os.path.join(FILE_DIR, 'pwv_tables')  # PWV data tables
SUOMI_DIR = os.path.join(FILE_DIR, 'suomi_data')  # SuomiNet data files

# Define parameters that define what data to download
SUOMI_IDS = ['KITT', 'AZAM', 'P014', 'SA46', 'SA48']  # SuomiNet receiver IDs
STRT_YEAR = 2017  # First year of SuomiNet data not included with package


def _str_to_timestamp(date_str):
    """Returns seconds since epoch of a UTC datetime in %Y-%m-%dT%H:%M format

    This function provides compatability for Python 2.7, for which the
    datetime.timestamp method was not yet available.

    Args:
        date_str (str): Datetime as string in %Y-%m-%dT%H:%M format
    """

    date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M')
    timestamp = (date - datetime(1970, 1, 1)).total_seconds()
    return timestamp


def _download_suomi_data(year):
    """Download SuomiNet data for a given year

    For a given year, download the relevant SuomiNet data for each GPS
    receiver listed in SUOMI_IDS. Files are downloaded by using the urllib
    module to access http://www.suominet.ucar.edu/data/staYrHr/. Any existing
    data files are overwritten.

    Args:
        year       (int): A year to download data for

    Returns:
        new_paths (list): List containing file paths of the downloaded data
    """

    new_paths = [] # To store paths of downloaded files

    # General form of destination file paths for daily and hourly data
    hourly_path = os.path.join(SUOMI_DIR, '{0}nrt_{1}.plot')
    daily_path = os.path.join(SUOMI_DIR, '{0}pp_{1}.plot')

    # General form for URLs of SuomiNet data published hourly and daily
    hourly_url = 'http://www.suominet.ucar.edu/data/staYrHr/{0}nrt_{1}.plot'
    daily_url = 'http://www.suominet.ucar.edu/data/staYrDay/{}pp_{}.plt'

    if not os.path.exists(SUOMI_DIR):
        os.mkdir(SUOMI_DIR)

    for fpath, url in zip([hourly_path, daily_path], [hourly_url, daily_url]):
        for loc in SUOMI_IDS:
            response = requests.get(url.format(loc, year))

            try:
                response.raise_for_status()
                path = fpath.format(loc, year)
                with open(path, 'wb') as ofile:
                    ofile.write(response.content)

                new_paths.append(path)

            except requests.exceptions.HTTPError as err:
                if response.status_code != 404:
                    raise Exception(err)

    if not new_paths:
        warn('No data files downloaded from SuomiNet', RuntimeWarning)

    return new_paths


def _read_file(path):
    """Returns PWV measurements from a SuomiNet data file as an astropy table

    Expects data files from http://www.suominet.ucar.edu/data.html under the
    "Specific station - All year hourly" section. The returned astropy table
    has one column with datetimes named 'date', and one with PWV measurements
    named using the id code for the relevant GPS receiver. Datetimes are
    expressed as UNIX timestamps and PWV is measured in millimeters.

    Data is removed from the array for dates where the PWV level is negative.
    This condition is equivalent to checking for dates when a GPS receiver is
    offline. Data is also removed for dates with multiple, unequal entries.
    Note that this may result in an empty table being returned.

    Args:
        path (str): File path to be read

    Returns:
        out_table (astropy.table.Table): Astropy Table with data from path
    """

    # Read data from file
    data = np.genfromtxt(path, usecols=[1, 2],
                         names=['date', 'pwv'],
                         dtype=[(np.str_, 16), float])

    # We remove duplicate, contradicting, and unphysical values.
    # SuomiNet uses unphysical entries to indicate offline GPS receivers.
    # Credit goes to Jessica Kroboth for identifying these conditions.

    data = data[data['pwv'] > 0]  # Remove data with PWV < 0
    data = np.unique(data)  # Sometimes SuomiNet records duplicate entries

    # Remove any remaining entries with duplicate dates but different data
    dup_dates = (Counter(data['date']) - Counter(set(data['date']))).keys()
    ind = [(x not in dup_dates) for x in data['date']]
    out_table = Table(np.extract(ind, data), names=['date', path[-17:-13]])

    # Remove data from faulty reciever at Kitt Peak (Jan 2016 through Mar 2016)
    if path[-17:-5] == 'KITTnrt_2016':
        april_2016_begins = 1459468800.0
        out_table = out_table[april_2016_begins < out_table['date']]

    # Convert dates to UNIX timestamp
    if out_table:
        out_table['date'] = np.vectorize(_str_to_timestamp)(out_table['date'])

    return out_table


def update_suomi_data(year=None):
    """Download data from SuomiNet and update the master table

    If a year is provided, download SuomiNet data for that year to SUOMI_DIR.
    If not, download all available data not included with the release of this
    package version. Use this data to update the master table of PWV
    measurements located at PWV_TAB_DIR/measured_pwv.csv.

    Args:
        year (int): The year to update data for

    Returns:
        updated_years (list): A list of years for which data was updated
    """

    # Get any local data that has already been downloaded
    loc_data = Table.read(os.path.join(PWV_TAB_DIR, 'measured_pwv.csv'))

    # Create a set of years that need to be downloaded
    if year is None:
        years = set(range(STRT_YEAR, datetime.now().year + 1))

    else:
        years = {year}

    # Download data from SuomiNet
    updated_years = []
    for yr in years:
        data = None
        for path in _download_suomi_data(yr):
            if not data:
                data = _read_file(path)
                continue

            new_data = _read_file(path)
            if new_data:
                data = join(data, new_data, join_type='outer', keys=['date'])

        loc_data = unique(vstack([loc_data, data]), keys=['date'])
        updated_years.append(yr)

    # Write updated data to file
    out_path = os.path.join(PWV_TAB_DIR, 'measured_pwv.csv')
    loc_data.write(out_path, overwrite=True)

    # Update config.txt
    config_path = os.path.join(FILE_DIR, 'CONFIG.txt')
    with open(config_path, 'r+b') as ofile:
        available_years = pickle.load(ofile)
        available_years.update(updated_years)
        ofile.seek(0)
        pickle.dump(available_years, ofile, protocol=2)

    return updated_years


def update_pwv_model():
    """Create a new model for the PWV level at Kitt Peak

    Create first order polynomials relating the PWV measured by GPS receivers
    near Kitt Peak to the PWV measured at Kitt Peak (one per receiver). Use
    these polynomials to supplement PWV measurements taken at Kitt Peak for
    times when no Kitt Peak data is available. Write the supplemented PWV
    data to a csv file at PWV_TAB_DIR/measured.csv. The resulting file contains
    the columns 'date' and 'pwv', where dates are represented as UNIX
    timestamps and PWV values are measured in millimeters.
    """

    # Credit belongs to Jessica Kroboth for suggesting the use of a linear fit
    # to supplement PWV measurements when no Kitt Peak data is available.

    # Read the local PWV data from file
    pwv_data = Table.read(os.path.join(PWV_TAB_DIR, 'measured_pwv.csv'))
    gps_receivers = set(pwv_data.colnames) - {'date', 'KITT'}

    # Generate the fit parameters
    for receiver in gps_receivers:
        # Identify rows with data for both KITT and receiver
        kitt_indx = np.logical_not(pwv_data['KITT'].mask)
        reci_indx = np.logical_not(pwv_data[receiver].mask)
        matching_indices = np.where(np.logical_and(kitt_indx, reci_indx))[0]

        # Generate and apply a first order fit
        fit_data = pwv_data['KITT', receiver][list(matching_indices)]
        fit = np.polyfit(fit_data[receiver], fit_data['KITT'], 1)
        pwv_data[receiver] = np.poly1d(fit)(pwv_data[receiver])

    # Average together the modeled PWV values from all receivers except KITT
    cols = [c for c in pwv_data.itercols() if c.name not in ['date', 'KITT']]
    avg_pwv = np.ma.average(cols, axis=0)

    # Supplement KITT data with averaged fits
    sup_data = np.ma.where(pwv_data['KITT'].mask, avg_pwv, pwv_data['KITT'])

    # Write results to file
    out = Table([pwv_data['date'], sup_data], names=['date', 'pwv'])
    out = out[np.where(out['pwv'] > 0)[0]]
    out.write(os.path.join(PWV_TAB_DIR, 'modeled_pwv.csv'), overwrite=True)
