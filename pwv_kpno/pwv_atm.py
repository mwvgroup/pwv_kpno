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

"""This module provides access precipitable water vapor (PWV) measurements and
the modeled atmospheric transmission due to PWV.

For full documentation on a function use the builtin Python `help` function
or see https://mwvgroup.github.io/pwv_kpno/.

An incomplete guide to getting started:

    To check what years data is locally available for the current site being
    modeled:

      >>> from pwv_kpno import pwv_atm
      >>> pwv_atm.downloaded_years()


    To update the locally available data with any new SuomiNet measurements:

      >>> pwv_atm.update_models()


    To determine the PWV concentration at the current site being modeled for a
    a given datetime:

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
      >>> pwv, pwv_err = pwv_atm.pwv_date(obsv_date)


    To retrieve the atmospheric model for a line of sight PWV concentration
    (Note that this model will be the same regardless of the site being
    modeled. Thankfully the physics of the light passing through atmosphere
    don't depend on our geographic location!):

      >>> # With a known error
      >>> pwv_atm.trans_for_pwv(pwv)
      >>>
      >>> # Without any error propagation
      >>> pwv_atm.trans_for_pwv(pwv, pwv_err)


    To retrieve the atmospheric model for at the current site being modeled
    at a given datetime and airmass:

      >>> pwv_atm.trans_for_date(date=obsv_date, airmass=1.2)


    To access the PWV measurements for the current site being modeled as an
    astropy table:

      >>> # All locally available PWV measurements
      >>> pwv_atm.measured_pwv()
      >>>
      >>> # All PWV measurements taken on November 14, 2016
      >>> pwv_atm.measured_pwv(year=2016, month=11, day=14)


    To access the modeled PWV level at at the current site being modeled as an
    astropy table:

      >>> # The entire model from 2010 to present
      >>> pwv_atm.modeled_pwv()
      >>>
      >>> # The modeled PWV level only for November 14, 2016
      >>> pwv_atm.modeled_pwv(year=2016, month=11, day=14)
"""

import os
from datetime import datetime, timedelta
from glob import glob
from typing import Tuple, Union

import numpy as np
from astropy.table import Table, unique, vstack
from pytz import utc
from scipy.stats import binned_statistic

from ._download_pwv_data import _read_file
from ._update_pwv_model import update_models
from .package_settings import settings

__authors__ = ['Daniel Perrefort', 'Michael Wood-Vasey']
__copyright__ = 'Copyright 2017, Daniel Perrefort'

__license__ = 'GPL V3'
__email__ = 'djperrefort@pitt.edu'
__status__ = 'Release'


