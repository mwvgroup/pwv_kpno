#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

#    This file is part of the software package.
#
#    The package is free software: you can redistribute it and/or
#    modify it under the terms of the GNU General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    The package is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General
#    Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with  If not, see <http://www.gnu.org/licenses/>.

"""This file provides tests for the pwv_kpno.atm_model module."""

from unittest import TestCase

import numpy as np

from pwv_kpno._atm_model import _calc_num_density_conversion
from pwv_kpno._atm_model import create_pwv_atm_model

__authors__ = ['Daniel Perrefort']
__copyright__ = 'Copyright 2017, Daniel Perrefort'

__license__ = 'GPL V3'
__email__ = 'djperrefort@pitt.edu'
__status__ = 'Release'


def calc_conv_factor(cross_section):
    """Return the conversion factor from PWV to optical depth in units of 1/mm

    Args:
        cross_section (float): H2O cross section in units of cm^2

    Returns:
        The conversion factor from pwv to optical depth
    """

    mock_model = create_pwv_atm_model(
        mod_lambda=[0],  # Dummy value
        mod_cs=[cross_section],
        out_lambda=[0]  # Dummy value
    )

    return mock_model['1/mm'][0]


class CreatePWVModel(TestCase):
    """Tests for pwv_kpno.atm_model.create_pwv_atm_model"""

    def test_cross_section_eq_zero(self):
        """Check the The conversion factor for a cross section of zero should be zero"""

        returned_conv_factor = calc_conv_factor(0)
        self.assertEqual(returned_conv_factor, 0)

    def test_cross_section_eq_one(self):
        """The conversion factor for a cross section of zero should be zero"""

        expected_conv_factor = _calc_num_density_conversion()
        returned_conv_factor = calc_conv_factor(1)
        self.assertEqual(returned_conv_factor, expected_conv_factor)

    def test_cross_section_negative(self):
        """A negative cross section should raise a value error"""

        self.assertRaises(ValueError, calc_conv_factor, -1)

    def test_returned_wavelengths(self):
        """Returned wavelengths should match the out_lambda argument"""

        mock_cross_sections = np.array([0, .5, 1])
        mock_lambda_in = np.array([0, 5, 10])
        mock_lambda_out = np.array([0, 2.5, 5, 7.5, 10])

        mock_model = create_pwv_atm_model(
            mod_lambda=mock_lambda_in,
            mod_cs=mock_cross_sections,
            out_lambda=mock_lambda_out
        )

        arr_equals = np.array_equal(mock_model['wavelength'], mock_lambda_out)
        self.assertTrue(arr_equals)
