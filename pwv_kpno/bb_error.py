#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""This module provides functions for calculating values relevant to a black
body.
"""

import os
import warnings

from astropy import units as u
from astropy.modeling.blackbody import blackbody_lambda
from astropy.constants import c
from astropy.utils.exceptions import AstropyDeprecationWarning
from astropy.table import Table
import numpy as np

import pwv_kpno

FILE_DIR = os.path.dirname(os.path.realpath(__file__))
PWV_MODEL_PATH = os.path.join(FILE_DIR, 'locations/{}/modeled_pwv.csv')


def _black_body_sed(wavelengths, temp):
    """For provided wavelengths, return the corresponding flux of a black body

     Flux is returned in units of ergs / (s * angstrom * cm2 * sr)

     Args:
         wavelengths (ndarray): An array like object containing wavelengths
         temp          (float): The desired temperature of the black body

     Returns:
         An array of flux values in units of ergs / (s * angstrom * cm2 * sr)
     """

    with np.errstate(all='ignore'):
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', AstropyDeprecationWarning)
            return blackbody_lambda(wavelengths, temp)


def _black_body_mag(temp, transmission, band):
    """For a given band and temperature, returns the magnitude of a black body

    Args:
        temp         (float): The temperature of the desired black body
        transmission (Table): A table of atm transmission values per wavelength
        band         (tuple): Tuple specifying the beginning and end points
                               of the desired band in angstroms

    Returns:
        The magnitude of the desired black body WITHOUT H2O absorption
        The magnitude of the desired black body WITH H2O absorption
    """

    wavelengths = np.arange(band[0], band[1])
    resampled_transmission = np.interp(wavelengths,
                                       transmission['wavelength'],
                                       transmission['transmission'])

    lambda_over_c = (np.median(band) * u.AA).cgs / c.cgs
    flux = _black_body_sed(wavelengths, temp)
    flux *= (4 * np.pi * u.sr) * lambda_over_c
    flux_trasm = flux * resampled_transmission

    zero_point = (3631 * u.jansky).to(u.erg / u.cm ** 2)
    int_flux = np.trapz(x=wavelengths, y=flux) * u.AA
    int_flux_transm = np.trapz(x=wavelengths, y=flux_trasm) * u.AA

    magnitude = -2.5 * np.log10(int_flux / zero_point)
    magnitude_transm = -2.5 * np.log10(int_flux_transm / zero_point)

    return magnitude.value, magnitude_transm.value


def zp_bias_pwv(ref_temp, cal_temp, band, pwv):
    """Calculate the residual error in the zero point due to PWV

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

    atm_trans = pwv_kpno.transmission_pwv(pwv)

    min_lambda = atm_trans['wavelength'][0]
    max_lambda = atm_trans['wavelength'][-1]
    if band[0] < min_lambda or band[1] < max_lambda:
        msg = 'Wavelength range ({}, {}) out of bounds ({}, {})'
        raise ValueError(msg.format(band[0], band[1], min_lambda, max_lambda))

    # Values for reference star
    ref_mag, ref_mag_atm = _black_body_mag(ref_temp, atm_trans, band)
    ref_zero_point = ref_mag - ref_mag_atm

    # Values for star being calibrated
    cal_mag, cal_mag_atm = _black_body_mag(cal_temp, atm_trans, band)
    cal_zero_point = cal_mag - cal_mag_atm

    bias = cal_zero_point - ref_zero_point
    return bias


def zp_bias(ref_temp, cal_temp, band, date, airmass):
    """Calculate the residual error in the zero point due to PWV

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

    location_name = pwv_kpno.settings.Settings().current_location.name
    pwv_model = Table.read(PWV_MODEL_PATH.format(location_name))

    # Determine the PWV level along line of sight as pwv(zenith) * airmass
    timestamp = pwv_kpno.calc_transmission._timestamp(date)
    pwv = np.interp(timestamp, pwv_model['date'], pwv_model['pwv']) * airmass

    return zp_bias_pwv(ref_temp, cal_temp, band, pwv)
