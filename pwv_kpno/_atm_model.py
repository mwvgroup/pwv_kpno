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

"""This code calculates the wavelength dependent conversion factor from
integrated PWV column density to integrated H2O number density. It is based on
work done by Azalee Bostroem.
"""

from typing import Union

import numpy as np
import scipy.interpolate as interpolate
from astropy.table import Table

__authors__ = ['Daniel Perrefort']
__copyright__ = 'Copyright 2016, Daniel Perrefort'
__credits__ = ['Azalee Bostroem']

__license__ = 'GPL V3'
__email__ = 'djperrefort@pitt.com'
__status__ = 'Release'


def _calc_num_density_conversion():
    """Calculate conversion factor from PWV * cross section to optical depth

    Returns:
        The conversion factor in units of 1 / (mm * cm^2)
    """

    n_a = 6.02214129E23       # 1 / mol (Avogadro's constant)
    h2o_molar_mass = 18.0152  # g / mol
    h2o_density = 0.99997     # g / cm^3
    one_mm_in_cm = 10         # mm / cm

    # Conversion factor 1 / (mm * cm^2)
    mm_to_num_dens = (n_a * h2o_density) / (h2o_molar_mass * one_mm_in_cm)

    return mm_to_num_dens


def create_pwv_atm_model(mod_lambda, mod_cs, out_lambda):
    # type: (Union[list, np.ndarray], Union[list, np.ndarray], Union[list, np.ndarray]) -> Table
    """Creates a table of conversion factors from PWV to optical depth

    Expects input and output wavelengths to be in same units. Expects modeled
    cross sections to be in cm^2.

    Args:
        mod_lambda (ndarray): Array of input wavelengths
        mod_cs     (ndarray): Array of cross sections for each input wavelength
        out_lambda (ndarray): Array of desired output wavelengths

    Returns:
        A table with columns 'wavelength' and '1/mm'
    """

    mod_cs = np.array(mod_cs)
    if (mod_cs < 0).any():
        raise ValueError('Cross sections cannot be negative.')

    if np.array_equal(mod_lambda, out_lambda):
        out_cs = mod_cs  # This function requires ndarray behavior

    else:
        interp_cs = interpolate.interp1d(mod_lambda, mod_cs)
        out_cs = interp_cs(out_lambda)

    pwv_num_density = out_cs * _calc_num_density_conversion()
    out_table = Table(
        data=[out_lambda, pwv_num_density],
        names=['wavelength', '1/mm']
    )

    return out_table
