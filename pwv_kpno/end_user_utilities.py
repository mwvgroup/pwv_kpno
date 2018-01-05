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

"""This document defines end user functions for accessing / updating PWV data.
Functions contained in this document include `available_data`, `update_models`,
`measured_pwv`, and `modeled_pwv`.
"""

import os
from datetime import datetime

import numpy as np
from pytz import utc
from astropy.table import Table

from .download_suomi_data import update_suomi_data
from .settings import Settings

__author__ = 'Daniel Perrefort'
__copyright__ = 'Copyright 2017, Daniel Perrefort'
__credits__ = ['Alexander Afanasyev']

__license__ = 'GPL V3'
__email__ = 'djperrefort@gmail.com'
__status__ = 'Development'


# Define path of PWV data tables
FILE_DIR = os.path.dirname(os.path.realpath(__file__))
PWV_MSRED_PATH = os.path.join(FILE_DIR, 'locations/{}/measured_pwv.csv')
PWV_MODEL_PATH = os.path.join(FILE_DIR, 'locations/{}/modeled_pwv.csv')


def available_data():
    """Return a list of years for which SuomiNet data has been downloaded

    Return a list of years for which SuomiNet data has been downloaded to the
    local machine. Note that this list includes years for which any amount
    of data has been downloaded. It does not indicate if additional data has
    been released by SuomiNet for a given year that is not locally available.

    Returns:
        A list of years with locally available SuomiNet data
    """

    return sorted(Settings().current_location.available_years)


def _check_date_time_args(year=None, month=None, day=None, hour=None):
    """Provides type and value checking for date and time arguments

    This function provides argument type and value checking for the functions
    `measured_pwv` and `modeled_pwv`.

    Args:
        year  (int): An integer value between 2010 and the current year
        month (int): An integer value between 1 and 12 (inclusive)
        day   (int): An integer value between 1 and 31 (inclusive)
        hour  (int): An integer value between 0 and 23 (inclusive)

    Returns:
        None
    """

    if not (isinstance(year, int) or year is None):
        raise TypeError("Argument 'year' (pos 1) must be an integer")

    elif isinstance(year, int) and year < 2010:
        raise ValueError('pwv_kpno does not provide data years prior to 2010')

    elif isinstance(year, int) and year > datetime.now().year:
        raise ValueError("Argument 'year' (pos 1) is larger than current year")

    def check_type(arg, value, pos, bounds):
        """Check an argument is of an appropriate type and value"""

        if not (isinstance(value, int) or value is None):
            msg = "Argument '{0}' (pos {1}) must be an integer"
            raise TypeError(msg.format(arg, pos))

        if isinstance(value, int) and not (bounds[0] <= value <= bounds[1]):
            raise ValueError('Invalid value for {0}: {1}'.format(arg, value))

    check_type('month', month, 2, (1, 12))
    check_type('day', day, 3, (1, 31))
    check_type('hour', hour, 4, (0, 23))


def _search_dt_table(data_tab, **kwargs):
    """Search an astropy table

    Given an astropy table with column 'date', return all entries in the table
    for which there is an object in date with attributes matching the values
    specified in params

    Args:
        data_tab (astropy.table.Table): An astropy table to search
        **kwargs (): The parameters to search data_tab for

    Returns:
        Entries from data_tab that match search parameters
    """

    # Credit for this function belongs to Alexander Afanasyev
    # https://codereview.stackexchange.com/questions/165811

    def vectorized_callable(obj):
        """Checks if datetime attributes match specified values"""
        return all(getattr(obj, param_name) == param_value
                   for param_name, param_value in kwargs.items()
                   if param_value is not None)

    indexing_func = np.vectorize(vectorized_callable)
    return data_tab[np.where(indexing_func(data_tab['date']))[0]]


def _get_measured_data():
    """Reads in measured PWV data and removes flagged values

    Reads in all measured PWV data for the current location. Remove any data
    for datetimes flagged to ignore. Return results as an astropy table.

    Returns:
        An astropy table with all measured PWV data for the current location
    """

    location_name = Settings().current_location.name
    data = Table.read(PWV_MSRED_PATH.format(location_name))
    location = Settings().current_location

    for site_id in data.colnames:
        if site_id != 'date':
            for start_time, end_time in location[site_id].ignore_timestamps:
                i_start = start_time < data['date']
                i_end = data['date'] < end_time
                mask = np.logical_and(i_start, i_end)
                data[site_id].mask = np.logical_or(data[site_id].mask, mask)

    return data


