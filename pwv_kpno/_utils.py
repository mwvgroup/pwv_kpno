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

"""The ``_utils`` module is a grab bag of utilities for running fits and
manipulating tabular data.
"""

import warnings
from datetime import datetime

import numpy as np
import pandas as pd
from scipy.odr import ODR, Output, RealData, polynomial

from .types import DataCuts


def apply_data_cuts(data: pd.DataFrame, cuts: DataCuts) -> pd.DataFrame:
    """Apply a dictionary of data cuts to a DataFrame

    Data cuts on ``date`` values are exclusive. All other data cuts are inclusive.

    Args:
        data: Data to apply cuts on
        cuts: Dict of column names with a list of tuples [(cut start, cut end), ...]

    Returns:
        A subset of the passed DataFrame
    """

    for param_name, cut_list in cuts.items():
        for start, end in cut_list:
            if param_name == 'date':
                data = data[(data.index <= start) & (end <= data.index)]

            else:
                data = data[(start <= data[param_name]) & (data[param_name] <= end)]

    return data


def linear_regression(x: np.array, y: np.array, sx: np.array, sy: np.array) -> Output:
    """Optimize and apply a linear regression using masked arrays

    Generates a linear fit ``f`` using orthogonal distance regression and
    returns the applied model ``f(x)``.

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
        data: pd.DataFrame, year: int = None, month: int = None, day=None, hour=None) -> pd.DataFrame:
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
