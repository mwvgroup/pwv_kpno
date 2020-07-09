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

"""The ``transmission.py`` module is responsible modeling atmospheric
absorption due to PWV.
"""

from .types import NumpyReturn


class Transmission:
    """Represents an PWV atmospheric transmission model"""

    def __init__(self, wave, transmission):
        self.wave = wave
        self.transmission = transmission

    def trans_at_wave(self, wave) -> NumpyReturn:
        raise NotImplementedError

# Todo: Define the default transmission model
# default_model = Transmission()
