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
and pressure measurements) and PWV concentrations along the line of sight.

Module API
----------
"""

import warnings
from copy import deepcopy
from datetime import datetime
from typing import Set
from typing import Tuple

import numpy as np
import pandas as pd
from scipy.odr import ODR, Output, RealData, polynomial

from .downloads import DownloadManager
from .file_parsing import read_suomi_file
from .types import DataCuts, DataCuts1D, NumpyArgument, NumpyReturn


def apply_data_cuts(data: pd.DataFrame, cuts: DataCuts1D) -> pd.DataFrame:
    """Apply a dictionary of data cuts to a DataFrame

    Only return data that is within the specified value ranges

    Args:
        data: Data to apply cuts on
        cuts: Dict with a list of tuples (cut start, cut end)

    Returns:
        A subset of the passed DataFrame
    """

    for param_name, cut_list in cuts.items():
        for start, end in cut_list:
            data = data[(start <= data[param_name]) & (data[param_name] <= end)]

    return data


def linear_regression(x: np.array, y: np.array, sx: np.array, sy: np.array) -> Output:
    """Optimize and apply a linear regression using masked arrays

    Generates a linear fit f using orthogonal distance regression and returns
    the applied model f(x).

    Args:
        x: The independent variable of the regression
        y: The dependent variable of the regression
        sx: Standard deviations of x
        sy: Standard deviations of y

    Returns:
        A Scipy.odr Output object
    """

    data = RealData(x=x, y=y, sx=sx, sy=sy)
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore")
        odr = ODR(data, polynomial(1), beta0=[0., 1.])
        fit_results = odr.run()

    if 'Numerical error detected' in fit_results.stopreason:
        raise RuntimeError(fit_results.stopreason)

    return fit_results


def search_data_table(
        data: pd.DataFrame, year: int = None, month: int = None, day=None,
        hour=None) -> pd.DataFrame:
    """Return a subset of a table with dates corresponding to a given timespan

    Args:
        data: Pandas DataFrame to return a subset of
        year: Only return data within the given year
        month: Only return data within the given month
        day: Only return data within the given day
        hour: Only return data within the given hour
    """

    # Raise exception for bad datetime args
    # We use ``if`` here instead of ``or`` since some values may be zero
    datetime(
        1 if year is None else year,
        1 if month is None else month,
        1 if day is None else day,
        1 if hour is None else hour
    )

    if data.empty or not any((year, month, day, hour)):
        return data

    # Convert datetimes into strings and compare dates against the test string
    date_format = ''
    test_string = ''
    for formatter, kwarg in zip(('%Y', '%m', '%d', '%h'), (year, month, day, hour)):
        if kwarg:
            date_format += formatter
            test_string += str(kwarg).zfill(2)

    return data[data.index.strftime(date_format) == test_string]


def load_rec_data(receiver_id: str) -> pd.DataFrame:
    """Load all data for a given GPS receiver from a directory

    Data from daily data releases is prioritized over hourly data releases

    Args:
        receiver_id: Id of the SuomiNet GPS receiver to load data for

    Returns:
        A pandas DataFrame of SuomiNet weather data
    """

    directory = DownloadManager().data_dir

    # Data release types ordered in terms of priority
    # Prefer global data over daily data over hourly data
    data_types = ('gl', 'dy', 'hr')

    data = []  # Collector for DataFrames with data from each data type
    for dtype in data_types:
        global_files = list(directory.glob(f'{receiver_id}{dtype}_*.plt'))
        if global_files:
            data.append(pd.concat([read_suomi_file(f) for f in global_files]))

    if data:
        combined_data = pd.concat(data)
        return combined_data.loc[~combined_data.index.duplicated(keep='first')]

    warnings.warn('No local data found for {}'.format(receiver_id))

    return pd.DataFrame(columns=[
        'date', 'PWV, PWVErr',
        'ZenithDelay', 'SrfcPress', 'SrfcTemp', 'SrfcRH'
    ]).set_index('date')


class PWVModel:
    """Handles the modeling of PWV for times when direct measurements are not
    available at the primary location.
    """

    # noinspection PyMissingConstructor
    def __init__(self, primary: str, secondaries: Set[str] = None, data_cuts: DataCuts = None) -> None:
        """Handles getter / setter logic for class attributes

        Args:
            primary: SuomiNet Id of the receiver to access
            secondaries: Secondary receivers used to supplement periods with
                missing primary data
            data_cuts: Only include data in the given ranges
        """

        self._primary = primary.upper()
        self._data_cuts = data_cuts if data_cuts else dict()
        self._secondaries = set() if secondaries is None else set(s.upper() for s in secondaries)
        self._pwv_model = None  # Place holder for lazy loading

        if primary in self._secondaries:
            raise ValueError('Primary receiver cannot be listed as a secondary receiver')

    @property
    def primary(self) -> str:
        """The primary GPS receiver to retrieve PWV data for"""

        return self._primary

    @property
    def secondaries(self) -> Set[str]:
        """Secondary GPS receivers used to model the PWV concentration at
         the primary GPS location when primary data is not available.
         """

        return self._secondaries

    @property
    def data_cuts(self) -> DataCuts:
        """Dictionary of data cuts on returned data for each GPS receiver"""

        return deepcopy(self._data_cuts)

    ###########################################################################
    # PWV is modeled by separately fitting the primary PWV as a function of
    # the PWV measured by each secondary receiver and then averaging the result
    ###########################################################################

    def _load_data_with_cuts(self, receiver_id: str) -> pd.DataFrame:
        """Returns a table of all weather data for the primary receiver

        Data is returned as an pandas DataFrame indexed by the SuomiNet Id
        of each GPS receiver. Results can be optionally refined by year,
        month, day, and hour.

        Args:
            receiver_id: Id of the receiver to load data for

        Returns:
            A pandas DataFrame
        """

        receiver_data = load_rec_data(receiver_id)
        receiver_cuts = self.data_cuts.get(receiver_id, {})

        # noinspection PyTypeChecker
        return apply_data_cuts(receiver_data, receiver_cuts)

    def weather_data(self, year: int = None, month: int = None, day=None, hour=None) -> pd.DataFrame:
        """Return a table of weather data taken at the primary GPS receiver

        Args:
            year: The year of the desired PWV data
            month: The month of the desired PWV data
            day: The day of the desired PWV data
            hour: The hour of the desired PWV data in 24-hour format

        Returns:
            A pandas DataFrame of modeled PWV values in mm
        """

        return search_data_table(self._load_data_with_cuts(self.primary), year, month, day, hour)

    @staticmethod
    def _fit_to_secondary(primary_data: pd.DataFrame, secondary_data: pd.DataFrame) -> Tuple[pd.Series, pd.Series]:
        """Apply a linear fit to the primary PWV data as a function of the PWV
        at a secondary location

        Args:
            primary_data: SuomiNet data from the primary receiver
            secondary_data: SuomiNet data from the secondary receiver

        Returns:
            - The fitted PWV (mm)
            - Error values for the fitted PWV
        """

        # Get subset of primary / secondary data with datetimes that overlap
        joined_data = primary_data \
            .join(secondary_data, lsuffix='Primary', rsuffix='Secondary') \
            .dropna(subset=['PWVPrimary', 'PWVErrPrimary', 'PWVSecondary', 'PWVErrSecondary'])

        # Evaluate the fit
        b, m = linear_regression(
            joined_data['PWVSecondary'],
            joined_data['PWVPrimary'],
            joined_data['PWVErrSecondary'],
            joined_data['PWVErrPrimary']).beta

        # Apply the linear regression
        applied_fit = m * secondary_data.PWV + b
        residuals = joined_data['PWVPrimary'] - applied_fit
        errors = pd.Series(residuals.std(), name='fitted_err', index=applied_fit.index)

        return applied_fit, errors

    def _calc_avg_pwv_model(self) -> pd.DataFrame:
        """Determines a PWV model using each off site receiver and averages them

        Returns:
            A DataFrame with modeled PWV values and the associated errors over time
        """

        primary_data = self.weather_data()

        # Fit fit the primary receiver's PWV data as function of each secondary
        # receiver and accumulate the results
        fitted_pwv = pd.DataFrame()
        fitted_error = pd.DataFrame()
        for secondary_rec in self.secondaries:
            secondary_data = self._load_data_with_cuts(secondary_rec)

            try:
                _fitted_pwv, _fitted_error = self._fit_to_secondary(primary_data, secondary_data)

            except RuntimeError:  # Failed ODR regression
                warnings.warn('Linear regression failed for {}. Dropped from model'.format(secondary_rec))

            else:
                fitted_pwv[secondary_rec] = _fitted_pwv
                fitted_error[secondary_rec] = _fitted_error

        # Average PWV models from different sites
        # noinspection PyTypeChecker
        out_data = pd.DataFrame({
            'PWV': fitted_pwv.mean(axis=1),
            'PWVErr': np.sqrt((fitted_error ** 2).sum(axis=1)) / len(fitted_error)
        })

        if out_data.empty:
            warnings.warn('No overlapping PWV data between primary and secondary '
                          'receivers. Cannot model PWV for times when primary '
                          'receiver is offline')

        # Upsert data from the primary receiver
        out_data = pd.concat([out_data[~out_data.index.isin(primary_data.index)], primary_data[['PWV', 'PWVErr']]])
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

    def interp_pwv_date(self, date: NumpyArgument, interp_limit: int = None,
                        method: str = 'linear', order: int = None) -> NumpyReturn:
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
        interp_data = uniform_model.interpolate(method=method, limit=interp_limit, order=order).loc[date]

        if interp_data.isna().any():
            warnings.warn('Some values were outside the permitted interpolation range')

        return interp_data

    def __repr__(self) -> str:
        return 'PWVModel(primary="{}", secondaries={}, data_cuts={})'.format(
            self.primary, self.secondaries, self.data_cuts)
