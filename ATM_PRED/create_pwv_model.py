#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

#    This file is part of the atm_pred module.
#
#    The atm_pred module is free software: you can redistribute it and/or
#    modify it under the terms of the GNU General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    The atm_pred module is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with atm_pred.  If not, see <http://www.gnu.org/licenses/>.

"""This code downloads perciptable water vapor (PWV) measurments from SuomiNet
and uses the measured values to create a model for the PWV level at Kitt Peak.
One PWV model is produced per year. Each model is stored as a .csv file with
one collumn for the modeled PWV and one column for the corresponding date.
Dates are represented using UNIX timestamps and occure in 30 minute incriments,
or longer if noSuomiNet data is available for an extended period of time.
"""

import os
from collections import Counter
from datetime import datetime, timedelta
from urllib.request import urlretrieve
from urllib.error import HTTPError, ContentTooShortError, URLError

import numpy as np

__author__ = 'Daniel Perrefort, Jessica Kroboth'
__email__ = ''
__copyright__ = ''
__license__ = 'GPL V3'
__status__ = 'Development'

SUOMI_DIR = './suomi_data'  # Location of SuomiNet data
PWV_MOD_DIR = './pwv_models/'  # Location of PWV models


def _download_suomi_data(year, overwrite=True):
    """Download SuomiNet data for a given year to SUOMI_DIR

    Given a year after 2009, download the data files from SuomiNet for that
    year by accessing http://www.suominet.ucar.edu/data/staYrHr/. Download data
    for the KITT, AZAM, P014, SA46 and SA48 receivers. Only overwrite existing
    files if overwrite is True.

    Args:
        year (int): A Year after 2009
        overwrite (bool): Whether existing files should be overwritten

    Returns:
        new_data (list): List of locations for which data was downloaded
    """

    # List to store locations for which we find SuomiNet data
    new_data = []

    # GPS locations to be checked
    locations = ['KITT', 'AZAM', 'P014', 'SA46', 'SA48']

    # General form of destination file path
    fpath = os.path.join(SUOMI_DIR, '{0}nrt_{1}.plot')

    # General form for URL of SuomiNet data
    url = 'http://www.suominet.ucar.edu/data/staYrHr/{0}nrt_{1}.plot'

    # Download data for each GPS reciever
    for loc in locations:
        if overwrite or not os.path.isfile(fpath.format(loc, year)):
            try:
                urlretrieve(url.format(loc, year), fpath.format(loc, year))
                new_data.append(loc)

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

    return new_data


def _get_suomi_paths():
    """Create a dictionary of filepaths for locally stored SuomiNet data

    Iterate over the files in SUOMI_DIR and create a dictionary of the form
    {year (int): [paths of data files for year (str)]}.

    Args:
        None

    Returns:
        suomi_data (dict): A dictionary of available SuomiNet data
    """

    suomi_data = {}

    files = [f for f in os.listdir(SUOMI_DIR)]
    for file in files:
        if file.endswith('.plot'):
            if int(file[-9:-5]) not in suomi_data.keys():
                suomi_data[int(file[-9:-5])] = []

            suomi_data[int(file[-9:-5])].append(os.path.join(SUOMI_DIR, file))

    return suomi_data


def _read_file(path):
    """Returns contents of a SuomiNet data file as a numpy array

    Expects data files from http://www.suominet.ucar.edu/data.html under the
    "Specific station - All year hourly" section. Data is returned in a
    structured numpy array with the columns 'date', and 'pwv', where dates are
    expressed as UNIX timestamps.

    Data is automatically removed from the array for dates where the PWV
    readout is negative or the preasure falls to -999. Data is also removed for
    dates with duplicate, unequal entries.

    Args:
        path (str): File path to be read

    Returns:
        unix_array (numpy.ndarray): numpy array with data from file
    """

    data = np.genfromtxt(path, usecols=(1, 2, 7),
                         names=('date', 'pwv', 'pres'),
                         dtype=((np.str_, 16), float, float))

    data = np.unique(data)  # Sometimes SuomiNet records duplicate entries

    # Remove data with PWV < 0 or pressure = -999
    data = data[(data['pwv'] > 0) & (data['pres'] != -999)]

    # Remove any remaining entries with duplicate dates but different data
    dup_dates = (Counter(data['date']) - Counter(set(data['date']))).keys()
    ind = [(x not in dup_dates) for x in data['date']]
    data = np.extract(ind, data)

    # Convert dates to UNIX timestamp
    unix_data = [(datetime.strptime(value[0], '%Y-%m-%dT%H:%M').timestamp(),
                  value[1]) for value in data]
    unix_array = np.array(unix_data, dtype=[('date', float), ('pwv', float)])

    return unix_array


def _get_suomi_data():
    """Read all available SuomiNet data from file

    Use the `_read_file` function to read all locally available SuomiNet data
    into memory. Use the data arrays to create a composit dictionary of the
    form {year (int): {location ID (str): PWV data (np.array)}}. The numpy
    arrays have column names 'date', 'pwv', 'pres', 'temp', and 'hum'.

    Args:
        None

    Returns:
        data (dict): A dictionary of file paths returned by _get_suomi_paths
    """

    suomi_paths = _get_suomi_paths()
    data = {yr: {os.path.basename(f)[:4].upper(): _read_file(f) for f in flist}
            for yr, flist in suomi_paths.items()}

    return data


