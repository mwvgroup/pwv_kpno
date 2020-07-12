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

import numpy as np

from .types import ArrayLike


# Todo: how do we want to scale transmission values?
# Via cross section?
# Via [T_fiducial ^ (1 / pwv_fid)] ^ pwv ?
# Via interpolation?

class Transmission:
    """Represents an PWV atmospheric transmission model"""

    def __init__(self, wave: ArrayLike, transmission: ArrayLike, name: str = None):
        self.pwv = 0
        self.name = name
        self.wave = wave
        self.transmission = transmission

    def __call__(self, wave: ArrayLike, resolution: float = None) -> np.array:
        """Evaluate transmission model at given wavelengths

        Args:
            wave: Wavelengths to evaluate transmission for in angstroms
            resolution: Reduce model to the given resolution

        Returned:
            The interpolated transmission at the given wavelengths / resolution
        """

        raise NotImplementedError

    def at_resolution(self, res: float) -> ArrayLike:
        """Bin the transmission model to a given resolution

        Args:
            res: New resolution in angstroms

        Returned:
            The binned transmission values of the model
        """

        raise NotImplementedError

    def __repr__(self):
        return '<Transmission(name={})>'.format(self.name)


# Todo: Define the default transmission model
default_model = Transmission([], [])
