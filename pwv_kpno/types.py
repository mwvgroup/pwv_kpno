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

"""The ``types`` module defines typing aliases used by the parent package to
inform type hints. Aliases defined here can be used to support type hints in
downstream projects for which **pwv_kpno** is a dependency, and ensure
compatibility with modern IDE inspection tools.

For more information on Python type hinting, see Python
Enhancement Protocol 484: https://www.python.org/dev/peps/pep-0484/ .

Typing Aliases
--------------

+---------------------------+-------------------------------------------------+
| Alias                     | Typing Equivalence                              |
+===========================+=================================================+
| ``PathLike``              | ``Union[str, Path]``                            |
+---------------------------+-------------------------------------------------+
| ``ArrayLike``             | ``Union[list, ndarray, Series]``                |
+---------------------------+-------------------------------------------------+
| ``NumpyArgument``         | ``Union[float, list, ndarray, Series]``         |
+---------------------------+-------------------------------------------------+
| ``NumpyReturn``           | ``Union[float, ndarray]``                       |
+---------------------------+-------------------------------------------------+
| ``DataCuts1D``            | ``Dict[str, List[Tuple[float, float]]]``        |
+---------------------------+-------------------------------------------------+
| ``DataCuts``              | ``Dict[str, DataCuts1D]``                       |
+---------------------------+-------------------------------------------------+


"""

from pathlib import Path as Path
from typing import Dict, List, Tuple, Union

from numpy import ndarray
from pandas import Series

PathLike = Union[str, Path]
ArrayLike = Union[list, ndarray, Series]
NumpyArgument = Union[float, list, ndarray, Series]
NumpyReturn = Union[float, ndarray]
DataCuts1D = Dict[str, List[Tuple[float, float]]]
DataCuts = Dict[str, DataCuts1D]