def _timestamp(date):
    """Returns seconds since epoch of a UTC datetime in %Y-%m-%dT%H:%M format

    This function provides comparability for Python 2.7, for which the
    datetime.timestamp method was not yet available.

    Args:
        date (datetime): A datetime to find the _timestamp for

    Returns:
        The timestamp of the provided datetime as a float
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


def _pwv_date(date, airmass=1., test_model=None):
    """Returns the modeled PWV column density at the current site

    Interpolate from the modeled PWV column density at at the current site
    being modeled and return the PWV column density for a given datetime and
    airmass.

    Args:
        date    (datetime): The date of the desired PWV column density
        airmass    (float): The airmass along line of sight
        test_model (Table): A mock PWV model used by the test suite

    Returns:
        The modeled PWV column density at the current site
        The error in modeled PWV column density
    """

    if test_model is None:
        pwv_model = Table.read(settings._pwv_modeled_path)

    else:
        pwv_model = test_model

    _raise_available_data(date, pwv_model)
    time_stamp = _timestamp(date)
    pwv = np.interp(time_stamp, pwv_model['date'], pwv_model['pwv'])
    pwv_err = np.interp(time_stamp, pwv_model['date'], pwv_model['pwv_err'])

    # Determine the PWV level along line of sight as outlined in
    # Horne et al. 2012
    pwv_los = pwv * (airmass ** .6)
    pwv_err_los = pwv_err * (airmass ** .6)
    return pwv_los, pwv_err_los


def pwv_date(date, airmass=1.):
    # type: (datetime, float) -> Tuple[float, float]
    """Returns the modeled PWV column density at the current site

    Interpolate from the modeled PWV column density at the current site being
    modeled and return the PWV column density for a given datetime and airmass.

    Args:
        date (datetime): The date of the desired PWV column density
        airmass (float): The airmass along line of sight

    Returns:
        The modeled PWV column density at the current site
        The error in modeled PWV column density
    """

    return _pwv_date(date, airmass)


def downloaded_years():
    # type: () -> list[int]
    """Return a list of years for which SuomiNet data has been downloaded

    Return a list of years for which SuomiNet data has been downloaded to the
    local machine. Note that this list includes years for which any amount
    of data has been downloaded. It does not indicate if additional data has
    been released by SuomiNet for a given year that is not locally available.

    Returns:
        A list of years with locally available SuomiNet data
    """

    return sorted(settings._downloaded_years)


def _check_date_time_args(year=None, month=None, day=None, hour=None):
    """Provides type and value checking for date and time arguments

    This function provides argument type and value checking for the functions
    `measured_pwv` and `modeled_pwv`.

    Args:
        year  (int): An integer value less than or equal to the current year
        month (int): An integer value between 1 and 12 (inclusive)
        day   (int): An integer value between 1 and 31 (inclusive)
        hour  (int): An integer value between 0 and 23 (inclusive)
    """

    if year is not None and year > datetime.now().year:
        raise ValueError("Provided year is larger than current year")

    arg_constraints = [('month', month, (1, 12)),
                       ('day', day, (1, 31)),
                       ('hour', hour, (0, 23))]

    for arg, value, bounds in arg_constraints:
        if value is not None and not (bounds[0] <= value <= bounds[1]):
            raise ValueError('Invalid value for {0}: {1}'.format(arg, value))


def _search_data_table(data_tab, **kwargs):
    """Search an astropy table of dates

    Given an astropy table with column 'date', return all entries in the table
    for which there is an object in that column with attributes matching the
    given kwargs.

    Credit for this function belongs to Alexander Afanasyev
    https://codereview.stackexchange.com/questions/165811

    Args:
        data_tab (Table): An astropy table to search
        **kwargs      (): The parameters to search data_tab for

    Returns:
        Entries from data_tab that match search parameters
    """

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
        path  (str): The path of the file to read
        year  (int): An integer value between 2010 and the current year
        month (int): An integer value between 1 and 12 (inclusive)
        day   (int): An integer value between 1 and 31 (inclusive)
        hour  (int): An integer value between 0 and 23 (inclusive)

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

        data = _search_data_table(
            data, year=year, month=month, day=day, hour=hour
        )

    for colname in data.colnames:
        if colname != 'date':
            data[colname].unit = 'mm'

    return data


def measured_pwv(year=None, month=None, day=None, hour=None):
    # type: (int, int, int, int) -> Table
    """Return an astropy table of PWV measurements taken by SuomiNet

    Columns are named using the SuomiNet IDs for different GPS receivers. PWV
    measurements for each receiver are recorded in millimeters. Results can be
    optionally refined by year, month, day, and hour.

    Args:
        year  (int): The year of the desired PWV data
        month (int): The month of the desired PWV data
        day   (int): The day of the desired PWV data
        hour  (int): The hour of the desired PWV data in 24-hour format

    Returns:
        An astropy table of measured PWV values in mm
    """

    # Specify the order of returned columns
    col_order = ['date', settings.primary_rec, settings.primary_rec + '_err']
    for receiver in settings.supplement_rec:
        col_order.append(receiver)
        col_order.append(receiver + '_err')

    data = _get_pwv_data_table(
        settings._pwv_measured_path, year, month, day, hour
    )

    return data[col_order]


def modeled_pwv(year=None, month=None, day=None, hour=None):
    # type: (int, int, int, int) -> Table
    """Return a table of the modeled PWV at the current site being modeled

    Return a model for the precipitable water vapor level at the current site
    as an astropy table. PWV measurements are reported in units of millimeters.
    Results can be optionally refined by year, month, day, and hour.

    Args:
        year  (int): The year of the desired PWV data
        month (int): The month of the desired PWV data
        day   (int): The day of the desired PWV data
        hour  (int): The hour of the desired PWV data in 24-hour format

    Returns:
        An astropy table of modeled PWV values in mm
    """

    return _get_pwv_data_table(settings._pwv_modeled_path,
                               year, month, day, hour)


def _calc_transmission(atm_model, pwv, bins=None, ignore_lim=False):
    """Calculate the PWV transmission from an atmospheric model

    atm_model should be a table with columns for wavelength ('wavelength') and
    conversion factor from PWV to cross section ('1/mm').

    Args:
        atm_model  (Table): Atmospheric model
        pwv        (float): A PWV concentration in mm
        bins (int or list): Integer number of bins or sequence of bin edges
        ignore_lim  (bool): Whether to ignore errors for negative PWV values

    Returns:
        A table with wavelengths, transmission, and optional transmission error
    """

    if not ignore_lim and pwv < 0:
        raise ValueError('PWV concentration cannot be negative')

    transmission = np.exp(- pwv * atm_model['1/mm'])

    if bins is not None:
        dx = atm_model['wavelength'][1] - atm_model['wavelength'][0]
        statistic_func = lambda y: np.trapz(y, dx=dx) / ((len(y) - 1) * dx)
        statistic, bin_edges, _ = binned_statistic(
            atm_model['wavelength'],
            transmission,
            statistic_func,
            bins
        )

        out_table = Table([bin_edges[:-1], statistic],
                          names=['wavelength', 'transmission'])

    else:
        out_table = Table([atm_model['wavelength'], transmission],
                          names=['wavelength', 'transmission'])

    out_table['wavelength'].unit = 'angstrom'
    return out_table


def trans_for_pwv(pwv, pwv_err=None, bins=None):
    # type: (float, float, Union[int, float, list]) -> Table
    """Return the atmospheric transmission due a given PWV concentration in mm

    For a given precipitable water vapor concentration, return the modeled
    atmospheric transmission function. The transmission function can optionally
    be binned by specifying the `bins` argument.

    Args:
        pwv        (float): A PWV concentration in mm
        pwv_err    (float): The error in pwv
        bins (int or list): Integer number of bins or sequence of bin edges

    Returns:
        The modeled transmission function as an astropy table
    """

    atm_model = Table.read(settings._atm_model_path)
    transmission = _calc_transmission(atm_model=atm_model, pwv=pwv, bins=bins)

    if pwv_err is not None:
        trans_plus_pwv_err = _calc_transmission(atm_model,
                                                pwv + pwv_err,
                                                bins,
                                                ignore_lim=True)

        trans_minus_pwv_err = _calc_transmission(atm_model,
                                                 pwv - pwv_err,
                                                 bins,
                                                 ignore_lim=True)

        transmission_err = np.subtract(trans_plus_pwv_err['transmission'],
                                       trans_minus_pwv_err['transmission'])

        transmission['transmission_err'] = np.abs(transmission_err)

    return transmission


def _raise_transmission_args(date, airmass):
    """Raise exception if arguments have wrong type or value

    Args:
        date    (datetime): A datetime value
        airmass    (float): An airmass value
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


