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
from copy import deepcopy
from datetime import datetime
from typing import Tuple

import numpy as np
import pandas as pd
from scipy.odr import ODR, RealData, polynomial

from .file_parsing import load_rec_directory
from .types import DataCuts, NumpyArgument, NumpyReturn


def _linear_regression(x: np.array, y: np.array, sx: np.array, sy: np.array) -> Tuple[pd.Series, pd.Series]:
    """Optimize and apply a linear regression using masked arrays

    Generates a linear fit f using orthogonal distance regression and returns
    the applied model f(x). If y is completely masked, return y and sy.

    Args:
        x: The independent variable of the regression
        y: The dependent variable of the regression
        sx: Standard deviations of x
        sy: Standard deviations of y

    Returns:
        The applied linear regression on x
        The uncertainty in the applied linear regression
    """

    data = RealData(x=x, y=y, sx=sx, sy=sy)
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
    std = np.std(y - m * x - b)

    applied_fit.name = 'fitted_pwv'
    errors = pd.Series(std, index=applied_fit.index, name='fitted_err')
    return applied_fit, errors


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
            colname: Use a column in ``data`` instead of the index
        """

    # Raise exception for bad datetime args
    datetime(
        year if year else 1,
        month if month else 1,
        day if day else 1,
        hour if hour else 1)

    # Todo: search DataFrame index by default
    if any((year, month, day, hour)):
        raise NotImplementedError

    return data.copy()


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
        self._data_cuts = data_cuts if data_cuts else dict()

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

    @property
    def data_cuts(self) -> DataCuts:
        """Dictionary of data cuts on returned data for each GPS receiver"""

        return deepcopy(self._data_cuts)

    @data_cuts.setter
    def data_cuts(self, value: DataCuts):
        """Change the instance's data cuts and clear the cached PWV Model"""

        self._data_cuts = value
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
        for param_name, cut_list in self._data_cuts.get(receiver_id, {}).items():
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

    def _calc_avg_pwv_model(self) -> pd.DataFrame:
        """Determines a PWV model using each off site receiver and averages them

        Returns:
            A DataFrame with modeled PWV values and the associated errors over time
        """

        primary_data = self._load_with_data_cuts(self._primary)

        fitted_pwv = pd.DataFrame()
        fitted_error = pd.DataFrame()
        for secondary_rec in self._secondaries:

            secondary_data = self._load_with_data_cuts(secondary_rec)
            joined_data = primary_data \
                .join(secondary_data, lsuffix='primary', rsuffix='secondary') \
                .dropna(subset=['PWVprimary', 'PWVsecondary'])

            try:
                _fitted_pwv, _fitted_error = _linear_regression(
                    joined_data['PWVsecondary'],
                    joined_data['PWVErrsecondary'],
                    joined_data['PWVprimary'],
                    joined_data['PWVErrprimary'])

            except RuntimeError:
                continue

            fitted_pwv[secondary_rec] = _fitted_pwv
            fitted_error[secondary_rec] = _fitted_error

        # Average PWV models from different sites
        out_data = pd.DataFrame({
            'PWV': fitted_pwv.mean(axis=1),
            'PWVErr': np.sqrt((fitted_error ** 2).sum(axis=1)) / len(fitted_error)
        })

        if out_data.empty:
            warnings.warn('No overlapping PWV data between primary and secondary '
                          'receivers. Cannot model PWV for times when primary '
                          'receiver is offline')

        # Todo: This doesn't include data that is in primary_data but not out_data
        out_data.update(primary_data[['PWV', 'PWVErr']])
        return out_data.dropna().sort_index()

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
            A pandas DataFrame of modeled PWV values in mm
        """

        if self._pwv_model is None:
            self._pwv_model = self._calc_avg_pwv_model()

        return _search_data_table(self._pwv_model, year, month, day, hour)

    # Todo: Add limit on number of successive values interpolate
    def interp_pwv_date(self, date: NumpyArgument, method: str = 'linear', order=None) -> NumpyReturn:
        """Evaluate the PWV model for a given datetime

        Args:
            date: UTC datetime object or timestamp
            method: interpolation technique to use. Supported methods include
                'linear' 'nearest', 'zero', 'slinear', 'quadratic', 'cubic',
                'spline', 'barycentric', 'polynomial'
            order: Order of interpolation if using ‘polynomial’ or ‘spline’

        Returns:
            Line of sight PWV concentration at the given datetime
        """

        if method == 'linear':
            method = 'index'

        valid_methods = (
            'index', 'nearest', 'zero', 'slinear', 'quadratic', 'cubic',
            'spline', 'barycentric', 'polynomial')

        if method not in valid_methods:
            raise ValueError(f'Invalid interpolation method: {method}')

        raise NotImplementedError

        # pwv_model = self.modeled_pwv().copy()
        # pwv_model.loc[date] = np.nan
        # interp_data = pwv_model.interpolate(
        #     method=method, limit_direction='both', limit_area='inside', order=order
        # ).loc[date]

        # if interp_data.isna().any():
        #     warnings.warn('Some values were outside the permitted interpolation range')

        # return interp_data
