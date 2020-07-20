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
import pandas as pd
from scipy.odr import ODR, RealData, polynomial

from .file_parsing import load_rec_directory
from .types import NumpyReturn, NumpyArgument


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

    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", message='Empty data detected for ODR instance.')
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


def _search_data_table(
        data: pd.DataFrame, year: int = None, month: int = None, day=None,
        hour=None, colname: str = 'date') -> pd.DataFrame:
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
    datetime(year if year else datetime.now().year, month, day, hour)
    if any((year, month, day, hour)):
        raise NotImplementedError

    return data


class GPSReceiver:
    """Represents data taken by a SuomiNet GPS receiver"""

    def __init__(self, primary: str, secondaries: Tuple[str] = None,
                 data_cuts: dict = None):
        """Provides data access to weather and PWV data for a GPS receiver

        Args:
            primary: SuomiNet Id of the receiver to access
            secondaries: Secondary receivers used to supplement periods with
                missing primary data
            data_cuts: Only include data in the given ranges
        """

        self._primary = primary
        self._secondaries = tuple(secondaries) if secondaries else tuple()
        self.data_cuts = data_cuts

        self._data = {}
        self._pwv_model = None

    @property
    def primary(self) -> str:
        """The primary GPS receiver to retrieve PWV data for"""

        return self._primary

    @primary.setter
    def primary(self, value: str):
        """Change the instance's primary receiver and clear cached data"""

        # No action necessary if new value == old value
        if value == self._primary:
            return

        self._data.pop(self._primary)  # Delete data for old primary receiver
        self._primary = value
        self._pwv_model = None

    @property
    def secondaries(self) -> Tuple[str]:
        """Secondary GPS receivers used to model the PWV concentration at
         the primary GPS location when primary data is not available.
         """

        return self._secondaries

    @secondaries.setter
    def secondaries(self, value: Tuple[str]):
        """Change the instance's secondary receivers and clear cached data"""

        # No action necessary if new value == old value
        if value == self._secondaries:
            return

        # Delete data for old secondary receivers
        for key in self._secondaries:
            self._data.pop(key)

        self._secondaries = value
        self._pwv_model = None

    def _load_with_data_cuts(self, receiver_id: str) -> pd.DataFrame:
        """Load data for a given GPS receiver into memory

        Args:
            receiver_id: Id of the SuomiNet GPS receiver to load data for

        Returns:
            A Pandas DataFrame
        """

        # Use cached data if available to avoid slow I/O operations
        if receiver_id not in self._data:
            self._data[receiver_id] = load_rec_directory(receiver_id)

        # Applying data cuts every time the function is called means we
        # don't have to write a setter for self.data_cuts
        data = self._data[receiver_id]
        for param_name, cut_list in self.data_cuts.get(receiver_id, {}).items():
            for start, end in cut_list:
                data = data[(start <= data[param_name]) & (data[param_name] <= end)]

        return data.copy()

    def weather_data(self, year: int = None, month: int = None, day=None, hour=None) -> pd.DataFrame:
        """Returns a table of all weather data for the primary receiver

        Data is returned as an pandas DataFrame indexed by the SuomiNet Id
        of each GPS receiver. Results can be optionally refined by year,
        month, day, and hour.

        Args:
            year: The year of the desired PWV data
            month: The month of the desired PWV data
            day: The day of the desired PWV data
            hour: The hour of the desired PWV data in 24-hour format

        Returns:
            A pandas DataFrame
        """

        primary_data = self._load_with_data_cuts(self.primary)
        return _search_data_table(primary_data, year, month, day, hour)

    def modeled_pwv(self, year: int = None, month: int = None, day=None, hour=None) -> pd.DataFrame:
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
            A pandas dataframe of modeled PWV values in mm
        """

        # Todo: how to handle changing data-cuts and the PWV model?
        raise NotImplementedError

    def interp_pwv_date(self, date: NumpyArgument) -> NumpyReturn:
        """Evaluate the PWV model for a given datetime

        Args:
            date: UTC datetime object or timestamp

        Returns:
            Line of sight PWV concentration at the given datetime
        """

        raise NotImplementedError
