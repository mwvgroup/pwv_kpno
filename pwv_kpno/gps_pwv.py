# !/usr/bin/env python3
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
from typing import Set
from typing import Tuple

import numpy as np
import pandas as pd
from scipy.odr import ODR, Output, RealData, polynomial

from .file_parsing import load_rec_directory
from .types import DataCuts, DataCuts1D, NumpyArgument, NumpyReturn


def apply_data_cuts(data: pd.DataFrame, cuts: DataCuts1D):
    """Apply a dictionary of data cuts to a DataFrame

    Only return data that is within the specified ranges

    Args:
        data: Data to apply cuts on
        cuts: Dict with a list of tuples (cut start, cut end)

    Returns:
        A subset of the passed DataFrame
    """

    for param_name, cut_list in cuts:
        for start, end in cut_list:
            data = data[(start <= data[param_name]) & (data[param_name] <= end)]

    return data


def search_data_table(
        data: pd.DataFrame, year: int = None, month: int = None, day=None,
        hour=None, colname: str = None) -> pd.DataFrame:
    """Return a subset of a table with dates corresponding to a given timespan

    Args:
        data: Pandas DataFrame to return a subset of
        year: Only return data within the given year
        month: Only return data within the given month
        day: Only return data within the given day
        hour: Only return data within the given hour
        colname: Use a column in ``data`` instead of the index
    """

    # Get just the datetime args that aren't None
    test_attr = dict(year=year, month=month, day=day, hour=hour)
    test_attr = {k: v for k, v in test_attr.items() if v}
    if not test_attr:
        return data

    # Raise exception for bad datetime args
    datetime(
        test_attr.get('year', 1),
        test_attr.get('month', 1),
        test_attr.get('day', 1),
        test_attr.get('hour', 1)
    )

    search_col = data[colname] if colname else data.index
    matches_kw = tuple(getattr(search_col.index, k) == v for k, v in test_attr.items())

    # If we are only searching against a single attr then use the booleans from
    # that attr to select from the array
    if len(matches_kw) == 1:
        return data[matches_kw[0]]

    # If checking multiple attr's, when need to logically combine them
    return data[np.logical_and(*matches_kw)]


class PWVData:
    """Loads GPS weather data and applies data cuts"""

    _cached_class_data = dict()  # To store cached data
    _ref_count = dict()  # To count references to cached data by instances

    def __init__(self, primary: str, secondaries: Set[str] = None, data_cuts: dict = None):
        """Provides data access to weather and PWV data

        Args:
            primary: SuomiNet Id of the receiver to access
            secondaries: Secondary receivers used to supplement periods with
                missing primary data
            data_cuts: Only include data in the given ranges
        """

        self.primary = primary.upper()
        self.secondaries = secondaries or set()
        self.data_cuts = data_cuts or dict()

    def _load_data_with_cuts(self, receiver_id: str) -> pd.DataFrame:
        """Load data for a given GPS receiver into memory

        Args:
            receiver_id: Id of the SuomiNet GPS receiver to load data for

        Returns:
            A Pandas DataFrame
        """

        receiver_data = load_rec_directory(receiver_id)
        receiver_cuts = self.data_cuts.get(receiver_id, {}).items()
        return apply_data_cuts(receiver_data, receiver_cuts)

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

        primary_data = self._load_data_with_cuts(self.primary)
        return search_data_table(primary_data, year, month, day, hour)


