#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""This module provides modeling for the effects of atmospheric absorption
due to precipitable water vapor (PWV) on a black body.

For full documentation on a function use the builtin Python `help` function
or see https://mwvgroup.github.io/pwv_kpno/.

An incomplete guide to getting started:

    To determine the SED of a black body under the influence of atmospheric
    effects due to a known PWV concentration (in mm):

    >>> import numpy as np
    >>> from pwv_kpno import blackbody_with_atm as bb_atm
    >>>
    >>> bb_temp = 8000  # Black Body temperature in Kelvin
    >>> wavelengths = np.arange(7000, 10000, 100)  # Wavelengths in Angstrom
    >>> pwv = 15  # Integrated PWV concentration in mm
    >>>
    >>> sed = bb_atm.sed(bb_temp, wavelengths, pwv)


    To determine the magnitude of a black body either with (PWV > 0) or without
    (PWV = 0) atmospheric effects:

    >>> from pwv_kpno import blackbody_with_atm as bb_atm
    >>>
    >>> bb_temp = 8000
    >>> i_band = (7000, 8500)
    >>> pwv = 15
    >>>
    >>> bb_mag = bb_atm.magnitude(bb_temp, i_band, pwv)


    To determine the residual error in the zero point of a photometric image
    due to PWV:

    >>> from pwv_kpno import blackbody_with_atm as bb_atm
    >>>
    >>> reference_star_temp = 4000
    >>> other_star_temp = 10000
    >>> bias = bb_atm.zp_bias(reference_star_temp,
    >>>                       other_star_temp,
    >>>                       i_band,
    >>>                       pwv)
"""

from typing import Union

import numpy as np
from astropy import units as u
from astropy.constants import c
from astropy.modeling.blackbody import blackbody_lambda

from pwv_kpno.pwv_atm import trans_for_pwv

__authors__ = ['Daniel Perrefort']
__copyright__ = 'Copyright 2017, Daniel Perrefort'

__license__ = 'GPL V3'
__email__ = 'djperrefort@pitt.edu'
__status__ = 'Release'


def sed(temp, wavelengths, pwv, bins=None):
    # type: (float, np.ndarray, float) -> np.ndarray[float]
    """Return the flux of a black body under the influence of pwv absorption

     Flux is returned in units of ergs / (angstrom * cm2 * s).

     Args:
         temp        (float): The temperature of the black body in Kelvin
         wavelengths (array): The SED's wavelengths in Angstroms
         pwv         (float): The PWV concentration along line of sight in mm
         bins  (int or list): Integer number of bins or sequence of bin edges
                               used to smooth atmospheric transmission

     Returns:
         An array of flux values in units of ergs / (angstrom * cm2 * s * sr)
     """

    # blackbody_lambda returns ergs / (angstrom * cm2 * s * sr)
    bb_sed = blackbody_lambda(wavelengths, temp).value

    if pwv > 0:
        transmission = trans_for_pwv(pwv, bins=bins)
        sampled_transmission = np.interp(wavelengths,
                                         transmission['wavelength'],
                                         transmission['transmission'])

        bb_sed *= sampled_transmission

    return bb_sed


def magnitude(temp, band, pwv):
    # type: (float, Union[tuple, np.ndarray], float) -> float
    """Return the AB magnitude of a black body in a given band

    Magnitudes are calculated relative to a zero point of 3631 Jy. If the band
    argument is a 1d array of wavelengths, then the photometric band is treated
    as a top-hat function ranging from the first value in the array to the
    last. If it is two dimensional then the first dimension is treated as
    wavelength values and the second as the response function for the given
    band. All wavelengths values are expected in Angstroms.

    Args:
        temp (float): The temperature of the black body in Kelvin
        band (tuple): An array specifying a photometric bandpass
        pwv  (float): The PWV concentration along line of sight in mm

    Returns:
        The magnitude of the desired black body as effected by H2O absorption
    """

    if np.ndim(band) == 1:
        wavelengths = np.arange(band[0], band[-1])
        flux_pwv = sed(temp, wavelengths, pwv)

    else:
        wavelengths = band[0]
        flux_pwv = sed(temp, wavelengths, pwv)
        flux_pwv *= band[1]

    # We introduce units here to make dimensional analysis easier
    lambda_over_c = (np.median(wavelengths) * u.AA) / c
    flux_pwv *= u.erg / (u.AA * u.cm * u.cm * u.s * u.sr)
    flux_pwv *= 2 * np.pi * u.sr  # integrate over angular coordinates
    flux_pwv *= lambda_over_c.cgs

    zero_point = (3631 * u.jansky).to(u.erg / u.cm ** 2)
    int_flux = np.trapz(x=wavelengths, y=flux_pwv) * u.AA
    mag = -2.5 * np.log10(int_flux / zero_point)

    return mag.value


def zp_bias(ref_temp, cal_temp, band, pwv):
    # type: (float, float, tuple[float, int], float) -> float
    """Calculate the residual error in the photometric zero point due to PWV

    Using a black body approximation, calculate the residual error in the zero
    point of a photometric image cause by not considering the PWV transmission
    function. Returned values are in units of magnitude relative to a zero
    point of 3631 Jy.

    Args:
        ref_temp (float): The temperature of the star used to calibrate the
                            image in Kelvin
        cal_temp (float): The temperature of another star in the same image
        band     (tuple): An array specifying a photometric bandpass
        pwv      (float): The PWV concentration along line of sight in mm

    Returns:
        The error in magnitudes for the photometric zero point of the given band
    """

    # Values for reference star
    ref_mag = magnitude(ref_temp, band, 0)
    ref_mag_atm = magnitude(ref_temp, band, pwv)
    ref_zero_point = ref_mag - ref_mag_atm

    # Values for star being calibrated
    cal_mag = magnitude(cal_temp, band, 0)
    cal_mag_atm = magnitude(cal_temp, band, pwv)
    cal_zero_point = cal_mag - cal_mag_atm

    bias = cal_zero_point - ref_zero_point
    return bias
