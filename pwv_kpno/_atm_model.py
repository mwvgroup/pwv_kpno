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

import os

import numpy as np
import scipy.interpolate as interpolate
from astropy.table import Table

__authors__ = ['Daniel Perrefort']
__copyright__ = 'Copyright 2016, Daniel Perrefort'
__credits__ = ['Azalee Bostroem']

__license__ = 'GPL V3'
__email__ = 'djperrefort@pitt.com'
__status__ = 'Development'


def calc_num_density_conversion():
    """Calculate conversion factor from PWV to integrated number density

    Returns:
        The conversion factor from PWV to number density in 1 / (mm * cm^2)
    """

    # Todo: Create an analogous function for 02, 03, and aerosols

    n_a = 6.02214129E23       # 1 / mol (Avogadro's constant)
    h2o_molar_mass = 18.0152  # g / mol
    h2o_density = 0.99997     # g / cm^3
    one_mm_in_cm = 10         # mm / cm

    # Conversion factor 1 / (mm * cm^2)
    mm_to_num_dens = (n_a * h2o_density) / (h2o_molar_mass * one_mm_in_cm)

    return mm_to_num_dens


def create_pwv_atm_model(mod_lambda, mod_cs, out_lambda):
    """Creates a table of conversion factors from PWV to number density

    Expects input and output wavelengths to be in same units. Expects modeled
    cross sections to be in cm^2.

    Args:
        mod_lambda (ndarray): Array of input wavelengths
        mod_cs     (ndarray): Array of cross sections for each input wavelength
        out_lambda (ndarray): Array of desired output wavelengths

    Returns:
        A table with columns 'wavelength' and 'mm_cm_2'
    """

    # Todo: Add contribution from 02, 03, and aerosols to this function

    if not np.array_equal(mod_lambda, out_lambda):
        interp_cs = interpolate.interp1d(mod_lambda, mod_cs)
        out_cs = interp_cs(out_lambda)

    else:
        out_cs = mod_cs

    pwv_num_density = out_cs * calc_num_density_conversion()
    out_table = Table([out_lambda, pwv_num_density],
                      names=['wavelength', 'mm_cm_2'])

    return out_table


if __name__ == '__main__':

    from pwv_kpno._settings import settings

    # Load modeled wavelengths and cross sections
    h2o_cs_path = os.path.join(settings._loc_dir, 'atmosphere/h2ocs.txt')
    cs_data = np.loadtxt(h2o_cs_path, usecols=[0, 1]).transpose()

    model_cs = cs_data[1]
    model_lambda = cs_data[0] * 10000  # convert from microns to angstroms
    output_lambda = np.arange(3000., 12001., 1)  # Angstroms
    transmission = create_pwv_atm_model(model_lambda, model_cs, output_lambda)

    transmission.write(settings._atm_model_path, overwrite=True)
