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

      >>> pwv_atm.trans_for_date(date=obsv_date,airmass=1.2,format=)


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
from typing import List, Tuple, Union

import numpy as np
from astropy.table import Table, unique, vstack
from astropy.time import Time
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


def _warn_available_data(
        test_dates: Union[float, np.array], known_dates: np.array):
    """Check if a date falls within the range of data in an astropy table

    Args:
        test_dates: A timezone aware datetime
        known_dates: An astropy table containing column 'date'
    """

    test_dates = np.atleast_1d(test_dates)  # In case passed a float
    if not len(known_dates):
        err_msg = 'No PWV data for primary receiver available on local machine.'
        raise RuntimeError(err_msg)

    # Check date falls within the range of available PWV data
    min_known_date, max_known_date = min(known_dates), max(known_dates)
    dates_too_early = test_dates[test_dates < min_known_date]
    if len(dates_too_early):
        min_date = datetime.utcfromtimestamp(min_known_date)
        raise ValueError(
            f'No PWV data found for dates before {min_date} on local machine'
        )

    dates_too_late = test_dates[test_dates > max_known_date]
    if len(dates_too_late):
        max_date = datetime.utcfromtimestamp(max_known_date)
        raise ValueError(
            f'No PWV data found for dates after {max_date} on local machine'
        )

    differences = (test_dates.reshape(1, -1) - known_dates.reshape(-1, 1))
    indices = np.abs(differences).argmin(axis=0)
    residual = np.diagonal(differences[indices,])

    one_day_in_seconds = 24 * 60 * 60
    out_of_interp_range = test_dates[residual > one_day_in_seconds]
    if len(out_of_interp_range):
        raise ValueError(
            f'Specified datetimes falls within interval of missing SuomiNet' 
            f' data larger than 1 day: {out_of_interp_range}.'
        )


def _pwv_date(
        date: Union[float, np.array, datetime],
        airmass: float = 1,
        format: str = None,
        test_model: Table = None) \
        -> Tuple[Union[float, np.array], Union[float, np.array]]:
    """Returns the modeled PWV column density at the current site

    Interpolate from the modeled PWV column density at at the current site
    being modeled and return the PWV column density for a given datetime and
    airmass.

    Args:
        date: The date of the desired PWV column density
        airmass: The airmass along line of sight
        format: An astropy compatible time format
        test_model: A mock PWV model used by the test suite

    Returns:
        The modeled PWV column density at the current site
        The error in modeled PWV column density
    """

    if test_model is None:
        pwv_model = Table.read(settings._pwv_modeled_path)

    else:
        pwv_model = test_model

    time_stamp = Time(date, format=format).to_value('unix')
    _warn_available_data(time_stamp, pwv_model['date'])

    pwv = np.interp(time_stamp, pwv_model['date'], pwv_model['pwv'])
    pwv_err = np.interp(time_stamp, pwv_model['date'], pwv_model['pwv_err'])

    # Determine the PWV level along line of sight as outlined in
    # Horne et al. 2012
    pwv_los = pwv * (airmass ** .6)
    pwv_err_los = pwv_err * (airmass ** .6)
    return pwv_los, pwv_err_los


def pwv_date(
        date: Union[float, np.array, datetime],
        airmass: float = 1,
        format: str = None) \
        -> Tuple[Union[float, np.array], Union[float, np.array]]:
    """Returns the modeled PWV column density at the current site

    Interpolate from the modeled PWV column density at the current site being
    modeled and return the PWV column density for a given datetime and airmass.

    Args:
        date: The date of the desired PWV column density
        airmass: The airmass along line of sight
        format: An astropy compatible time format (e.g., unix, mjd, datetime)

    Returns:
        The modeled PWV column density at the current site
        The error in modeled PWV column density
    """

    return _pwv_date(date, airmass, format)


def downloaded_years() -> List[int]:
    """Return a list of years for which SuomiNet data has been downloaded

    Return a list of years for which SuomiNet data has been downloaded to the
    local machine. Note that this list includes years for which any amount
    of data has been downloaded. It does not indicate if additional data has
    been released by SuomiNet for a given year that is not locally available.

    Returns:
        A list of years with locally available SuomiNet data
    """

    return sorted(settings._downloaded_years)


def _check_date_time_args(
        year: int = None,
        month: int = None,
        day: int = None,
        hour: int = None):
    """Provides type and value checking for date and time arguments

    This function provides argument type and value checking for the functions
    `measured_pwv` and `modeled_pwv`.

    Args:
        year: An integer value less than or equal to the current year
        month: An integer value between 1 and 12 (inclusive)
        day: An integer value between 1 and 31 (inclusive)
        hour: An integer value between 0 and 23 (inclusive)
    """

    if year is not None and year > datetime.now().year:
        raise ValueError("Provided year is larger than current year")

    arg_constraints = [('month', month, (1, 12)),
                       ('day', day, (1, 31)),
                       ('hour', hour, (0, 23))]

    for arg, value, bounds in arg_constraints:
        if value is not None and not (bounds[0] <= value <= bounds[1]):
            raise ValueError('Invalid value for {0}: {1}'.format(arg, value))


