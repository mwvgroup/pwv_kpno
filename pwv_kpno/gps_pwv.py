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
given location. This includes location specific weather  data (e.g.,
temperature and pressure measurements) and PWV concentrations (both measured and
modeled).
"""

from astropy.table import Table

from .types import NumpyReturn


class GPSReceiver:
    """Represents data taken by a SuomiNet GPS receiver"""

    # Used to signal that new data has been downloaded and PWV values to
    # be re-loaded into into memory by class instances
    _reload_from_download = [False]

    def __init__(self, primary, secondary=None, data_cuts=None, model=None):
        self._primary = primary
        self._secondary = secondary
        self.data_cuts = data_cuts
        self._model = model

    @property
    def primary(self):
        raise NotImplementedError

    @primary.setter
    def primary(self, value):
        raise NotImplementedError

    @property
    def secondary(self):
        raise NotImplementedError

    @secondary.setter
    def secondary(self, value):
        raise NotImplementedError

    @property
    def model(self):
        raise NotImplementedError

    @model.setter
    def model(self, value):
        raise NotImplementedError

    def modeled_pwv(self) -> Table:
        raise NotImplementedError

    def measured_pwv(self) -> Table:
        raise NotImplementedError

    def weather_data(self) -> Table:
        raise NotImplementedError

    def interp_pwv_date(self) -> NumpyReturn:
        raise NotImplementedError
