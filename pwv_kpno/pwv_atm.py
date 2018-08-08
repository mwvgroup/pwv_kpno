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

"""This module provides access PWV measurements for Kitt Peak and the modeled
PWV transmission function.

For full documentation on a function use the builtin Python `help` function
or see https://mwvgroup.github.io/pwv_kpno/.

An Incomplete Guide to Getting Started:

    To check what years data is locally available for:

      >>> from pwv_kpno import pwv_atm
      >>> pwv_atm.available_data()


    To update the locally available data with any new measurements:

      >>> pwv_atm.update_models()


    To determine the PWV concentration at Kitt Peak for a datetime:

      >>> from datetime import datetime
      >>> import pytz
      >>>
      >>> obsv_date = datetime(year=2013,
      >>>                      month=12,
      >>>                      day=15,
      >>>                      hour=5,
      >>>                      minute=35,
      >>>                      tzinfo=pytz.utc)
      >>>
      >>> pwv = pwv_atm.pwv_date(obsv_date)


    To retrieve the atmospheric model for a line of sight PWV concentration:

      >>> pwv_atm.trans_for_pwv(pwv)


    To retrieve the atmospheric model for a datetime:

      >>> pwv_atm.trans_for_date(date=obsv_date, airmass=1.2)


    To access the PWV measurements as an astropy table:

      >>> # All locally available PWV measurements
      >>> pwv_atm.measured_pwv()
      >>>
      >>> # All PWV measurements taken on November 14, 2016
      >>> pwv_atm.measured_pwv(year=2016, month=11, day=14)


    To access the modeled PWV level at Kitt Peak as an astropy table:

      >>> # The entire model from 2010 to present
      >>> pwv_atm.modeled_pwv()
      >>>
      >>> # The modeled PWV level only for November 14, 2016
      >>> pwv_atm.modeled_pwv(year=2016, month=11, day=14)
"""

import os
from datetime import datetime, timedelta

from astropy.table import Table
import numpy as np
from pytz import utc

from ._package_settings import settings
from ._update_pwv_model import update_models

__authors__ = ['Daniel Perrefort', 'Michael Wood-Vasey']
__copyright__ = 'Copyright 2017, Daniel Perrefort'

__license__ = 'GPL V3'
__email__ = 'djperrefort@pitt.edu'
__status__ = 'Development'


def _timestamp(date):
    # type: (datetime) -> float
    """Returns seconds since epoch of a UTC datetime in %Y-%m-%dT%H:%M format

    This function provides comparability for Python 2.7, for which the
    datetime._timestamp method was not yet available.

    Args:
        date (datetime.datetime): A datetime to find the _timestamp for

    Returns:
        The _timestamp of the provided datetime as a float
    """

    unix_epoch = datetime(1970, 1, 1, tzinfo=utc)
    utc_date = date.astimezone(utc)
    return (utc_date - unix_epoch).total_seconds()


def _raise_available_data(date, pwv_model):
    """Check if a date falls within the range of data in an astropy table

    Args:
        date   (datetime): A timezone aware datetime
        pwv_model (Table): An astropy table containing column 'date'
    """

    if not pwv_model:
        err_msg = 'No PWV data for primary receiver available on local machine.'
        raise RuntimeError(err_msg)

    # Check date falls within the range of available PWV data
    time_stamp = _timestamp(date)
    w_data_less_than = np.where(pwv_model['date'] <= time_stamp)[0]
    if len(w_data_less_than) < 1:
        min_date = datetime.utcfromtimestamp(min(pwv_model['date']))
        msg = 'No PWV data found for datetimes before {0} on local machine'
        raise ValueError(msg.format(min_date))

    w_data_greater_than = np.where(time_stamp <= pwv_model['date'])[0]
    if len(w_data_greater_than) < 1:
        max_date = datetime.utcfromtimestamp(max(pwv_model['date']))
        msg = 'No PWV data found for datetimes after {0} on local machine'
        raise ValueError(msg.format(max_date))

    # Check for SuomiNet data available near the given date
    diff = pwv_model['date'] - time_stamp
    interval = min(diff[diff >= 0]) - max(diff[diff <= 0])
    one_day_in_seconds = 24 * 60 * 60

    if one_day_in_seconds <= interval:
        msg = ('Specified datetime falls within interval of missing SuomiNet' +
               ' data larger than 1 day ({0} interval found).')
        raise ValueError(msg.format(timedelta(seconds=interval)))


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
    _raise_available_data(date, pwv_model)
    time_stamp = _timestamp(date)
    pwv = np.interp(time_stamp, pwv_model['date'], pwv_model['pwv']) * airmass
    return pwv