def _search_data_table(data_tab: Table, **kwargs):
    """Search an astropy table of dates

    Given an astropy table with column 'date', return all entries in the table
    for which there is an object in that column with attributes matching the
    given kwargs.

    Credit for this function belongs to Alexander Afanasyev
    https://codereview.stackexchange.com/questions/165811

    Args:
        data_tab: An astropy table to search
        **kwargs: The parameters to search data_tab for

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


def _get_pwv_data_table(path: str, year: int, month: int, day: int, hour: int):
    """Reads a PWV data table from file and formats the table and data

    Adds units and converts 'date' column from timestamps to datetimes.

    Args:
        path: The path of the file to read
        year: An integer value between 2010 and the current year
        month: An integer value between 1 and 12 (inclusive)
        day: An integer value between 1 and 31 (inclusive)
        hour: An integer value between 0 and 23 (inclusive)

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


def measured_pwv(year: int = None, month: int = None, day: int = None,
                 hour: int = None) -> Table:
    """Return an astropy table of PWV measurements taken by SuomiNet

    Columns are named using the SuomiNet IDs for different GPS receivers. PWV
    measurements for each receiver are recorded in millimeters. Results can be
    optionally refined by year, month, day, and hour.

    Args:
        year: The year of the desired PWV data
        month: The month of the desired PWV data
        day: The day of the desired PWV data
        hour: The hour of the desired PWV data in 24-hour format

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


def modeled_pwv(year: int = None, month: int = None, day: int = None,
                hour: int = None) -> Table:
    """Return a table of the modeled PWV at the current site being modeled

    Return a model for the precipitable water vapor level at the current site
    as an astropy table. PWV measurements are reported in units of millimeters.
    Results can be optionally refined by year, month, day, and hour.

    Args:
        year: The year of the desired PWV data
        month: The month of the desired PWV data
        day: The day of the desired PWV data
        hour: The hour of the desired PWV data in 24-hour format

    Returns:
        An astropy table of modeled PWV values in mm
    """

    return _get_pwv_data_table(settings._pwv_modeled_path,
                               year, month, day, hour)


def _calc_transmission(
        atm_model: Table,
        pwv: float,
        bins: Union[int, list] = None,
        ignore_lim: bool = False) -> Table:
    """Calculate the PWV transmission from an atmospheric model

    atm_model should be a table with columns for wavelength ('wavelength') and
    conversion factor from PWV to cross section ('1/mm').

    Args:
        atm_model: Atmospheric model
        pwv: A PWV concentration in mm
        bins: Integer number of bins or sequence of bin edges
        ignore_lim: Whether to ignore errors for negative PWV values

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


def trans_for_pwv(
        pwv: float,
        pwv_err: float = None,
        bins: Union[int, list] = None) -> Table:
    """Return the atmospheric transmission due a given PWV concentration in mm

    For a given precipitable water vapor concentration, return the modeled
    atmospheric transmission function. The transmission function can optionally
    be binned by specifying the `bins` argument.

    Args:
        pwv: A PWV concentration in mm
        pwv_err: The error in pwv
        bins: Integer number of bins or sequence of bin edges

    Returns:
        The modeled transmission function as an astropy table
    """

    atm_model = Table.read(settings._atm_model_path)
    transmission = _calc_transmission(atm_model=atm_model, pwv=pwv, bins=bins)

    if pwv_err is not None:
        trans_plus_pwv_err = _calc_transmission(
            atm_model, pwv + pwv_err, bins, ignore_lim=True)

        trans_minus_pwv_err = _calc_transmission(
            atm_model, pwv - pwv_err, bins, ignore_lim=True)

        transmission_err = np.subtract(
            trans_plus_pwv_err['transmission'],
            trans_minus_pwv_err['transmission'])

        transmission['transmission_err'] = np.abs(transmission_err)

    return transmission


def _raise_transmission_args(date: datetime, airmass: float):
    """Raise exception if arguments have wrong type or value

    Args:
        date: A datetime value
        airmass: An airmass value
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


def _trans_for_date(
        date: Union[float, np.array, datetime],
        airmass: float = 1,
        format: str = None,
        bins: Union[int, list] = None,
        test_model: Table = None) -> Table:
    """Return a model for the atmospheric transmission function due to PWV

    Args:
        date: The datetime of the desired model
        airmass: The airmass of the desired model
        format: An astropy compatible time format
        bins: Integer number of bins or sequence of bin edges
        test_model: A mock PWV model used by the test suite

    Returns:
        The modeled transmission function as an astropy table
    """

    pwv, pwv_err = _pwv_date(date, airmass=airmass, format=format,
                             test_model=test_model)

    return trans_for_pwv(pwv, pwv_err, bins)


def trans_for_date(
        date: Union[float, np.array, datetime],
        airmass: float = 1, 
        format: str = None,
        bins: Union[int, list] = None) -> Table:
    """Return a model for the atmospheric transmission function due to PWV

    For a given datetime and airmass, return a model for the atmospheric
    transmission function due to precipitable water vapor at the current site
    being modeled. The transmission function can optionally be binned by
    specifying the `bins` argument.

    Args:
        date: The date of the desired model in the given format
        airmass: The airmass of the desired model
        format: An astropy compatible time format (e.g., unix, mjd, datetime)
        bins: Integer number of bins or sequence of bin edges

    Returns:
        The modeled transmission function as an astropy table
    """

    return _trans_for_date(date, airmass, format, bins)


def get_all_receiver_data(receiver_id: str, apply_cuts: bool = True):
    """Returns a table of all local SuomiNet data for a given receiver id

    Data is returned as an astropy table with columns 'date', 'PWV',
    'PWV_err', 'ZenithDelay', 'SrfcPress', 'SrfcTemp', and 'SrfcRH'.

    Args:
        receiver_id: A SuomiNet receiver id code (eg. KITT)
        apply_cuts: Whether to apply data cuts from the package settings

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
        table_list = [_read_file(path, apply_cuts, False) for path in
                      path_list]

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
