#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""This module provides modeling for the effects of atmospheric absorption
due to precipitable water vapor (PWV) on a black body.
"""

# Todo: Write rst documentation

from astropy import units as u
from astropy.modeling.blackbody import blackbody_lambda
from astropy.constants import c
import numpy as np

from pwv_kpno.transmission import transmission_pwv


def sed(temp, wavelengths, pwv):
    """Return the flux of a black body under the influence of pwv absorption

     Flux is returned in units of ergs / (angstrom * cm2 * s)

     Args:
         temp          (float): The desired temperature of the black body
         wavelengths (ndarray): An array like object containing wavelengths
         pwv           (float): The PWV concentration along line of sight in mm

     Returns:
         An array of flux values in units of ergs / (angstrom * cm2 * s)
     """

    sed = blackbody_lambda(wavelengths, temp)
    sed *= (4 * np.pi * u.sr)  # Integrate over angular coordinates

    if pwv > 0:
        transmission = transmission_pwv(pwv)
        resampled_transmission = np.interp(wavelengths,
                                           transmission['wavelength'],
                                           transmission['transmission'])

        sed *= resampled_transmission

    return sed


def magnitude(temp, band, pwv):  # Todo: specify zero point
    """Return the magnitude of a black body with and without pwv absorption

    Magnitudes are calculated relative to a zero point of 3631 Jy

    Args:
        temp (float): The temperature of the desired black body
        band (tuple): Tuple with the beginning and end wavelengths of the
                       desired band in angstroms
        pwv  (float): The PWV concentration along line of sight in mm

    Returns:
        The magnitude of the desired black body WITHOUT H2O absorption
        The magnitude of the desired black body WITH H2O absorption
    """

    wavelengths = np.arange(band[0], band[1])
    lambda_over_c = (np.median(band) * u.AA) / c

    flux = sed(temp, wavelengths, 0)
    flux *= lambda_over_c.cgs

    flux_pwv = sed(temp, wavelengths, pwv)
    flux_pwv *= lambda_over_c.cgs

    zero_point = (3631 * u.jansky).to(u.erg / u.cm ** 2)
    int_flux = np.trapz(x=wavelengths, y=flux) * u.AA
    int_flux_transm = np.trapz(x=wavelengths, y=flux_pwv) * u.AA

    magnitude = -2.5 * np.log10(int_flux / zero_point)
    magnitude_transm = -2.5 * np.log10(int_flux_transm / zero_point)

    return magnitude.value, magnitude_transm.value


def zp_bias(ref_temp, cal_temp, band, pwv):
    """Calculate the residual error in the photometric zero point due to PWV

    Using a black body approximation, calculate the residual error in the zero
    point of a photometric image cause by not considering the PWV transmission
    function.

    Args:
        ref_temp (float): The temperature of a star used to calibrate the image
        cal_temp (float): The temperature of another star in the same image to
                           calculate the error for
        band     (tuple): Tuple specifying the beginning and end points
                           of the desired band in angstroms
        pwv      (float): The PWV concentration along line of sight

    Returns:
        The residual error in the second star's magnitude
    """

    # Values for reference star
    ref_mag, ref_mag_atm = magnitude(ref_temp, band, pwv)
    ref_zero_point = ref_mag - ref_mag_atm

    # Values for star being calibrated
    cal_mag, cal_mag_atm = magnitude(cal_temp, band, pwv)
    cal_zero_point = cal_mag - cal_mag_atm

    bias = cal_zero_point - ref_zero_point
    return bias
