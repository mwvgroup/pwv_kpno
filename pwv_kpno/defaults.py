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

"""The ``defaults`` module provides pre-built transmission models and data
access objects as a convenience for the user.

Transmission models are provided
using both the original, MODTRAN based transmission data from version 1.0 of
**pwv_kpno** (deprecated), and using an updated set of measurements base on
TAPAS. Data access objects are also included for select GPS locations, and
include settings selected by the developers as being desirable for most general
science cases.

Default Data Access Objects
---------------------------

+--------------------------+-----------------------------------------------+----------------------------------+
| Instance Name            | Summary                                       | Data Cuts                        |
+==========================+===============================================+==================================+
| ``azam``                 | Default data access for Amado Arizona.        |   800 < SrfcPress < 925   mbar   |
+--------------------------+-----------------------------------------------+----------------------------------+
| ``ctio``                 | Default data access for Cerro-Tololo          |   0 < PWV < 30   mm              |
|                          | International Observatory.                    |                                  |
+--------------------------+-----------------------------------------------+----------------------------------+
|                          | Default data access for Kitt Peak National    | 775 < SrfcPress < 1000 mbar      |
| ``kitt``                 | Observatory. Data cuts include a period where | and drops UTC timestamps         |
|                          | the pressure sensor was malfunctioning        | 1451606400 through 1459468800    |
+--------------------------+-----------------------------------------------+----------------------------------+
| ``P014``                 | Default data access for Sahuarita Arizona.    |   870 < SrfcPress < 1000   mbar  |
+--------------------------+-----------------------------------------------+----------------------------------+
| ``SA46``                 | Default data access for Tucson Arizona.       |   900 < SrfcPress < 1000   mbar  |
+--------------------------+-----------------------------------------------+----------------------------------+
| ``SA48``                 | Default data access for Sells Arizona.        |   910 < SrfcPress < 1000   mbar  |
+--------------------------+-----------------------------------------------+----------------------------------+

Default Transmission Models
---------------------------

+--------------------------+------------------------------+--------------------------------------------------+
| Instance Name            | Model Type                   | Summary                                          |
+==========================+==============================+==================================================+
| ``v1_transmission``      | ``CrossSectionTransmission`` | The same MODTRAN based atmospheric transmission  |
|                          |                              | model used in Version 1 of **pwv_kpno**.         |
+--------------------------+------------------------------+--------------------------------------------------+

"""

from pathlib import Path

import pandas as pd

# Import as private to prevent name conflicts
from . import transmission as _transmission
from .gps_pwv import GPSReceiver as _GPSReceiver, PWVModel as _PWVModel

_defaults_dir = Path(__file__).resolve().parent / 'default_atmosphere'

kitt = _GPSReceiver('KITT', data_cuts={'SrfcPress': [(775, 1000), ], 'date': [(1451606400.0, 1459468800.0), ]}, cache_data=False)
azam = _GPSReceiver('AZAM', data_cuts={'SrfcPress': [(880, 925), ]}, cache_data=False)
p014 = _GPSReceiver('P014', data_cuts={'SrfcPress': [(870, 1000), ]}, cache_data=False)
sa46 = _GPSReceiver('SA46', data_cuts={'SrfcPress': [(900, 1000), ]}, cache_data=False)
sa48 = _GPSReceiver('SA48', data_cuts={'SrfcPress': [(910, 1000), ]}, cache_data=False)
ctio = _GPSReceiver('CTIO', data_cuts={'PWV': [(0, 30), ]})
kitt_model = _PWVModel(kitt, secondaries=(azam, p014, sa46, sa48))


def _load_v1_transmission() -> _transmission.CrossSection:
    _default_v1_data = pd.read_csv(
        _defaults_dir / 'h2ocs.txt',
        usecols=[1, 2],
        delimiter=' ',
        header=None,
        names=['wave', 'cross_section'])

    return _transmission.CrossSection(
        _default_v1_data.wave * 10_000,  # Convert wavelength values to angstroms
        _default_v1_data.cross_section)


v1_transmission = _load_v1_transmission()