def _trans_for_date(date, airmass, bins=None, test_model=None):
    """Return a model for the atmospheric transmission function due to PWV

    Args:
        date    (datetime): The datetime of the desired model
        airmass    (float): The airmass of the desired model
        bins (int or list): Integer number of bins or sequence of bin edges
        test_model (Table): A mock PWV model used by the test suite

    Returns:
        The modeled transmission function as an astropy table
    """

    pwv, pwv_err = _pwv_date(date, airmass, test_model)
    return trans_for_pwv(pwv, pwv_err, bins)


def trans_for_date(date, airmass, bins=None):
    # type: (datetime, float) -> Table
    """Return a model for the atmospheric transmission function due to PWV

    For a given datetime and airmass, return a model for the atmospheric
    transmission function due to precipitable water vapor at the current site
    being modeled. The transmission function can optionally be binned by
    specifying the `bins` argument.

    Args:
        date    (datetime): The datetime of the desired model
        airmass    (float): The airmass of the desired model
        bins (int or list): Integer number of bins or sequence of bin edges

    Returns:
        The modeled transmission function as an astropy table
    """

    return _trans_for_date(date, airmass, bins)


def get_all_receiver_data(receiver_id, apply_cuts=True):
    """Returns a table of all local SuomiNet data for a given receiver id

    Data is returned as an astropy table with columns 'date', 'PWV',
    'PWV_err', 'ZenithDelay', 'SrfcPress', 'SrfcTemp', and 'SrfcRH'.

    Args:
        receiver_id (str): A SuomiNet receiver id code (eg. KITT)
        apply_cuts (bool): Whether to apply data cuts from the package settings

    Returns:
        An astropy table with SuomiNet data for the given site
    """

    if receiver_id not in settings.receivers:
        err_msg = 'Receiver is not part of currently modeled site: {}'
        raise ValueError(err_msg.format(receiver_id))

    out_table = None
    for year in settings._downloaded_years:
        path_pattern = os.path.join(settings._suomi_dir, '{}*_{}.plt')
        path_pattern = path_pattern.format(receiver_id, year)

        # Sorting ensures that daily data releases take precedent over
        # hourly data releases. We are not concerned here with the global
        # data releases, since they do not have two published data sets
        path_list = sorted(glob(path_pattern))
        table_list = [_read_file(path, apply_cuts, False) for path in path_list]

        if table_list and any(table_list):
            data_for_year = unique(
                vstack(table_list),
                keep='first',
                keys=['date']
            )

            if out_table is None:
                out_table = data_for_year

            else:
                out_table = vstack([out_table, data_for_year])

    out_table.rename_column(receiver_id, 'PWV')
    out_table.rename_column(receiver_id + '_err', 'PWV_err')
    return out_table
