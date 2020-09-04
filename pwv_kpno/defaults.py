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

# Underscores to prevent user from thinking there is a default ``transmission``
# or ``GPSReceiver`` object
from . import transmission as _transmission
from .gps_pwv import PWVModel as _GPSReceiver

# default_transmission = _transmission.TransmissionModel([], [], [])
# v1_transmission = _transmission.CrossSectionTransmission([], [])

kitt = _GPSReceiver('KITT', ('AZAM', 'SA48', 'P014', 'SA46'))
