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

"""The ``defaults`` module provides default transmission and data access
objects with pre-defined data cuts that have been investigated for each site.
"""

from .gps_pwv import GPSReceiver
from .transmission import Transmission

# Todo: Define the default transmission model
default_transmission = Transmission([], [], [])

default_KITT = GPSReceiver('KITT')

default_CTIO = GPSReceiver('CTIO')
