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

"""The ``transmission`` module is responsible modeling atmospheric
absorption due to PWV.
"""

import numpy as np
import pandas as pd
from scipy.interpolate import LinearNDInterpolator as lNDI
from scipy.spatial.qhull import QhullError
from scipy.stats import binned_statistic

from .types import ArrayLike, NumpyArgument, NumpyReturn


def calc_pwv_eff(pwv_los: NumpyArgument, norm_pwv: float = 2, eff_exp: float = 0.6) -> NumpyReturn:
    """Convert PWV along line of sight to PWV effective

    pwv_eff = (pwv_los / norm_pwv) ** eff_exp

    See ``calc_pwv_los`` for the inverse of this function.

    Args:
        pwv_los: PWV concentration along line of sight in mm
        norm_pwv: Normalize result such that an effective PWV of one is
            equivalent to this concentration of PWV along line of sight.
        eff_exp: Power by which to scale PWV effective
    """

    return np.divide(pwv_los, norm_pwv) ** eff_exp


def calc_pwv_los(pwv_eff: NumpyArgument, norm_pwv: float = 2, eff_exp: float = 0.6) -> NumpyReturn:
    """Convert PWV effective to PWV along line of sight

    pwv_los = norm_pwv * pwv_eff ** (1 / eff_exp)

    See ``calc_pwv_eff`` for the inverse of this function.

    Args:
        pwv_eff: Effective PWV concentration in mm
        norm_pwv: Normalize result such that an effective PWV of one is
            equivalent to this concentration of PWV along line of sight.
        eff_exp: Power by which to scale PWV effective
    """

    return norm_pwv * pwv_eff ** np.divide(1, eff_exp)


def bin_transmission(transmission, resolution, wave=None) -> pd.Series:
    """Bin a transmission table using a normalized integration

    Args:
        transmission: Array with transmission values for each wavelength
        resolution: Resolution to bin to
        wave: Array of wavelengths in angstroms (defaults to ``transmission.index``)

    Returns:
        A binned version of ``atm_model``
    """

    if wave is None:
        wave = transmission.index

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

    dx = bin_edges_left[1] - bin_edges_left[0]
    bin_centers = bin_edges_left[:-1] + dx
    statistic = (statistic_right + statistic_left) / 2
    return pd.Series(statistic, index=bin_centers)


class TransmissionModel:
    """Represents PWV atmospheric transmission model using pre-tabulated
    transmission values.
    """

    def __init__(self, samp_pwv: ArrayLike, samp_wave: ArrayLike, samp_transmission: ArrayLike,
                 norm_pwv: float = 2, eff_exp: float = 0.6):
        """PWV transmission model that interpolates through pre-tabulated transmission values

        Args:
            samp_pwv: 1D array of PWV values for the sampled transmission
            samp_wave: 1D Array with wavelengths in angstroms for the sampled transmission
            samp_transmission: 2D array with transmission values for each PWV and wavelength
        """

        self._samp_pwv = samp_pwv
        self._samp_wave = samp_wave
        self._samp_transmission = samp_transmission
        self._norm_pwv = norm_pwv
        self._eff_exp = eff_exp

        # Build interpolation function used to calculate transmission values
        pwv_eff = calc_pwv_eff(samp_pwv, norm_pwv=norm_pwv, eff_exp=eff_exp)
        points = np.array(np.meshgrid(pwv_eff, samp_wave)).T.reshape(-1, 2)
        values = np.array(samp_transmission).flatten()

        try:
            self._interp_func = lNDI(points, values)

        except QhullError:  # Wrap an otherwise cryptic error message
            raise ValueError('Dimensions of init arguments do not match.')

    @property
    def samp_pwv(self):
        """Returns the value of ``samp_pwv`` specified at init"""

        return self._samp_pwv

    @property
    def samp_wave(self):
        """Returns the value of ``samp_wave`` specified at init"""

        return self._samp_wave

    @property
    def samp_transmission(self):
        """Returns the value of ``samp_transmission`` specified at init"""

        return self._samp_transmission

    def __call__(self, pwv: float, wave: ArrayLike = None) -> pd.Series:
        """Evaluate transmission model at given wavelengths

        Args:
            pwv: Line of sight PWV to interpolate for
            wave: Wavelengths to evaluate transmission for in angstroms

        Returns:
            The interpolated transmission at the given wavelengths / resolution
        """

        wave = self._samp_wave if wave is None else wave
        pwv_eff = calc_pwv_eff(pwv, norm_pwv=self._norm_pwv, eff_exp=self._eff_exp)
        xi = [[pwv_eff, w] for w in wave]

        return pd.Series(self._interp_func(xi), index=wave)


class CrossSectionTransmission:
    """Represents PWV atmospheric transmission model calculated from
    per-wavelength cross-sections
    """

    # Define physical constants
    n_a = 6.02214129E23  # 1 / mol (Avogadro's constant)
    h2o_molar_mass = 18.0152  # g / mol
    h2o_density = 0.99997  # g / cm ** 3
    one_mm_in_cm = 10  # mm / cm

    def __init__(self, samp_wave: ArrayLike, cross_sections: ArrayLike):
        """PWV transmission model using H20 cross sections

        Transmission values are determined using individual cross sections a
        long with the Beer-Lambert law.

        Args:
            samp_wave: 1D Array or sampled wavelengths in angstroms
            cross_sections: 1D array with cross sections in cm squared
        """

        self.samp_wave = samp_wave
        self.cross_sections = cross_sections

    @classmethod
    def _num_density_conversion(cls) -> float:
        """Calculate conversion factor from PWV * cross section to optical depth

        Returns:
            The conversion factor in units of 1 / (mm * cm^2)
        """

        return (cls.n_a * cls.h2o_density) / (cls.h2o_molar_mass * cls.one_mm_in_cm)

    def __call__(self, pwv: float, wave: ArrayLike = None, resolution: float = None) -> pd.Series:
        """Evaluate transmission model at given wavelengths

        Args:
            pwv: Line of sight PWV to interpolate for
            wave: Wavelengths to evaluate transmission for in angstroms
            resolution: Reduce model to the given resolution

        Returns:
            The interpolated transmission at the given wavelengths / resolution
        """

        # Evaluate transmission using the Beer-Lambert Law
        tau = pwv * self.cross_sections * self._num_density_conversion
        transmission = np.interp(wave, self.samp_wave, np.exp(-tau))
        return pd.Series(transmission, index=wave)
