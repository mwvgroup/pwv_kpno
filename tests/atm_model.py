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

"""This file provides tests for the creation of atmospheric models using

Primary tested modules:
    pwv_kpno.atm_model module.
"""

from unittest import TestCase

import numpy as np

from pwv_kpno._atm_model import _calc_num_density_conversion
from pwv_kpno._atm_model import create_pwv_atm_model

__authors__ = ['Daniel Perrefort']
__copyright__ = 'Copyright 2017, Daniel Perrefort'

__license__ = 'GPL V3'
__email__ = 'djperrefort@pitt.edu'
__status__ = 'Development'


# Todo: add docstring
class CreatePWVModel(TestCase):
    """Tests for pwv_kpno.atm_model.create_pwv_atm_model"""

    def setUp(self):
        """Create a model for conversion from mm of PWV to atm cross section"""

        self.mock_cross_sections = np.array([0, .5, 1])
        self.mock_lambda_in = np.array([0, 5, 10])
        self.mock_lambda_out = np.array([0, 2.5, 5, 7.5, 10])

        self.mock_model = create_pwv_atm_model(
            self.mock_lambda_in,
            self.mock_cross_sections,
            self.mock_lambda_out
        )

    def test_zero_cross_section(self):
        self.assertEqual(self.mock_model['1/mm_cm_2'][0], 0)

    def test_cs_equal_one(self):
        conv_factor = _calc_num_density_conversion()
        self.assertEqual(self.mock_model['1/mm_cm_2'][-1], conv_factor)

    def test_returned_wavelengths(self):
        eq = np.array_equal(self.mock_model['wavelength'],
                            self.mock_lambda_out)

        self.assertTrue(eq)

    def test_interpolation(self):
        pass
