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

"""Utilities used to ensure a stable and predictable testing environment"""

import functools
import os
from datetime import datetime, timedelta
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import List, Tuple, Union

from astropy.table import Table
from pytz import utc


class TestWithCleanEnv:
    """Context manager and decorator for running tests in a clean environment

    Clears all environmental variables and sets ``SUOMINET_DIR`` to a temporary
    directory.
    """

    def __init__(self, data_path: Union[str, Path] = None):
        """Clears all environmental variables and set ``SUOMINET_DIR``

        Value for ``SUOMINET_DIR`` defaults to a temporary directory.

        Args:
            data_path: Optional path to set ``SUOMINET_DIR`` to
        """

        if isinstance(data_path, Path):
            data_path = str(data_path)

        self._data_path = data_path

    def __call__(self, obj):
        # Decide whether we should wrap a callable or a class

        if isinstance(obj, type):
            return self._decorate_class(obj)

        return self._decorate_callable(obj)

    def __enter__(self):
        # Store a copy of environmental variables and clear the environment

        self._old_environ = dict(os.environ)
        os.environ.clear()

        if self._data_path:  # Use user defined path
            os.environ['SUOMINET_DIR'] = self._data_path

        else:
            self._temp_dir = TemporaryDirectory()
            os.environ['SUOMINET_DIR'] = self._temp_dir.name

    def __exit__(self, *args):
        # Restore the original environment

        os.environ.clear()
        os.environ.update(self._old_environ)

        if not self._data_path:  # If there is no user defined path
            self._temp_dir.cleanup()

    def _decorate_callable(self, func: callable) -> callable:
        # Decorates a callable

        @functools.wraps(func)
        def inner(*args, **kwargs):
            with TestWithCleanEnv(self._data_path):
                return func(*args, **kwargs)

        return inner

    def _decorate_class(self, wrap_class: type) -> type:
        # Decorates methods in a class with request_mock
        # Method will be decorated only if it name begins with ``test_``

        for attr_name in dir(wrap_class):
            # Skip attributes without correct prefix
            if not attr_name.startswith('test_'):
                continue

            # Skip attributes that are not callable
            attr = getattr(wrap_class, attr_name)
            if not hasattr(attr, '__call__'):
                continue

            setattr(wrap_class, attr_name, self._decorate_callable(attr))

        return wrap_class


def create_mock_pwv_model(year: int, gaps: List[Tuple[datetime, datetime]] = None):
    """Create a mock model for the PWV level at Kitt Peak for airmass 1

    Return a table with the columns "date" and "pwv" and "pwv_err". Dates span
    the given year in 30 minute increments and are represented in UTC. PWV
    values are calculated as the index of its position in the table modulo
    15 mm. Error values are 10% of the PWV values. Gaps in the returned data
    can be included via the gaps argument.

    Args:
        year  (int): The year of the desired model
        gaps (list): [(start day as datetime, gap length in days as int), ]

    Returns:
        The modeled data set as an astropy table
    """

    start_date = datetime(year - 1, 12, 31, 23, 45, tzinfo=utc)
    end_date = datetime(year + 1, 1, 1, tzinfo=utc)
    total_time_intervals = (end_date - start_date).days * 24 * 60 // 30

    out_table = Table(names=['date', 'pwv', 'pwv_err'],
                      dtype=[float, float, float])

    for i in range(total_time_intervals):
        start_date += timedelta(minutes=30)
        pwv = i % 15
        out_table.add_row([start_date.timestamp(), pwv, pwv * .1])

    if gaps is not None:
        intervals = 48  # number of 30 min intervals in a day
        gap_indices = []

        for date, length in gaps:
            gap_start = (date - start_date).days
            gap_end = gap_start + length
            gap_range = range(gap_start * intervals, gap_end * intervals)
            gap_indices.extend(gap_range)

        out_table.remove_rows(gap_indices)

    return out_table
