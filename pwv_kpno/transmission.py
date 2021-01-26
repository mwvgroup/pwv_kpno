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
absorption due to PWV. Dedicated classes are used to represent different
approaches to calculating the atmospheric transmission function:

1. To interpolate through a pre-tabulated atmospheric transmission model, see
   the ``TransmissionModel`` class.
2. To calculate the atmospheric transmission function directly from a set
   of molecular cross-sections, see the ``CrossSectionTransmission``.

Module API
----------
"""
import abc
from typing import Collection, Union

import numpy as np
import pandas as pd
from scipy.interpolate import RegularGridInterpolator
from scipy.stats import binned_statistic

from .types import ArrayLike, NumpyArgument, NumpyReturn


class AbstractTransmission(metaclass=abc.ABCMeta):

    @staticmethod
    def _bin_transmission(wave: ArrayLike, transmission: ArrayLike, resolution: float) -> pd.Series:
        """Bin a transmission functions to a lower resolution using a normalized integration

        Args:
            wave: Array of wavelengths for the sampled transmission values in angstroms
            transmission: Array with transmission values for each wavelength
            resolution: The new resolution to bin to

        Returns:
            A binned version of ``atm_model``
        """

        if resolution <= (np.array(wave[1:]) - wave[:-1]).min():
            raise ValueError('Requested resolution exceeds resolution of underlying model')

        # Create bins that uniformly sample the given wavelength range
        # at the given resolution
        half_res = resolution / 2
        bins = np.arange(
            wave[0] - half_res,
            wave[-1] + half_res + resolution,
            resolution
        )

        # noinspection PyArgumentEqualDefault
        statistic_left, bin_edges_left, _ = binned_statistic(
            wave, transmission, statistic='mean', bins=bins[:-1])

        # noinspection PyArgumentEqualDefault
        statistic_right, bin_edges_right, _ = binned_statistic(
            wave, transmission, statistic='mean', bins=bins[1:])

        dx = bin_edges_left[1] - bin_edges_left[0]
        bin_centers = bin_edges_left[:-1] + dx
        statistic = (statistic_right + statistic_left) / 2
        return pd.Series(statistic, index=bin_centers)

    @abc.abstractmethod
    def __call__(self, pwv: Union[float, Collection[float]], wave: ArrayLike = None, res: float = None) -> pd.DataFrame:
        ...


class Interpolation(AbstractTransmission):
    """Interpolates the PWV transmission function using pre-tabulated transmission values"""

    def __init__(
            self,
            samp_pwv: ArrayLike,
            samp_wave: ArrayLike,
            samp_transmission: ArrayLike
    ) -> None:
        """PWV transmission model that interpolates through pre-tabulated transmission values

        Args:
            samp_pwv: 1D array of PWV values for the sampled transmission
            samp_wave: 1D Array with wavelengths in angstroms for the sampled transmission
            samp_transmission: 2D array with transmission values for each PWV and wavelength
        """

        if not np.all(np.diff(samp_wave) >= 0):
            raise ValueError('Input wavelengths must be sorted.')

        self._samp_pwv = samp_pwv
        self._samp_wave = np.array(samp_wave)
        self._samp_transmission = samp_transmission

        # Always maintain a cached interpolation object for default wavelengths
        # Will raise error for malformed arguments
        self._default_interpolator = self._build_interpolator()

    @staticmethod
    def _calc_pwv_eff(pwv_los: NumpyArgument, norm_pwv: float = 2, eff_exp: float = 0.6) -> NumpyReturn:
        """Convert PWV along line of sight to PWV effective

        ``pwv_effective = (pwv_los / norm_pwv) ** eff_exp``

        See ``calc_pwv_los`` for the inverse of this function.

        Args:
            pwv_los: PWV concentration along line of sight in mm
            norm_pwv: Normalize result such that an effective PWV of one is
                equivalent to this concentration of PWV along line of sight.
            eff_exp: Power by which to scale PWV effective
        """

        return np.divide(pwv_los, norm_pwv) ** eff_exp

    def _build_interpolator(self, res=None) -> RegularGridInterpolator:
        """Build an interpolation object for the given resolution

        Args:
            res: Reduce the resolution of the transmission model before building the interpolator

        Returns:
             A callable interpolation object
        """

        if res is None:
            return self._default_interpolator

        samp_wave, samp_transmission = self._bin_transmission(self._samp_transmission, self._samp_wave, res)
        samp_pwv_eff = self._calc_pwv_eff(self._samp_pwv)
        grid_points = (samp_pwv_eff, samp_wave)
        values = np.array(samp_transmission).T

        try:
            return RegularGridInterpolator(grid_points, values)

        except ValueError:  # Wrap an otherwise cryptic error message
            raise ValueError('Dimensions of sampled transmission values cannot be used to construct a regular grid.')

    def __call__(self, pwv: Union[float, Collection[float]], wave: ArrayLike = None, res: float = None) -> pd.DataFrame:
        """Evaluate transmission model at given wavelengths

        Args:
            pwv: Line of sight PWV to interpolate for
            wave: Wavelengths to evaluate transmission (Defaults to the full underlying resolution)

        Returns:
            The interpolated transmission at the given wavelengths / resolution
        """

        pwv_eff = self._calc_pwv_eff(pwv)  # The interpolation is performed in effective PWV space
        wave = self._samp_wave if wave is None else wave
        interpolator = self._build_interpolator(res)

        if np.isscalar(pwv):
            xi = [[pwv_eff, w] for w in wave]
            return pd.DataFrame([interpolator(xi)], columns=[pwv])

        else:
            # Equivalent to [[[pwv_val, w] for pwv_val in pwv_eff] for w in wave]
            xi = np.empty((len(wave), len(pwv_eff), 2))
            xi[:, :, 0] = pwv_eff
            xi[:, :, 1] = np.array(wave)[:, None]

            return pd.DataFrame(interpolator(xi), columns=pwv)


class Scaling(AbstractTransmission):
    """Scales a sampled PWV transmission function to different PWV values"""

    def __init__(self, samp_pwv: float, samp_wave: ArrayLike, samp_transmission: ArrayLike) -> None:
        """PWV transmission model that rescaled measured transmission values to a new PWV concentration

        Args:
            samp_pwv: PWV concentration of the sampled transmission
            samp_wave: 1D Array with wavelengths in angstroms for the sampled transmission
            samp_transmission: 1D array with transmission values for each wavelength
        """

        self._samp_pwv = samp_pwv
        self._samp_wave = samp_wave
        self._samp_transmission = samp_transmission

    def __call__(self, pwv: Union[float, Collection[float]], wave: ArrayLike = None, res: float = None) -> pd.DataFrame:
        """Evaluate transmission model at given wavelengths

        Args:
            pwv: Line of sight PWV to interpolate for
            wave: Wavelengths to evaluate transmission (Defaults to the full underlying resolution)

        Returns:
            The interpolated transmission at the given wavelengths / resolution
        """

        # Determine the wavelengths and scaled transmission for the given PWV concentration(s)
        pwv = np.atleast_1d(pwv)
        samp_wave = self._samp_wave
        samp_transmission = np.power(self._samp_transmission, np.divide(pwv, self._samp_pwv)[:, None])

        # Reduce the transmission resolution if necessary
        if res:
            samp_wave, samp_transmission = self._bin_transmission(samp_transmission, samp_wave, res)

        # Interpolate the output transmission fro the given wavelengths
        output_wave = self._samp_wave if wave is None else wave
        out_transmission = RegularGridInterpolator([samp_wave], samp_transmission)(output_wave)
        return pd.DataFrame(out_transmission, index=output_wave, columns=pwv)


class CrossSection(AbstractTransmission):
    """Calculated PWV transmission using per-wavelength cross-sections"""

    # Define physical constants
    n_a = 6.02214129E23  # 1 / mol (Avogadro's constant)
    h2o_molar_mass = 18.0152  # g / mol
    h2o_density = 0.99997  # g / cm ** 3
    one_mm_in_cm = 10  # mm / cm

    def __init__(self, samp_wave: ArrayLike, cross_sections: ArrayLike) -> None:
        """PWV transmission model using H20 cross sections

        Transmission values are determined using individual cross sections a
        long with the Beer-Lambert law.

        Args:
            samp_wave: 1D Array of sampled wavelengths in angstroms
            cross_sections: 1D array with cross sections in cm squared
        """

        if not np.all(np.diff(samp_wave) >= 0):
            raise ValueError('Input wavelengths must be sorted.')

        self._samp_wave = np.array(samp_wave)
        self._cross_sections = cross_sections

    @classmethod
    def _num_density_conversion(cls) -> float:
        """Calculate conversion factor from PWV * cross section to optical depth

        Returns:
            The conversion factor in units of 1 / (mm * cm^2)
        """

        return (cls.n_a * cls.h2o_density) / (cls.h2o_molar_mass * cls.one_mm_in_cm)

    def __call__(self, pwv: Union[float, Collection[float]], wave: ArrayLike = None, res: float = None) -> pd.DataFrame:
        """Evaluate the transmission model at the given wavelengths

        Args:
            pwv: Line of sight PWV to interpolate for
            wave: Wavelengths to evaluate transmission for in angstroms
            res: Resolution to bin the atmospheric model to

        Returns:
            The interpolated transmission at the given wavelengths / resolution
        """

        # Evaluate transmission using the Beer-Lambert Law
        tau = pwv * self._cross_sections * self._num_density_conversion()
        transmission = np.exp(-tau)
        samp_wave = self._samp_wave

        if res:
            transmission = self._bin_transmission(transmission, samp_wave, res)
            samp_wave = transmission.index

        # Interpolate the output transmission fro the given wavelengths
        output_wave = self._samp_wave if wave is None else wave
        out_transmission = RegularGridInterpolator([samp_wave], transmission)(output_wave)
        return pd.DataFrame(out_transmission, index=output_wave, columns=pwv)
