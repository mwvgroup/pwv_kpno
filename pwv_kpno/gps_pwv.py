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

"""The ``gps_pwv`` module is responsible for serving SuomiNet GPS data at a
given location. This includes location specific weather data (e.g., temperature
and pressure measurements) and PWV concentrations (both measured and modeled).
"""

import warnings
from datetime import datetime
from typing import Tuple

import numpy as np
from astropy.table import Table
from scipy.odr import ODR, RealData, polynomial

from .types import NumpyReturn, NumpyArgument

warnings.filterwarnings("ignore", message='Empty data detected for ODR instance.')


def _linear_regression(x: np.array, y: np.array, sx: np.array, sy: np.array) -> Tuple[np.array, np.array]:
    """Optimize and apply a linear regression using masked arrays

    Generates a linear fit f using orthogonal distance regression and returns
    the applied model f(x). If y is completely masked, return y and sy.

    Args:
        x: The independent variable of the regression
        y: The dependent variable of the regression
        sx: Standard deviations of x
        sy: Standard deviations of y

    Returns:
        The applied linear regression on x as a masked array
        The uncertainty in the applied linear regression as a masked array
    """

    x = np.ma.array(x)  # This type cast will propagate into returns
    y = np.ma.array(y)  # It also ensures that x, y have a .mask attribute

    if y.mask.all():
        return y, sy

    # Fit data with orthogonal distance regression (ODR)
    indices = ~np.logical_or(x.mask, y.mask)
    data = RealData(x=x[indices], y=y[indices], sx=sx[indices], sy=sy[indices])
    odr = ODR(data, polynomial(1), beta0=[0., 1.])
    fit_results = odr.run()

    fit_fail = 'Numerical error detected' in fit_results.stopreason
    if fit_fail:
        raise RuntimeError(fit_results.stopreason)

    # Apply the linear regression
    b, m = fit_results.beta
    applied_fit = m * x + b
    applied_fit.mask = np.logical_or(x.mask, applied_fit <= 0)

    std = np.ma.std(y[indices] - m * x[indices] - b)
    error = np.ma.zeros(applied_fit.shape) + std
    error.mask = applied_fit.mask

    return applied_fit, error


def search_data_table(
        data: Table, year: int = None, month: int = None, day=None, hour=None,
        colname: str = 'date') -> Table:
    """Return a subset of a table with dates corresponding to a given timespan

    Args:
        data: Astropy table to return a subset of
        year: Only return data within the given year
        month: Only return data within the given month
        day: Only return data within the given day
        hour: Only return data within the given hour
        colname: Name of the column in ``data`` having UTC timestamps
    """

    # Raise exception for bad datetime args
    datetime(year, month, day, hour)
    raise NotImplementedError


class GPSReceiver:
    """Represents data taken by a SuomiNet GPS receiver"""

    # Used to signal that new data has been downloaded and PWV values need to
    # be re-loaded into into memory by class instances
    _reload_from_download = [False]

    def __init__(self, primary: str, secondaries: Tuple[str] = None, data_cuts: dict = None):
        """Provides data access to weather and PWV data for a GPS receiver

        Args:
            primary: SuomiNet Id of the receiver to access
            secondaries: Tuple of secondary receivers to use for supplementing
                time ranges with missing data
            data_cuts: Ignore data in the given ranges
        """

        self._primary = primary
        self._secondaries = tuple(secondaries)
        self.data_cuts = data_cuts

    @property
    def primary(self) -> str:
        return self._primary

    @primary.setter
    def primary(self, value):
        raise NotImplementedError

    @property
    def secondaries(self) -> Tuple[str]:
        return self._secondaries

    @secondaries.setter
    def secondaries(self, value):
        raise NotImplementedError

    def modeled_pwv(self, year: int = None, month: int = None, day=None, hour=None) -> Table:
        """Return a table of the modeled PWV at the primary GPS site

        Return the modeled precipitable water vapor level at the primary
        GPS site. PWV measurements are reported in units of millimeters.
        Results can be optionally refined by year, month, day, and hour.

        Args:
            year: The year of the desired PWV data
            month: The month of the desired PWV data
            day: The day of the desired PWV data
            hour: The hour of the desired PWV data in 24-hour format

        Returns:
            An astropy table of modeled PWV values in mm
        """

        raise NotImplementedError

    def measured_pwv(self, year: int = None, month: int = None, day=None, hour=None) -> Table:
        """Return an astropy table of PWV measurements taken by SuomiNet

        Values are returned for all primary and secondary receivers.
        Columns are named using the SuomiNet IDs for different GPS receivers.
        PWV measurements for each receiver are recorded in millimeters.
        Results can be optionally refined by year, month, day, and hour.

        Args:
            year: The year of the desired PWV data
            month: The month of the desired PWV data
            day: The day of the desired PWV data
            hour: The hour of the desired PWV data in 24-hour format

        Returns:
            An astropy table of measured PWV values in mm
        """

        raise NotImplementedError

    def weather_data(self, year: int = None, month: int = None, day=None, hour=None) -> Table:
        """Returns a table of all weather_Data data for the primary receiver

        Data is returned as an astropy table with columns 'date', 'PWV',
        'PWV_err', 'ZenithDelay', 'SrfcPress', 'SrfcTemp', and 'SrfcRH'.
        Results can be optionally refined by year, month, day, and hour.

        Args:
            year: The year of the desired PWV data
            month: The month of the desired PWV data
            day: The day of the desired PWV data
            hour: The hour of the desired PWV data in 24-hour format

        Returns:
            An astropy Table
        """

        raise NotImplementedError

    def interp_pwv_date(self, date: NumpyArgument) -> NumpyReturn:
        """Evaluate the PWV model for a given datetime

        Args:
            date: UTC datetime object or timestamp

        Returns:
            Line of sight PWV concentration at the given datetime
        """

        raise NotImplementedError
