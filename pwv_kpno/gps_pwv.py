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

from datetime import datetime

from astropy.table import Table

from .types import NumpyReturn


def search_data_table(data, year: int = None, month: int = None, day=None, hour=None):
    # Raise exception for bad datetime args
    datetime(year, month, day, hour)
    raise NotImplementedError


class GPSReceiver:
    """Represents data taken by a SuomiNet GPS receiver"""

    # Used to signal that new data has been downloaded and PWV values need to
    # be re-loaded into into memory by class instances
    _reload_from_download = [False]

    def __init__(self, primary, secondaries=None, data_cuts=None):
        self._primary = primary
        self._secondaries = tuple(secondaries)
        self.data_cuts = data_cuts

    @property
    def primary(self):
        return self._primary

    @primary.setter
    def primary(self, value):
        raise NotImplementedError

    @property
    def secondaries(self):
        return self._secondaries

    @secondaries.setter
    def secondaries(self, value):
        raise NotImplementedError

    def modeled_pwv(self, year: int = None, month: int = None, day=None, hour=None) -> Table:
        raise NotImplementedError

    def weather_data(self, year: int = None, month: int = None, day=None, hour=None) -> Table:
        raise NotImplementedError

    def interp_pwv_date(self) -> NumpyReturn:
        raise NotImplementedError
