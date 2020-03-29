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

import numpy as np
import scipy.interpolate as interpolate
from astropy.table import Table


def _calc_num_density_conversion():
    """Calculate conversion factor from PWV * cross section to optical depth

    Returns:
        The conversion factor in units of 1 / (mm * cm^2)
    """

    n_a = 6.02214129E23  # 1 / mol (Avogadro's constant)
    h2o_molar_mass = 18.0152  # g / mol
    h2o_density = 0.99997  # g / cm^3
    one_mm_in_cm = 10  # mm / cm

    # Conversion factor 1 / (mm * cm^2)
    mm_to_num_dens = (n_a * h2o_density) / (h2o_molar_mass * one_mm_in_cm)

    return mm_to_num_dens


def create_pwv_atm_model(
        model_lambda: np.ndarray,
        model_cs: np.ndarray,
        out_lambda: np.ndarray) -> Table:
    """Creates a table of conversion factors from PWV to optical depth

    Expects input and output wavelengths to be in same units. Expects modeled
    cross sections to be in cm^2.

    Args:
        model_lambda: Array of input wavelengths
        model_cs: Array of cross sections for each input wavelength
        out_lambda: Array of desired output wavelengths

    Returns:
        A table with columns 'wavelength' and '1/mm'
    """

    model_cs = np.array(model_cs)  # Just in case we are passed a list
    if (model_cs < 0).any():
        raise ValueError('Cross sections cannot be negative.')

    if np.array_equal(model_lambda, out_lambda):
        out_cs = model_cs  # This function requires ndarray behavior

    else:
        interp_cs = interpolate.interp1d(model_lambda, model_cs)
        out_cs = interp_cs(out_lambda)

    pwv_num_density = out_cs * _calc_num_density_conversion()
    out_table = Table(
        data=[out_lambda, pwv_num_density],
        names=['wavelength', '1/mm']
    )

    return out_table
