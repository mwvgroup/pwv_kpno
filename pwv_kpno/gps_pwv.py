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
        data: pd.DataFrame, year: int = None, month: int = None, day=None, hour=None,
        colname: str = 'date') -> pd.DataFrame:
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


def _apply_data_cuts(data: pd.DataFrame, data_cuts: dict, exclusive: bool) -> pd.DataFrame:
    """Apply data cuts from settings to a table of SuomiNet measurements

    Args:
        data: A table containing data from a SuomiNet data file
        data_cuts: Dict of tuples with (upper, lower) bounds for each column
        exclusive: Whether ``data_cuts`` exclude the given regions as opposed
            to including them.

    Returns:
        A copy of the data with applied data cuts
    """

    for param_name, cut_list in data_cuts.items():
        for start, end in cut_list:
            indices = (start < data[param_name]) & (data[param_name] < end)

            if exclusive:
                indices = ~indices

            data = data[indices]

    return data


class GPSReceiver:
    """Represents data taken by a SuomiNet GPS receiver"""

    def __init__(self, primary: str, secondaries: Tuple[str] = None,
                 exclude_cut: dict = None, include_cut: dict = None):
        """Provides data access to weather and PWV data for a GPS receiver

        Args:
            primary: SuomiNet Id of the receiver to access
            secondaries: Secondary receivers used to supplement periods with
                missing primary data
            exclude_cut: Ignore data in the given ranges
            include_cut: Only include data in the given ranges
        """

        self._primary = primary
        self._secondaries = tuple(secondaries) if secondaries else tuple()
        self._exclude_cut = exclude_cut
        self._include_cut = include_cut

        # Lazy load this data to account for call of attribute setters
        self._instance_data = None
        self._pwv_model = None

    @property
    def primary(self) -> str:
        return self._primary

    @primary.setter
    def primary(self, value):
        self._primary = value
        self._instance_data = None
        self._pwv_model = None

    @property
    def secondaries(self) -> Tuple[str]:
        return self._secondaries

    @secondaries.setter
    def secondaries(self, value):
        self._secondaries = tuple(value)
        self._instance_data = None
        self._pwv_model = None

    @property
    def exclude_cut(self):
        return deepcopy(self._exclude_cut)

    @property
    def include_cut(self):
        return deepcopy(self._include_cut)

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

        raise NotImplementedError

    def weather_data(self, year: int = None, month: int = None, day=None, hour=None) -> pd.DataFrame:
        """Returns a table of all weather_Data data for the primary receiver

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

        # Todo: Decide how to handle data cuts
        # Todo: This return should not include secondary PWV values
        if self._instance_data is None:
            receivers = set(self.secondaries)
            receivers.add(self.primary)
            self._instance_data = pd.concat({rec: load_rec_directory(rec) for rec in receivers}, axis=1)

        return _search_data_table(self._instance_data, year, month, day, hour)

    def interp_pwv_date(self, date: NumpyArgument) -> NumpyReturn:
        """Evaluate the PWV model for a given datetime

        Args:
            date: UTC datetime object or timestamp

        Returns:
            Line of sight PWV concentration at the given datetime
        """

        raise NotImplementedError
