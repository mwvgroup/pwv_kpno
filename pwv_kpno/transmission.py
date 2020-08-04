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


class Transmission:
    """Represents PWV atmospheric transmission model using pre-tabulated
    transmission values
    """

    def __init__(self, wave: ArrayLike, transmission: ArrayLike):
        self.wave = wave
        self.transmission = transmission

    def __call__(self, wave: ArrayLike, resolution: float = None) -> np.array:
        """Evaluate transmission model at given wavelengths

        Args:
            wave: Wavelengths to evaluate transmission for in angstroms
            resolution: Reduce model to the given resolution

        Returns:
            The interpolated transmission at the given wavelengths / resolution
        """

        # Note: Interpolate transmission in using PWV effective and not PWV line of sight
        raise NotImplementedError

    def at_resolution(self, res: float) -> ArrayLike:
        """Bin the transmission model to a given resolution

        Args:
            res: New resolution in angstroms

        Returned:
            The binned transmission values of the model
        """

        raise NotImplementedError

    def __repr__(self) -> str:
        return '<Transmission(name={})>'.format(self.name)


class CrossSectionTransmission(Transmission):
    """Represents PWV atmospheric transmission model calculated from
    per-wavelength cross-sections
    """

    def __init__(self, wave: ArrayLike, cross_sections: ArrayLike):
        if (cross_sections < 0).any():
            raise ValueError('Cross sections cannot be negative.')

        self.wave = wave
        self.cross_sections = cross_sections

        # Define physical constants
        self.n_a = 6.02214129E23  # 1 / mol (Avogadro's constant)
        self.h2o_molar_mass = 18.0152  # g / mol
        self.h2o_density = 0.99997  # g / cm^3
        self.one_mm_in_cm = 10  # mm / cm

    @property
    def num_density_conversion(self) -> float:
        """Calculate conversion factor from PWV * cross section to optical depth

        Returns:
            The conversion factor in units of 1 / (mm * cm^2)
        """

        # Conversion factor 1 / (mm * cm^2)
        return (self.n_a * self.h2o_density) / (self.h2o_molar_mass * self.one_mm_in_cm)

    def __call__(self, wave: ArrayLike, resolution: float = None) -> np.array:
        """Evaluate transmission model at given wavelengths

        Args:
            wave: Wavelengths to evaluate transmission for in angstroms
            resolution: Reduce model to the given resolution

        Returns:
            The interpolated transmission at the given wavelengths / resolution
        """

        pwv_num_density = self.cross_sections * self.num_density_conversion
        raise NotImplementedError


# Todo: Define the default transmission model
default_model = Transmission([], [])