class PWVModeling(PWVData):
    """Handles the modeling of PWV for times when direct measurements are not
    available at the primary location.
    """

    # noinspection PyMissingConstructor
    def __init__(self, primary: str, secondaries: Set[str] = None, data_cuts: dict = None):
        """Handles getter / setter logic for class attributes

        Args:
            primary: SuomiNet Id of the receiver to access
            secondaries: Secondary receivers used to supplement periods with
                missing primary data
            data_cuts: Only include data in the given ranges
        """

        self._primary = primary
        self._secondaries = set(secondaries) if secondaries else set()
        self._data_cuts = data_cuts if data_cuts else dict()
        self._pwv_model = None

        if primary in secondaries:
            raise ValueError('Primary receiver cannot be listed as a secondary receiver')

    ###########################################################################
    # Getter / setters are used to reset the cached PWV Model
    ###########################################################################

    @property
    def primary(self) -> str:
        """The primary GPS receiver to retrieve PWV data for"""

        return self._primary

    @primary.setter
    def primary(self, value: str):
        """Change the instance's primary receiver and clear cached data"""

        # No action necessary if new value == old value
        if value.upper() == self._primary:
            return

        self._primary = value.upper()
        self._pwv_model = None

    @property
    def secondaries(self) -> Set[str]:
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

    ###########################################################################
    # PWV is modeled by separately fitting the primary PWV as a function of
    # the PWV measured by each secondary receiver and then averaging the result
    ###########################################################################

    @staticmethod
    def _linear_regression(x: np.array, y: np.array, sx: np.array, sy: np.array) -> Output:
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

        return fit_results

    def _fit_to_secondary(self, secondary_receiver: str) -> Tuple[pd.Series, pd.Series]:
        """Apply a linear fit to the primary PWV data as a function of the PWV
        at a secondary location

        Args:
            secondary_receiver: Receiver Id for the secondary location

        Returns:
            - The fitted PWV (mm)
            - Error values for the fitted PWV
        """

        # Get subset of primary / secondary data with datetimes that overlap
        primary_data = self._load_data_with_cuts(self._primary)
        secondary_data = self._load_data_with_cuts(secondary_receiver)
        joined_data = primary_data \
            .join(secondary_data, lsuffix='Primary', rsuffix='Secondary') \
            .dropna(subset=['PWVPrimary', 'PWVErrPrimary', 'PWVSecondary', 'PWVErrSecondary'])

        # Evaluate the fit
        fit_results = self._linear_regression(
            joined_data['PWVSecondary'],
            joined_data['PWVErrSecondary'],
            joined_data['PWVPrimary'],
            joined_data['PWVErrPrimary'])

        # Apply the linear regression
        b, m = fit_results.beta
        applied_fit = m * joined_data['PWVSecondary'] + b
        residuals = joined_data['PWVPrimary'] - applied_fit
        errors = residuals.std()

        applied_fit.name = 'fitted_pwv'
        errors.name = 'fitted_err'
        return applied_fit, errors

    def _calc_avg_pwv_model(self) -> pd.DataFrame:
        """Determines a PWV model using each off site receiver and averages them

        Returns:
            A DataFrame with modeled PWV values and the associated errors over time
        """

        fitted_pwv = pd.DataFrame()
        fitted_error = pd.DataFrame()
        for secondary_rec in self._secondaries:
            try:
                _fitted_pwv, _fitted_error = self._fit_to_secondary(secondary_rec)

            except RuntimeError:  # Failed ODR regression
                warnings.warn('Linear regression failed for {}'.format(secondary_rec))

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

        primary_data = self._load_data_with_cuts(self._primary)
        out_data.loc[primary_data.index] = primary_data
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

        return search_data_table(self._pwv_model, year, month, day, hour)


class GPSReceiver(PWVModeling):
    """Data access for measurements taken by SuomiNet GPS receivers"""

    def interp_pwv_date(self, date: NumpyArgument, interp_limit: float = None,
                        method: str = 'linear', order=None) -> NumpyReturn:
        """Evaluate the PWV model for a given datetime

        Args:
            date: UTC datetime object or timestamp
            interp_limit: Require measured values within the given time
                interval, otherwise result will be nan
                (Defined in units of 30 min).
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

        # Resample modeled values onto a uniform sampling of time values
        # Credit: https://stackoverflow.com/a/47148740
        pwv_model = self.modeled_pwv()
        old_index = pwv_model.index
        new_index = pd.date_range(old_index.min(), old_index.max(), freq='30min')
        uniform_model = pwv_model.reindex(old_index.union(new_index))

        # We loose some efficiency here because we have to interpolate more
        # values than necessary (because of the resampling). However, the
        # resampling allows us to enforce physically meaningful interpolation
        # limits. Fortunately, interpolation is relatively cheap.
        uniform_model.loc[date] = np.nan
        interp_data = uniform_model.interpolate(
            method=method, limit=interp_limit, limit_direction='both', limit_area='inside', order=order
        ).loc[date]

        if interp_data.isna().any():
            warnings.warn('Some values were outside the permitted interpolation range')

        return interp_data