def pwv_date(date, airmass=1.):
    # type: (datetime, float) -> datetime
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
    # type: () -> list[int]
    """Return a list of years for which SuomiNet data has been downloaded

    Return a list of years for which SuomiNet data has been downloaded to the
    local machine. Note that this list includes years for which any amount
    of data has been downloaded. It does not indicate if additional data has
    been released by SuomiNet for a given year that is not locally available.

    Returns:
        A list of years with locally available SuomiNet data
    """

    return sorted(settings._available_years)


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


def _get_pwv_data_table(path, year, month, day, hour):
    """Reads a PWV data table from file and formats the table and data

    Adds units and converts 'date' column from timestamps to datetimes.

    Args:
        path (str): The path of the file to read

    Returns:
        An astropy table with PWV data
    """

    _check_date_time_args(year, month, day, hour)
    if not os.path.exists(path):
        raise RuntimeError('No data downloaded for current location.')

    data = Table.read(path)
    if data:
        # vectorized callable can not be used on an empty table
        to_datetime = lambda date: datetime.fromtimestamp(date, utc)
        data['date'] = np.vectorize(to_datetime)(data['date'])
        data['date'].unit = 'UTC'

        data = _search_dt_table(data, year=year, month=month, day=day, hour=hour)

    for colname in data.colnames:
        if colname != 'date':
            data[colname].unit = 'mm'

    return data


def measured_pwv(year=None, month=None, day=None, hour=None):
    # type: (int, int, int, int) -> Table
    """Return an astropy table of PWV measurements taken by SuomiNet

    Columns are named using the SuomiNet IDs for different locations. PWV
    measurements each location are recorded in millimeters. Results can be
    optionally refined by year, month, day, and hour.

    Args:
        year  (int): The year of the desired PWV data
        month (int): The month of the desired PWV data
        day   (int): The day of the desired PWV data
        hour  (int): The hour of the desired PWV data in 24-hour format

    Returns:
        An astropy table of measured PWV values in mm
    """

    return _get_pwv_data_table(settings._pwv_measred_path,
                               year, month, day, hour)


def modeled_pwv(year=None, month=None, day=None, hour=None):
    # type: (int, int, int, int) -> Table
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

    return _get_pwv_data_table(settings._pwv_model_path,
                               year, month, day, hour)


def _raise_pwv(pwv):
    """Raise exception if pwv argument has wrong value

    PWV values should be in the range 0 <= pwv <= 30.1

    Args:
        pwv (int, float): A PWV concentration in mm
    """

    if pwv < 0:
        raise ValueError('PWV concentration cannot be negative')


def trans_for_pwv(pwv):
    # type: (float) -> Table
    """Return the atmospheric transmission due a given PWV concentration in mm

    For a given precipitable water vapor concentration, return the modeled
    atmospheric transmission function.

    Args:
        pwv (float): A PWV concentration in mm

    Returns:
        The modeled transmission function as an astropy table
    """

    _raise_pwv(pwv)

    atm_model = Table.read(settings._atm_model_path)
    atm_model['transmission'] = np.exp(- pwv * atm_model['mm_cm_2'])
    atm_model.remove_column('mm_cm_2')
    atm_model['wavelength'].unit = 'angstrom'

    return atm_model


def _raise_transmission_args(date, airmass):
    """Raise exception if arguments have wrong type or value

    Args:
        date    (datetime.datetime): A datetime value
        airmass             (float): An airmass value
    """

    if not isinstance(date, datetime):
        raise TypeError("Argument 'date' (pos 1) must be a datetime instance")

    if date.tzinfo is None:
        err_msg = "Argument 'date' (pos 1) has no timezone information."
        raise ValueError(err_msg)

    if date.year < 2010:
        err_msg = "Cannot model years before 2010 (passed {})"
        raise ValueError(err_msg.format(date.year))

    if date > datetime.now(utc):
        err_msg = "Cannot model dates in the future (passed {})"
        raise ValueError(err_msg.format(date))

    if not isinstance(airmass, (float, int)):
        raise TypeError("Argument 'airmass' (pos 2) must be an int or float")


def _trans_for_date(date, airmass, test_model=None):
    """Return a model for the atmospheric transmission function due to PWV

    Args:
        date (datetime.datetime): The datetime of the desired model
        airmass          (float): The airmass of the desired model
        test_model       (Table): A mock PWV model used by the test suite

    Returns:
        The modeled transmission function as an astropy table
    """

    pwv = _pwv_date(date, airmass, test_model)
    return trans_for_pwv(pwv)


def trans_for_date(date, airmass):
    # type: (datetime, float) -> Table
    """Return a model for the atmospheric transmission function due to PWV

    For a given datetime and airmass, return a model for the atmospheric
    transmission function due to precipitable water vapor at Kitt Peak National
    Observatory.

    Args:
        date (datetime.datetime): The datetime of the desired model
        airmass          (float): The airmass of the desired model

    Returns:
        The modeled transmission function as an astropy table
    """

    return _trans_for_date(date, airmass, test_model=None)

