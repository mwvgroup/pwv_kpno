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

"""This document contains functions for searching and returning the locally
available PWV data. Functions are also provided to determine what years of
SuomiNet data files have been downloaded to the local machine.
"""

from datetime import datetime

from astropy.table import Table
import numpy as np
from pytz import utc

from ._settings import settings

__authors__ = ['Daniel Perrefort', 'Alexander Afanasyev']
__copyright__ = 'Copyright 2017, Daniel Perrefort'

__license__ = 'GPL V3'
__email__ = 'djperrefort@pitt.edu'
__status__ = 'Development'


def timestamp(date):
    """Returns seconds since epoch of a UTC datetime in %Y-%m-%dT%H:%M format

    This function provides comparability for Python 2.7, for which the
    datetime.timestamp method was not yet available.

    Args:
        date (datetime.datetime): A datetime to find the timestamp for

    Returns:
        The timestamp of the provided datetime as a float
    """

    unix_epoch = datetime(1970, 1, 1, tzinfo=utc)
    utc_date = date.astimezone(utc)
    return (utc_date - unix_epoch).total_seconds()


def _pwv_date(date, airmass=1, test_model=None):
    """Returns the modeled PWV column density at Kitt Peak for a given date

    Interpolate from the modeled PWV column density at Kitt Peak and return
    the PWV column density for a given datetime and airmass.

    Args:
        date    (datetime): The date of the desired PWV column density
        airmass    (float): The airmass along line of sight
        test_model (Table): A mock PWV model used by the test suite

    Returns:
        The modeled PWV column density for Kitt Peak
    """

    if test_model is None:
        pwv_model = Table.read(settings._pwv_model_path)

    else:
        pwv_model = test_model

    # Determine the PWV level along line of sight as pwv(zenith) * airmass
    time_stamp = timestamp(date)
    pwv = np.interp(time_stamp, pwv_model['date'], pwv_model['pwv']) * airmass
    return pwv


def pwv_date(date, airmass=1):
    # This function is a public wrapper for _pwv_date
    """Returns the modeled PWV column density at Kitt Peak for a given date

    Interpolate from the modeled PWV column density at Kitt Peak and return
    the PWV column density for a given datetime and airmass.

    Args:
        date (datetime): The date of the desired PWV column density
        airmass (float): The airmass along line of sight

    Returns:
        The modeled PWV column density for Kitt Peak
    """

    return _pwv_date(date, airmass)


def available_data():
    """Return a list of years for which SuomiNet data has been downloaded

    Return a list of years for which SuomiNet data has been downloaded to the
    local machine. Note that this list includes years for which any amount
    of data has been downloaded. It does not indicate if additional data has
    been released by SuomiNet for a given year that is not locally available.

    Returns:
        A list of years with locally available SuomiNet data
    """

    return sorted(settings.available_years)


def _check_date_time_args(year=None, month=None, day=None, hour=None):
    """Provides type and value checking for date and time arguments

    This function provides argument type and value checking for the functions
    `measured_pwv` and `modeled_pwv`.

    Args:
        year  (int): An integer value between 2010 and the current year
        month (int): An integer value between 1 and 12 (inclusive)
        day   (int): An integer value between 1 and 31 (inclusive)
        hour  (int): An integer value between 0 and 23 (inclusive)
    """

    if year is not None and year < 2010:
        raise ValueError('pwv_kpno does not provide data years prior to 2010')

    elif year is not None and year > datetime.now().year:
        raise ValueError("Argument 'year' (pos 1) is larger than current year")

    arg_constraints = [('month', month, (1, 12)),
                       ('day', day, (1, 31)),
                       ('hour', hour, (0, 23))]

    for arg, value, bounds in arg_constraints:
        if value is not None and not (bounds[0] <= value <= bounds[1]):
            raise ValueError('Invalid value for {0}: {1}'.format(arg, value))


def _search_dt_table(data_tab, **kwargs):
    """Search an astropy table of dates

    Given an astropy table with column 'date', return all entries in the table
    for which there is an object in that column with attributes matching the
    given kwargs.

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


def _read_and_format(path):
    """Reads a PWV data table from file and formats the table and data

    Adds units and converts 'date' column from timestamps to datetimes.

    Args:
        path (str): The path of the file to read

    Returns:
        An astropy table with PWV data
    """

    data = Table.read(path)

    # Convert UNIX timestamps to UTC
    to_datetime = lambda date: datetime.fromtimestamp(date, utc)
    data['date'] = np.vectorize(to_datetime)(data['date'])
    data['date'].unit = 'UTC'

    for colname in data.colnames:
        if colname != 'date':
            data[colname].unit = 'mm'

    return data


def measured_pwv(year=None, month=None, day=None, hour=None):
    """Return an astropy table of PWV measurements taken by SuomiNet

    Return an astropy table of precipitable water vapor (PWV) measurements
    taken by the SuomiNet project. Columns are named using the SuomiNet IDs for
    different locations and contain PWV measurements for that location in
    millimeters. Results can be optionally refined by year, month, day, and
    hour.

    Args:
        year  (int): The year of the desired PWV data
        month (int): The month of the desired PWV data
        day   (int): The day of the desired PWV data
        hour  (int): The hour of the desired PWV data in 24-hour format

    Returns:
        An astropy table of measured PWV values in mm
    """

    _check_date_time_args(year, month, day, hour)
    data = _read_and_format(settings._pwv_measred_path)
    return _search_dt_table(data, year=year, month=month, day=day, hour=hour)


def modeled_pwv(year=None, month=None, day=None, hour=None):
    """Return an astropy table of the modeled PWV at Kitt Peak

    Return a model for the precipitable water vapor level at Kitt Peak as an
    astropy table. PWV measurements are reported in units of millimeters.
    Results can be optionally refined by year, month, day, and hour.

    Args:
        year  (int): The year of the desired PWV data
        month (int): The month of the desired PWV data
        day   (int): The day of the desired PWV data
        hour  (int): The hour of the desired PWV data in 24-hour format

    Returns:
        An astropy table of modeled PWV values in mm
    """

    _check_date_time_args(year, month, day, hour)
    data = _read_and_format(settings._pwv_model_path)
    return _search_dt_table(data, year=year, month=month, day=day, hour=hour)
