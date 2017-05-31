#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

#    This file is part of the pwv_kpno package.
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

The supplemented PWV values are stored in csv files with one column for the
datetime (in UNIX format) and one column for the supplemented PWV (in mm). One
csv file is produced for each year. This code only considers dates for years
from 2010 onward.

PWV measurements are downloaded from the receivers located at Kitt Peak (KITT),
Amado (AZAM), Sahuarita (P014), Tucson (SA46), and Tohono O'odham Community
College (SA48). For more details on the SuomiNet project see
http://www.suominet.ucar.edu/overview.html.
"""

import os
import pickle
from collections import Counter
from datetime import datetime
from urllib.request import urlretrieve
from urllib.error import HTTPError, ContentTooShortError, URLError

import numpy as np
from astropy.table import Table, join, vstack, unique

__authors__ = 'Daniel Perrefort, Jessica Kroboth'
__copyright__ = 'Copyright 2016, Daniel Perrefort and Jessica Kroboth'
__license__ = 'GPL V3'
__status__ = 'Development'

SUOMI_IDS = ['KITT', 'AZAM', 'P014', 'SA46', 'SA48']  # SuomiNet receiver IDs
PWV_TAB_DIR = './pwv_tables/'  # Where to write un-supplemented PWV data
SUOMI_DIR = './suomi_data'  # Location of raw SuomiNet data files
DIST_YEAR = 2017  # First year of SuomiNet data not included with package


def _download_suomi_data(year, overwrite=True):
    """Download SuomiNet data for a given year

    For a given year, download the relevant SuomiNet data for each GPS
    receiver listed in SUOMI_IDS. Files are downloaded by using the urllib
    module to access http://www.suominet.ucar.edu/data/staYrHr/. Existing
    data files are only overwritten if the overwrite argument is True.

    Args:
        year       (int): A year to download data for
        overwrite (bool): Whether existing files should be overwritten

    Returns:
        new_paths (list): List containing file paths of the downloaded data
    """

    # List to store paths of downloaded files
    new_paths = []

    # General form of destination file path
    fpath = os.path.join(SUOMI_DIR, '{0}nrt_{1}.plot')

    # General form for URL of SuomiNet data
    url = 'http://www.suominet.ucar.edu/data/staYrHr/{0}nrt_{1}.plot'

    # Make sure the necessary directories exist
    if not os.path.exists(SUOMI_DIR):
        os.mkdir(SUOMI_DIR)

    # Download data for each GPS receiver
    for loc in SUOMI_IDS:
        if overwrite or not os.path.isfile(fpath.format(loc, year)):
            try:
                path = fpath.format(loc, year)
                urlretrieve(url.format(loc, year), path)
                new_paths.append(path)

            except HTTPError as err:
                if err.code != 404:
                    raise Exception('Error connecting to ' + url + '. Code ' +
                                    str(err.code) + ', ' + err.reason)

            except ContentTooShortError:
                raise Exception('Downloaded data is less than expected.' +
                                ' Download from SuomiNet was interrupted.')

            except URLError as err:
                raise Exception('Could not connect to SuomiNet Server. ' +
                                'No error code available.')

    return new_paths


def _read_file(path):
    """Returns PWV measurements from a SuomiNet data file as an astropy table

    Expects data files from http://www.suominet.ucar.edu/data.html under the
    "Specific station - All year hourly" section. The returned astropy table
    one column for dates (named 'date') and one for PWV measurements (named
    using the id code of the relevant gaps receiver). Dates are expressed as
    UNIX timestamps and PWV is measured in millimeters.

    Data is removed from the array for dates where the PWV level is negative.
    This condition is equivalent to checking for dates when a GPS receiver is
    offline. Data is also removed for dates with duplicate, unequal entries.
    Note that this may result in an empty array being returned.

    Args:
        path (str): File path to be read

    Returns:
        out_table (astropy.table.Table): Astropy Table with data from file
    """

    # Read data from file
    data = np.genfromtxt(path, usecols=[1, 2],
                         names=['date', 'pwv'],
                         dtype=[(np.str_, 16), float])

    data = data[data['pwv'] > 0]  # Remove data with PWV < 0
    data = np.unique(data)  # Sometimes SuomiNet records duplicate entries

    # Remove any remaining entries with duplicate dates but different data
    dup_dates = (Counter(data['date']) - Counter(set(data['date']))).keys()
    ind = [(x not in dup_dates) for x in data['date']]
    data = np.extract(ind, data)

    # Convert dates to UNIX timestamp
    unix = [(datetime.strptime(value[0], '%Y-%m-%dT%H:%M').timestamp(),
             value[1]) for value in data]
    data = np.array(unix, dtype=[('date', float), (path[-17:-13], float)])
    out_table = Table(data)

    return out_table


def _update_suomi_data(year=None):
    """Download data from SuomiNet and update the master table

    If a year is provided, download SuomiNet data for that year to SUOMI_DIR.
    If not, download all available data not included with the release of this
    package. Use this data to update the master table of PWV measurements
    located at PWV_TAB_DIR/measured_pwv.csv.
    Args:
        years (list): List of years as integers from 2010 onward

    Returns:
        updated_years (list): A list of years for which data was updated
    """

    # Get any data that has already been downloaded
    l_data = Table.read(os.path.join(PWV_TAB_DIR, 'measured_pwv.csv'))

    # Create a set of years that need to be downloaded
    if year is None:
        years = set(range(DIST_YEAR, datetime.now().year + 1))

    else:
        years = set([year])

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

        l_data = unique(vstack([l_data, data]), keys=['date'])
        updated_years.append(yr)

    # Write updated data to file
    l_data.write(os.path.join(PWV_TAB_DIR, 'measured_pwv.csv'), overwrite=True)

    # Update config.txt
    with open('../CONFIG.txt', 'rb') as ofile:
        available_years = pickle.load(ofile)
        available_years.update(updated_years)

    with open('../CONFIG.txt', 'wb') as ofile:
        pickle.dump(available_years, ofile)

    return updated_years


def _update_pwv_model():
    """Create a model for the PWV level at Kitt Peak

    Create a collection of first order polynomials relating the PWV measured
    by GPS receivers near Kitt Peak to the PWV measured at Kitt Peak (one fit
    per receiver). Use these polynomials to supplement PWV measurements taken
    at Kitt Peak for times when no Kitt Peak data is available. Write the
    supplemented PWV values to a csv file at PWV_TAB_DIR/year.csv. The
    resulting file contains the columns 'date' and 'pwv', where dates are
    represented as UNIX timestamps and PWV values are measured in millimeters.

    Args:
        None

    Returns:
        None
    """

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
    out.write(os.path.join(PWV_TAB_DIR, 'modeled_pwv.csv'), overwrite=True)
