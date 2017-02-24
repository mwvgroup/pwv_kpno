#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

#    This file is part of the ATM_PRED module.
#
#    The ATM_PRED module is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    The ATM_PRED module is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Foobar.  If not, see <http://www.gnu.org/licenses/>.

"""This code downloads the most recently available data from SuomiNet. It can
also return information about PWV measurements available on the local machine.
"""

import os
import warnings
from datetime import datetime
from urllib.request import urlretrieve
from urllib.error import HTTPError, ContentTooShortError, URLError

from numpy import genfromtxt, str_, unique, ma
from astropy.units import millimeter
from astropy.table import Table, join

from create_pwv_model import create_fit_functions

__author__ = 'Daniel Perrefort'
__email__ = 'djperrefort@gmail.com'
__copyright__ = 'Copyright 2017, Daniel Perrefort'
__license__ = 'GPL V3'
__status__ = 'Development'

# Define necessary directory paths
SUOMI_DIR = './suomi_data' # Location of SuomiNet data
PWV_TABLES = './pwv_tables' # Location of PWV data tables as .fits files


def _get_suomi_paths():
    """Create a dictionary of filepaths for locally stored SuomiNet data

    Iterate over the files in SUOMI_DIR and create a dictionary of the form
    {year (int): [paths of data files for year (str)]}

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


def _download_suomi_data(year, overwrite=True):
    """Download SuomiNet data for a given year to SUOMI_DIR

    Given a year after 2009, download the relative data files from SuomiNet by
    accessing http://www.suominet.ucar.edu/data/staYrHr/. Download data for the
    KITT, AZAM, P014, SA46 and SA48 receivers. Only overwrite existing files if
    overwrite is True. This function does not update the PWV tables
    (see _create_pwv_table for more information on updating PWV tables).

    Args:
        year (int): A Year after 2009
        overwrite (bool): Whether existing files should be overwritten

    Returns:
        new_data (list): List of locations for which data was downloaded
    """

    # Check for valid args
    if not isinstance(year, int):
        raise ValueError('Argument must be an integer.')

    if year < 2009:
        raise ValueError('No SuomiNet data is available for KPNO before 2010')

    if year > datetime.now().year:
        raise ValueError('Argument cannot be greater than current year')

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
                    warnings.warn('Error connecting to ' + url + '. Code ' +
                                  str(err.code) + ', ' + err.reason)

            except ContentTooShortError:
                raise Exception('Downloaded data is less than expected.' +
                                ' Download from SuomiNet was interrupted.')

            except URLError as err:
                raise Exception('Could not connect to SuomiNet Server. ' +
                                'No error code available.')

    return new_data


def _create_pwv_table(year, overwrite=True):
    """Create a fits table of PWV values for a given year.

    For a given year, use the SuomiNet data in SUOMI_DIR to create a fits table
    of datetimes and PWV values. A separate column is created for each GPS
    receiver. Columns are named 'date' and 'pwv_TAG' where TAG is the
    abbreviated location identifier used by SuomiNet for each GPS receiver.
    The fits file is written to the directory PWV_TABLES.

    Args:
        year (int): A Year after 2009
        overwrite (bool): Whether existing files should be overwritten

    Returns:
        bool: True if the table has been written to file, False otherwise
    """

    # Check for valid args
    if not isinstance(year, int):
        raise ValueError('Year must be a valid integer.')

    if year < 2009:
        raise ValueError('No SuomiNet data is available for KPNO before 2010')

    if year > datetime.now().year:
        raise ValueError('Argument cannot be greater than current year')

    suomi_data = _get_suomi_paths()
    if year not in suomi_data.keys():
        msg = 'SuomiNet data for {0} has not been downloaded'
        raise Exception(msg.format(str(year)))

    # General form of file path of SuomiNet data
    fpath = os.path.join(PWV_TABLES, 'pwv_{0}.fits')

    # For each SuomiNet data file, add data to an astropy table
    # Note that an astropy table cannot be ampty, so we create it
    # with a single row that will be deleted later
    if not os.path.isfile(fpath.format(year)) or overwrite:
        data_table = Table([[0]], names=['date'], dtype=[(str_, 16)])

        for fil in suomi_data[year]:
            data = genfromtxt(fil, usecols=(1, 2),
                  names=('date', 'pwv_' + fil[-17:-13]),
                  dtype=[(str_, 16), float])

            # Keep only unique, non-negative measurements
            #unique_data = unique(data)
            #mask = unique_data['pwv_' + fil[-17:-13]] < 0
            #masked_data = ma.masked_where(mask, unique_data)

            data_table = join(data_table, Table(data),
                              keys=['date'], join_type='outer')

            data_table['pwv_' + fil[-17:-13]].units = millimeter

        # The first row in the table was added when we created the table
        data_table.remove_row(0)
        data_table.write(fpath.format(year), format='fits', overwrite=True)
        return True

    return False


def update_data(year=None, verbose=False):
    """Update the locally stored SuomiNet data

    Update the locally stored PWV data by downloading new data from SuomiNet's
    website. If a valid year is provided, only update data from that year. If
    not, automatically download any data from 2010 on that is not already on
    the local machine.

    Args:
        year (int): A Year after 2009
        verbose (bool): Whether to print status of update process
    """

    if not os.path.isdir(SUOMI_DIR):
        os.makedirs(SUOMI_DIR)

    if not os.path.isdir(PWV_TABLES):
        os.makedirs(PWV_TABLES)

    # Check what data has already been downloaded
    if verbose: print('Checking for local data')
    current_data = set(_get_suomi_paths().keys())
    updated_years = []

    if current_data:
        # Ensure we always update data for the most recently downloaded year
        current_data -= {max(current_data)}

    # Make a list of years to update
    if year is None:
        look_for_years = yr in range(2010, datetime.now().year+1)

    else:
        look_for_years = (year,)

    # Update data for each year
    for yr in look_for_years:
        if yr not in current_data:
            if verbose: print('Downloading data for ', str(year))
            downloaded_data = _download_suomi_data(yr)

            if downloaded_data:
                if verbose: print('Sorting data for ', str(year))
                _create_pwv_table(yr)

                if verbose: print('Creating models for ', str(year))
                create_fit_functions()

                updated_years.append(yr)
                
            elif (not downloaded_data) and verbose:
                print('Could not download data for ', str(year))

    return updated_years


def pwv_data(year, path=None):
    """Return an astropy table of PWV measurements for a given year

    Returns an astropy table of perceptible water vapor measurements for a
    given year as measured by SuomiNet. Values are measured in units of mm. If
    values are available from multiple receivers, include separate columns for
    each receiver.

    Args:
        year (int): The year of the desired PWV data
        path (str): If specified, write data to a fits file at this path

    Returns:
        pwv_data (astropy.table.Table): A table of PWV values in mm
    """

    # Check for valid args
    if not isinstance(year, int):
        raise ValueError('Argument must be an integer.')
    
    if not (path is None or isinstance(path, str)):
        raise ValueError('Path must be a string object.')

    if not year > 2009:
        msg = 'There is no SuomiNet data available for KPNO before 2010'
        raise ValueError(msg)

    # Check if data is available for the given year
    fpath = os.path.join(PWV_TABLES, 'pwv_{0}.fits')
    if not os.path.isfile(fpath.format(year)):
        msg = 'There is no locally available SuomiNet data for {0}.'
        raise ValueError(msg.format(str(year)))

    data = Table.read(fpath.format(year))
    
    if path:
        if not path.endswith('.fits'):
            path += '.fits'

        data.write(path, format='fits', overwrite=True)

    return data


def nearest_value(date, path=None):
    """Search an astropy Table instance for matching datetime information

    Given a datetime, return the nearest percipitable water vapor measurment
    from SuomiNet as an astropy table. If values are available from multiple
    receivers, include separate columns for each receiver.

    Args:
        year (int): An astropy table to be searched
        path (str): If specified, write results to a fits file at this path

    Returns:
        result (Table): An astropy table with the search results
    """

    # Check for valid args
    if not isinstance(date, datetime):
        raise ValueError('Date must be a datetime object.')

    if not (path is None or isinstance(path, str)):
        raise ValueError('Path must be a string object.')

    # Get the appropriate data table
    data_table = pwv_data(date.year)

    # Find the nearest datetime in the table
    nearest = min(data_table["date"], key=lambda x:
                  abs(datetime.strptime(x, '%Y-%m-%dT%H:%M') - date))

    # Find the corresponding row number
    indx = list(data_table["date"]).index(nearest)
    result = data_table[indx]

    if path:
        if not path.endswith('.fits'):
            path += '.fits'

        Table(result).write(path, format='fits', overwrite=True)

    return result

if __name__ == '__main__':
    update_data()