def _create_pwv_fits(data):
    """Create a polynomial relating the PWV from offsite recievers to Kitt Peak

    Use np.polyfit to create a collection of first order polynomials relating
    the PWV measured by recievers near Kitt Peak to the PWV measured at Kitt
    Peak. The parameters of each fit are stored in a dictionary of the form
    {reciever ID (str): [slope (float), y-intercept (float)]}.

    Args:
        data (dict): SuomiNet data as returned by _get_suomi_data()

    Returns:
        pwv_fits (dict): Parameters for the polynomial fit for each site
    """

    pwv_fits = dict()  # To store fit parameters for each reciever
    sites = set([key for subdict in data.values() for key in subdict])

    # Create a fit for each reciever
    for reciever in sites - set(['KITT']):
        k_data = []  # PWV data from Kitt Peak
        o_data = []  # PWV data from other sites

        # Collect the data from all available years into kdata and odata
        for array in data.values():
            if 'KITT' in array and reciever in array:
                match_dates = (set(array['KITT']['date']) &
                               set(array[reciever]['date']))

                k_ind = [(x in match_dates) for x in array['KITT']['date']]
                k_data += list(np.extract(k_ind, array['KITT']['pwv']))

                o_ind = [(x in match_dates) for x in array[reciever]['date']]
                o_data += list(np.extract(o_ind, array[reciever]['pwv']))

        # Fit a first order polynomial relating odata to kdata
        pwv_fits[reciever] = list(np.polyfit(o_data, k_data, 1))

    return pwv_fits


def _dates_in_year(year):
    """Create a list of all UNIX timestamps falling in a given year.

    Dates start at Jan 1st, 00:00:15 and proceed in 30 minute intervals.

    Args:
        year (int): The year to calculate dates for

    Returns:
        dates_unix (list): A list of UNIX timestamps
    """

    dates = [datetime(year=year, month=1, day=1, minute=15)]
    while dates[-1].year == year:
        dates.append(dates[-1] + timedelta(minutes=30))

    dates_unix = [date.timestamp() for date in dates][:-1]
    return dates_unix


def _create_pwv_model(data, year):
    """Model the PWV on Kitt Peak for a given year using SuomiNet Data

    Use SuomiNet data from regions near Kitt Peak to model the PWV level at
    Kitt Peak. The model is returned as a structured numpy array with columns
    'date' and 'pwv', where dates are expressed as unix timestamps.

    Args:
        data (dict): SuomiNet data as returned by _get_suomi_data()
        year  (int): The year to create a model for

    Returns:
        full_model (np.array): Structured array with columns 'date' and 'pwv'
    """

    # If there is only KITT data available, return it
    if list(data[year].keys()) == ['KITT']:
        return data[year]['KITT']

    # For each site, create the polynomial fit functions
    fit_params = _create_pwv_fits(data)
    funcs = {site: np.poly1d(val) for site, val in fit_params.items()}

    # Model the pwv on Kitt Peak using each site / fit function
    for site in data[year]:
        if site != 'KITT':
            data[year][site]['pwv'] = funcs[site](data[year][site]['pwv'])
            data[year][site] = data[year][site][data[year][site]['pwv'] > 0]

    # Create a model for the PWV at Kitt Peak
    combined_data = []
    for date in _dates_in_year(year):
        if 'KITT' in data[year] and date in data[year]['KITT']['date']:
            # Use Kitt data values if available
            index = np.where(data[year]['KITT']['date'] == date)[0][0]
            combined_data.append(data[year]['KITT'][index])

        else:
            # Average together the modeled pwv values for each date
            pwv_vals = []
            for array in data[year].values():
                index = np.where(array['date'] == date)[0]
                if len(index):
                    pwv_vals.append(array['pwv'][index[0]])

            if pwv_vals:
                avg = np.mean(pwv_vals)
                combined_data.append((date, avg))

    full_model = np.array(combined_data,
                          dtype=[('date', float), ('pwv', float)])

    return full_model


def update_models(year=None, overwrite=True):
    """Update the locally stored SuomiNet data and PWV models

    Update the locally stored PWV data by downloading new data from SuomiNet's
    website. Use this date to create a corresponding model for the PWV at Kitt
    Peak. If a year is provided, only update data from that year. If not,
    download any data from 2010 on that is not already on the local machine.

    Args:
        year (int): A Year after 2009
        overwrite (bool): Whether to overwrite existing local data

    Returns:
        None
    """

    # Check for valid args
    if not (isinstance(year, int) or year is None):
        raise ValueError("'year' argument must be an integer.")

    if isinstance(year, int) and year < 2010:
        raise ValueError('No SuomiNet data is available for KPNO before 2010')

    if isinstance(year, int) and year > datetime.now().year:
        raise ValueError("'year' argument cannot be greater than current year")

    if not isinstance(overwrite, bool):
        raise ValueError("'overwrite' argument must be an boolean.")

    # Create any missing directories
    if not os.path.isdir(SUOMI_DIR):
        os.makedirs(SUOMI_DIR)

    if not os.path.isdir(PWV_MOD_DIR):
        os.makedirs(PWV_MOD_DIR)

    # Check what data has already been downloaded
    current_data = set(_get_suomi_paths().keys())

    # Ensure we always update data for the most recently downloaded year
    if current_data:
        current_data -= {max(current_data)}

    # Make a list of years to update
    if year is None:
        look_for_years = range(2010, datetime.now().year+1)
    else:
        look_for_years = range(year, year+1)

    # Download SuomiNet data for each year
    for l_year in look_for_years:
        if l_year not in current_data or overwrite:
            downloaded_data = _download_suomi_data(l_year, overwrite)

    # Create Models for each year
    all_data = _get_suomi_data()
    updated_years = []
    for l_year in look_for_years:
        if l_year not in current_data or overwrite:
            if downloaded_data:
                model = _create_pwv_model(all_data, l_year)
                path = os.path.join(PWV_MOD_DIR, str(l_year) + '.csv')
                np.savetxt(path, model, delimiter=",")
                updated_years.append(l_year)

    return updated_years
