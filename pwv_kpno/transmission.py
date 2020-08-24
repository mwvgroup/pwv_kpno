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

from typing import Tuple

import numpy as np
import scipy
from scipy.stats import binned_statistic

from .types import ArrayLike, NumpyArgument


def calc_pwv_eff(pwv_los: NumpyArgument, norm_pwv: float = 2, exp: float = 0.6, ):
    """Convert PWV along line of sight to PWV effective

    pwv_eff =  (pwv_los / norm_pwv) ** exp

    Args:
        pwv_los: PWV along line of sight
        norm_pwv: Normalize result such that an effective PWV of one is
            equivalent to this amount of PWV along line of sight.
        exp: Power by which to scale PWV effective
    """

    return (pwv_los / norm_pwv) ** exp


def bin_transmission(wave, transmission, resolution) -> Tuple[np.arry, np.array]:
    """Bin a transmission table using a normalized integration

    Args:
        wave: Array of wavelengths in angstroms
        transmission: Array with transmission values for each wavelength
        resolution: Resolution to bin to

    Returns:
        A binned version of ``atm_model``
    """

    # Create bins that uniformly sample the given wavelength range
    # at the given resolution
    half_res = resolution / 2
    bins = np.arange(
        min(wave) - half_res,
        max(wave) + half_res + resolution,
        resolution)

    statistic_left, bin_edges_left, _ = binned_statistic(
        wave, transmission, statistic='mean', bins=bins[:-1])

    statistic_right, bin_edges_right, _ = binned_statistic(
        wave, transmission, statistic='mean', bins=bins[1:])

    dx = wave[1] - wave[0]
    statistic = (statistic_right + statistic_left) / 2
    bin_centers = bin_edges_left[:-1] + dx / 2
    return bin_centers, statistic


class Transmission:
    """Represents PWV atmospheric transmission model using pre-tabulated
    transmission values
    """

    def __init__(self, pwv: ArrayLike, wave: ArrayLike, transmission: ArrayLike):
        """PWV transmission model using pre-tabulated transmission values

        Args:
            pwv: 1D array of PWV values
            wave: 2D Array with wavelengths in angstroms
            transmission: 2D array with transmission values for each wavelength
        """

        self.pwv = pwv
        self._pwv_eff = calc_pwv_eff(pwv)
        self.wave = wave
        self.transmission = transmission

    # Todo: Interpolate transmission using PWV effective
    def _transmission(self, pwv: float, resolution: float = None) -> ArrayLike:
        """Return transmission values for a given PWV concentration

        Args:
            pwv: Line of sight PWV concentration to evaluate transmission for
            resolution: Reduce model to the given resolution

        Returns:
            An array of transmission values
        """

        wave, trans = bin_transmission(self.wave, self.transmission, resolution)
        return trans

    def __call__(self, pwv: float, wave: ArrayLike = None, resolution: float = None) -> np.ndarray:
        """Evaluate transmission model at given wavelengths

        Args:
            wave: Wavelengths to evaluate transmission for in angstroms
            resolution: Reduce model to the given resolution

        Returns:
            The interpolated transmission at the given wavelengths / resolution
        """

        wave = wave or self.wave
        trans_at_pwv = self._transmission(pwv)

        # noinspection PyUnresolvedReferences
        return scipy.interpolate.interpn(
            points=wave,
            values=trans_at_pwv,
            xi=[[w] for w in wave]
        )

    def __repr__(self) -> str:
        return 'Transmission(pwv={}, wave={}, transmission={})'.format(self.wave, self.wave, self.transmission)


class CrossSectionTransmission(Transmission):
    """Represents PWV atmospheric transmission model calculated from
    per-wavelength cross-sections
    """

    def __init__(self, wave: ArrayLike, cross_sections: ArrayLike):
        """PWV transmission model using H20 cross sections

        Transmission values are determined using individual cross sections a
        long with the Beer-Lambert law.

        Args:
            wave: 1D Array with wavelengths in angstroms
            cross_sections: 1D array with cross sections in cm squared
        """

        if (cross_sections < 0).any():
            raise ValueError('Cross sections cannot be negative.')

        self.wave = wave
        self.cross_sections = cross_sections

        # Define physical constants
        self.n_a = 6.02214129E23  # 1 / mol (Avogadro's constant)
        self.h2o_molar_mass = 18.0152  # g / mol
        self.h2o_density = 0.99997  # g / cm^3
        self.one_mm_in_cm = 10  # mm / cm

    def _transmission(self, pwv: float, resolution: float = None) -> ArrayLike:
        """Return transmission values for a given PWV concentration

        Args:
            pwv: Line of sight PWV concentration to evaluate transmission for
            resolution: Reduce model to the given resolution

        Returns:
            An array of transmission values
        """

        # Evaluate Beer-Lambert Law
        tau = pwv * self.cross_sections * self.num_density_conversion
        transmission = np.exp(-tau)
        wave, trans = bin_transmission(self.wave, transmission, resolution)
        return trans

    @property
    def num_density_conversion(self) -> float:
        """Calculate conversion factor from PWV * cross section to optical depth

        Returns:
            The conversion factor in units of 1 / (mm * cm^2)
        """

        # Conversion factor 1 / (mm * cm^2)
        return (self.n_a * self.h2o_density) / (self.h2o_molar_mass * self.one_mm_in_cm)

    def __repr__(self) -> str:
        return 'CrossSectionTransmission(pwv={}, wave={}, transmission={})'.format(
            self.wave, self.wave, self.transmission)

