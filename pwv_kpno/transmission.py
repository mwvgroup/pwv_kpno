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
from typing import Collection, Union, overload

import numpy as np
import pandas as pd
from scipy.interpolate import RegularGridInterpolator
from scipy.stats import binned_statistic

from .types import ArrayLike, NumpyArgument, NumpyReturn


def calc_pwv_eff(pwv_los: NumpyArgument, norm_pwv: float = 2, eff_exp: float = 0.6) -> NumpyReturn:
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


def calc_pwv_los(pwv_eff: NumpyArgument, norm_pwv: float = 2, eff_exp: float = 0.6) -> NumpyReturn:
    """Convert PWV effective to PWV along line of sight

    ``pwv_los = norm_pwv * pwv_eff ** (1 / eff_exp)``

    See ``calc_pwv_eff`` for the inverse of this function.

    Args:
        pwv_eff: Effective PWV concentration in mm
        norm_pwv: Normalize result such that an effective PWV of one is
            equivalent to this concentration of PWV along line of sight.
        eff_exp: Power by which to scale PWV effective
    """

    return norm_pwv * pwv_eff ** np.divide(1, eff_exp)


class AbstractTransmission(metaclass=abc.ABCMeta):
    """Base calss for building transmission objects"""

    samp_wave = None  # Default model wavelengths to be defined by child class

    @staticmethod
    def _bin_transmission(transmission: ArrayLike, wave: ArrayLike, resolution: float) -> pd.Series:
        """Bin a transmission functions to a lower resolution using a normalized integration

        Args:
            transmission: Array with transmission values for each wavelength
            wave: Array of wavelengths for the sampled transmission values in angstroms
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
            resolution)

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
    def _calc_transmission(self, pwv: float, wave: ArrayLike = None, res: float = None) -> pd.Series:
        ...

    @overload
    def __call__(self, pwv: float, wave: ArrayLike = None, res: float = None) -> pd.Series:
        ...

    @overload
    def __call__(self, pwv: Collection[float], wave: ArrayLike = None, res: float = None) -> pd.DataFrame:
        ...

    def __call__(self, pwv, wave=None, res=None):
        """Evaluate the transmission model at the given wavelength values

        Args:
            pwv: PWV concentration along the line of sight
            wave: Wavelengths to evaluate transmission for in angstroms
            res: Optionally bin the returned transmission to the given resolution

        Returns:
            The atmospheric transmission evaluated at the given wavelengths / resolution
        """

        wave = self.samp_wave if wave is None else wave
        if np.isscalar(pwv):
            return self._calc_transmission(pwv, wave, res)

        else:
            return pd.concat([self.__call__(p, wave, res) for p in pwv], axis=1)


class TransmissionModel(AbstractTransmission):
    """Interpolates the PWV transmission function using pre-tabulated transmission values"""

    def __init__(
            self,
            samp_pwv: ArrayLike,
            samp_wave: ArrayLike,
            samp_transmission: ArrayLike,
            norm_pwv: float = 2,
            eff_exp: float = 0.6
    ) -> None:
        """PWV transmission model that interpolates through pre-tabulated transmission values

        Args:
            samp_pwv: 1D array of PWV values for the sampled transmission
            samp_wave: 1D Array with wavelengths in angstroms for the sampled transmission
            samp_transmission: 2D array with transmission values for each PWV and wavelength
        """

        if not np.all(np.diff(samp_wave) >= 0):
            raise ValueError('Input wavelengths must be sorted.')

        self.samp_pwv = samp_pwv
        self.samp_wave = np.array(samp_wave)
        self.samp_transmission = samp_transmission
        self.norm_pwv = norm_pwv
        self.eff_exp = eff_exp

        # Will raise error for malformed arguments
        self._build_interpolator(samp_pwv, samp_wave, samp_transmission)

    @staticmethod
    def _build_interpolator(samp_pwv: ArrayLike, samp_wave: ArrayLike,
                            samp_transmission: ArrayLike) -> RegularGridInterpolator:
        """Construct a scipy interpolator for a given set of wavelengths, PWV,  and transmissions

        Interpolation if performed as a function of PWV effective.

        Args:
            samp_pwv: 1D array of PWV values for the sampled transmission
            samp_wave: 1D Array with wavelengths in angstroms for the sampled transmission
            samp_transmission: 2D array with transmission values for each PWV and wavelength
        """

        grid_points = (samp_pwv, samp_wave)
        values = np.array(samp_transmission).T

        try:
            return RegularGridInterpolator(grid_points, values)

        except ValueError:  # Wrap an otherwise cryptic error message
            raise ValueError('Dimensions of init arguments do not match.')

    def _calc_transmission(self, pwv: float, wave: ArrayLike = None, res: float = None) -> pd.Series:
        """Evaluate the transmission model at the given wavelengths

        Args:
            pwv: Line of sight PWV to interpolate for
            wave: Wavelengths to evaluate transmission for in angstroms
            res: Resolution to bin the atmospheric model to

        Returns:
            The interpolated transmission at the given wavelengths / resolution
        """

        # Build interpolation function
        sampled_pwv = calc_pwv_eff(self.samp_pwv, self.norm_pwv, self.eff_exp)
        sampled_transmission = self.samp_transmission
        sampled_wavelengths = self.samp_wave
        if res:
            sampled_transmission = self._bin_transmission(sampled_transmission, wave, res)
            sampled_wavelengths = sampled_wavelengths.index

        interp_func = self._build_interpolator(sampled_pwv, sampled_wavelengths, sampled_transmission)

        # Build interpolation grid
        pwv_eff = calc_pwv_eff(pwv, norm_pwv=self.norm_pwv, eff_exp=self.eff_exp)
        xi = [[pwv_eff, w] for w in wave]

        return pd.Series(interp_func(xi), index=wave, name=f'{float(np.round(pwv, 4))} mm')


class CrossSectionTransmission(AbstractTransmission):
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

        self.samp_wave = np.array(samp_wave)
        self.cross_sections = cross_sections

    @classmethod
    def _num_density_conversion(cls) -> float:
        """Calculate conversion factor from PWV * cross section to optical depth

        Returns:
            The conversion factor in units of 1 / (mm * cm^2)
        """

        return (cls.n_a * cls.h2o_density) / (cls.h2o_molar_mass * cls.one_mm_in_cm)

    def _calc_transmission(
            self,
            pwv: Union[float, Collection[float]],
            wave: ArrayLike = None,
            res: float = None
    ):
        """Evaluate the transmission model at the given wavelengths

        Args:
            pwv: Line of sight PWV to interpolate for
            wave: Wavelengths to evaluate transmission for in angstroms
            res: Resolution to bin the atmospheric model to

        Returns:
            The interpolated transmission at the given wavelengths / resolution
        """

        # Evaluate transmission using the Beer-Lambert Law
        tau = pwv * self.cross_sections * self._num_density_conversion()
        transmission = np.exp(-tau)
        transmission_wavelengths = self.samp_wave

        if res:
            transmission = self._bin_transmission(transmission, transmission_wavelengths, res)
            transmission_wavelengths = transmission.index

        return pd.Series(
            np.interp(wave, transmission_wavelengths, transmission),
            name=f'{float(np.round(pwv, 4))} mm',
            index=wave)
