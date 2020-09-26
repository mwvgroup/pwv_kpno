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

"""The ``defaults`` module provides pre-built ``GPSReceiver`` instances and
transmission models. These instances are provided for convenience and include
settings selected by the developers as being desirable for most general
science cases. Summaries for each object provided in the ``defaults`` module
are provided below.

Usage Example
-------------

.. code-block:: python

   # Load the pre-built data access object for Kitt Peak National Observatory
   from pwv_kpno.defaults import kitt

   # Use pre-built instances like any other instance
   print(kitt.primary)
   print(kitt.secondaries)
   print(kitt.data_cuts)

Default Objects
---------------

+--------------------------+------------------------------+------------------------------------------------------------+
| Instance Name            | Object Type                  | Summary                                                    |
+==========================+==============================+============================================================+
|                          |                              | Default data access for Kitt Peak National Observatory.    |
| ``kitt``                 | ``GPSReceiver``              | Includes preselected secondary receivers and data cuts on  |
|                          |                              | the measured pressure values.                              |
+--------------------------+------------------------------+------------------------------------------------------------+
|                          |                              | Default data access for Cerro-tololo International         |
| ``ctio``                 | ``GPSReceiver``              | Observatory Includes no secondary receivers                |
|                          |                              | but some data cuts.                                        |
+--------------------------+------------------------------+------------------------------------------------------------+
| ``default_transmission`` | ``TransmissionModel``        | Default atmospheric transmission model based on TAPAS      |
+--------------------------+------------------------------+------------------------------------------------------------+
| ``v1_transmission``      | ``CrossSectionTransmission`` | For backwards compatibility only. The atmospheric          |
|                          |                              | transmission model from Version 1 of the package.          |
+--------------------------+------------------------------+------------------------------------------------------------+



"""

from pathlib import Path

import pandas as pd

# Private to prevent user from thinking there is a default ``transmission`` or ``GPSReceiver`` object
from . import transmission as _transmission
from .gps_pwv import PWVModel as _GPSReceiver

# default_transmission = _transmission.TransmissionModel([], [], [])

_defaults_dir = Path(__file__).resolve().parent / 'default_atmosphere'
_default_v1_data = pd.read_csv(_defaults_dir / 'h2ocs.txt', usecols=[1, 2], delimiter=' ', header=None, names=['wave', 'cross_section'])
v1_transmission = _transmission.CrossSectionTransmission(
    _default_v1_data.wave * 1000,
    _default_v1_data.cross_section)

kitt = _GPSReceiver('KITT', ('AZAM', 'SA48', 'P014', 'SA46'))
ctio = _GPSReceiver('CTIO')