def measured_pwv(year=None, month=None, day=None, hour=None):
    """Return an astropy table of PWV measurements taken by SuomiNet

    Return an astropy table of precipitable water vapor (PWV) measurements
    taken by the SuomiNet project. The first column is named 'date' and
    contains the UTC datetime of each measurement. Successive columns are
    named using the SuomiNet IDs for different locations and contain PWV
    measurements for that location in millimeters. By default the returned
    table contains all locally available SuomiNet data. Results can be
    refined by year, month, day, and hour by using the keyword arguments.

    Args:
        year  (int): The year of the desired PWV data
        month (int): The month of the desired PWV data
        day   (int): The day of the desired PWV data
        hour  (int): The hour of the desired PWV data in 24-hour format

    Returns:
        An astropy table of measured PWV values in mm
    """

    _check_date_time_args(year, month, day, hour)
    data = _get_measured_data()

    # Convert UNIX timestamps to UTC
    to_datetime = lambda date: datetime.fromtimestamp(date, utc)
    data['date'] = np.vectorize(to_datetime)(data['date'])
    data['date'].unit = 'UTC'

    # Assign units to the remaining columns
    for colname in data.colnames:
        if colname != 'date':
            data[colname].unit = 'mm'

    # Refine results to only include datetimes indicated by kwargs
    return _search_dt_table(data, year=year, month=month, day=day, hour=hour)


def modeled_pwv(year=None, month=None, day=None, hour=None):
    """Return an astropy table of the modeled PWV at Kitt Peak

    Return a model for the precipitable water vapor level at Kitt Peak as an
    astropy table. The first column of the table is named 'date' and contains
    the UTC datetime of each modeled value. The second column is named 'pwv',
    and contains PWV values in millimeters. By default this function returns
    modeled values from 2010 onward. Results can be restricted to a specific
    year, month, day, and hour by using the key word arguments.

    Args:
        year  (int): The year of the desired PWV data
        month (int): The month of the desired PWV data
        day   (int): The day of the desired PWV data
        hour  (int): The hour of the desired PWV data in 24-hour format

    Returns:
        An astropy table of modeled PWV values in mm
    """

    # Check for valid arg types
    _check_date_time_args(year, month, day, hour)

    # Read in SuomiNet measurements from the master table
    location_name = Settings().current_location.name
    data = Table.read(PWV_MODEL_PATH.format(location_name))

    # Convert UNIX timestamps to UTC
    to_datetime = lambda date: datetime.fromtimestamp(date, utc)
    data['date'] = np.vectorize(to_datetime)(data['date'])
    data['date'].unit = 'UTC'
    data['pwv'].unit = 'mm'

    # Refine results to only include datetimes indicated by kwargs
    return _search_dt_table(data, year=year, month=month, day=day, hour=hour)


def _update_pwv_model():
    """Create a new model for the PWV level at Kitt Peak

    Create first order polynomials relating the PWV measured by GPS receivers
    near Kitt Peak to the PWV measured at Kitt Peak (one per off site receiver)
    Use these polynomials to supplement PWV measurements taken at Kitt Peak for
    times when no Kitt Peak data is available. Write the supplemented PWV
    data to a csv file at PWV_TAB_DIR/measured.csv.
    """

    # Credit belongs to Jessica Kroboth for suggesting the use of a linear fit
    # to supplement PWV measurements when no Kitt Peak data is available.

    # Read the local PWV data from file
    pwv_data = _get_measured_data()
    primary = Settings().current_location.primary_receiver
    gps_receivers = set(pwv_data.colnames) - {'date', primary}

    # Generate the fit parameters
    for receiver in gps_receivers:
        # Identify rows with data for both KITT and receiver
        primary_index = np.logical_not(pwv_data[primary].mask)
        receiver_index = np.logical_not(pwv_data[receiver].mask)
        matching_indices = np.logical_and(primary_index, receiver_index)

        # Generate and apply a first order fit
        fit_data = pwv_data[primary, receiver][list(matching_indices)]
        fit = np.polyfit(fit_data[receiver], fit_data[primary], 1)
        pwv_data[receiver] = np.poly1d(fit)(pwv_data[receiver])

    # Average together the modeled PWV values from all receivers except KITT
    cols = [c for c in pwv_data.itercols() if c.name not in ['date', primary]]
    avg_pwv = np.ma.average(cols, axis=0)

    # Supplement KITT data with averaged fits
    sup_data = np.ma.where(pwv_data[primary].mask, avg_pwv, pwv_data[primary])

    out = Table([pwv_data['date'], sup_data], names=['date', 'pwv'])
    out = out[out['pwv'] > 0]

    location_name = Settings().current_location.name
    out.write(PWV_MODEL_PATH.format(location_name), overwrite=True)


def update_models(year=None):
    """Download data from SuomiNet and update the locally stored PWV model

    Update the locally available SuomiNet data by downloading new data from
    the SuomiNet website. Use this data to create an updated model for the PWV
    level at Kitt Peak. If a year is provided, only update data for that year.
    If not, download all available data from 2017 onward. Data for years from
    2010 through 2016 is included with this package version by default.

    Args:
        year (int): A Year from 2010 onward

    Returns:
        A list of years for which models where updated
    """

    # Check for valid args
    if not (isinstance(year, int) or year is None):
        raise TypeError("Argument 'year' must be an integer")

    if isinstance(year, int):
        if year < 2010:
            raise ValueError('Cannot update models for years prior to 2010')

        elif year > datetime.now().year:
            msg = 'Cannot update models for years greater than current year'
            raise ValueError(msg)

    # Update the local SuomiData and PWV models
    updated_years = update_suomi_data(year)
    _update_pwv_model()
    return sorted(updated_years)
