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
#    along with pwv_kpno. If not, see <http://www.gnu.org/licenses/>.

"""This file tests the ``pwv_kpno.types`` module. It ensures  generic type
hints support the correct subscripted types.
"""

from pathlib import Path
from typing import List, Tuple
from unittest import TestCase

from numpy import ndarray
from pandas import Series

from pwv_kpno import types


class TestBase:
    def test_typing_support(self):
        """Test generic type includes expected subscript types"""

        self.assertSequenceEqual(self.support_types, self.hint_type.__args__)


class PathLike(TestBase, TestCase):
    """Tests for the ``PathLike`` generic type"""

    hint_type = types.PathLike
    support_types = (str, Path)


class ArrayLike(TestBase, TestCase):
    """Tests for the ``ArrayLike`` generic type"""

    hint_type = types.ArrayLike
    support_types = (list, ndarray, Series)


class NumpyArgument(TestBase, TestCase):
    """Tests for the ``NumpyArgument`` generic type"""

    hint_type = types.NumpyArgument
    support_types = (float, list, ndarray, Series)


class NumpyReturn(TestBase, TestCase):
    """Tests for the ``NumpyReturn`` generic type"""

    hint_type = types.NumpyReturn
    support_types = (float, ndarray)


class DataCuts1D(TestBase, TestCase):
    """Tests for the ``DataCuts1D`` generic type"""

    hint_type = types.DataCuts1D
    support_types = (str, List[Tuple[float, float]])


class DataCuts(TestBase, TestCase):
    """Tests for the ``DataCuts`` generic type"""

    hint_type = types.DataCuts
    support_types = (str, types.DataCuts1D)
