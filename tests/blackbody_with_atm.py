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
#    along with pwv_kpno. If not, see <http://www.gnu.org/licenses/>.

"""This file tests functions related to black body modeling"""

import unittest

from astropy.modeling.blackbody import blackbody_lambda
import numpy as np

from pwv_kpno.blackbody_with_atm import zp_bias
from pwv_kpno.blackbody_with_atm import sed
from pwv_kpno.blackbody_with_atm import magnitude

__authors__ = ['Daniel Perrefort']
__copyright__ = 'Copyright 2017, Daniel Perrefort'

__license__ = 'GPL V3'
__email__ = 'djperrefort@pitt.edu'
__status__ = 'Development'


class BlackbodySED(unittest.TestCase):
    """Tests for the function blackbody.sed"""

    wavelengths = np.arange(7000, 10001, 1000)  # Angstroms
    temp = 10000  # Kelvin
    pwv = 13  # Millimeters

    def test_zero_pwv(self):
        """Tests returned SED has no atmospheric features for pwv = 0"""

        returned_sed = sed(self.temp, self.wavelengths, 0)

        expected_sed = blackbody_lambda(self.wavelengths, self.temp).value

        sed_is_same = np.all(np.equal(returned_sed, expected_sed))
        self.assertTrue(sed_is_same,
                        "SED does not match ideal black body for pwv = 0")


class BlackbodyMagnitude(unittest.TestCase):
    """Tests for the function blackbody.magnitude"""

    def test_pwv_dependence(self):
        """Tests that returned magnitude increases with pwv"""

        temp = 10000  # Kelvin
        band = (7000, 8500)  # Angstroms
        test_pwv = 10  # Millimeters

        without_pwv = magnitude(temp, band, 0)
        with_pwv = magnitude(temp, band, test_pwv)
        self.assertLess(without_pwv, with_pwv,
                        "Returned magnitude does not decrease with pwv")


class ZeroPointBias(unittest.TestCase):
    """Tests for the function blackbody.zp_bias"""

    def test_same_temperature(self):
        """Tests that bias is zero for stars of same temperature"""

        msg = "Returned bias was non-zero"
        bias_3000 = zp_bias(3000, 3000, (7000, 8500), 13)
        self.assertEqual(0, bias_3000, msg)

        bias_6000 = zp_bias(6000, 6000, (8500, 10000), 13)
        self.assertEqual(0, bias_6000, msg)

        bias_10000 = zp_bias(10000, 10000, (8500, 10000), 21)
        self.assertEqual(0, bias_10000, msg)

    def test_returned_sign(self):
        """Tests that bias has expected sign"""

        msg = "Returned bias has incorrect sign"
        bias_3_6 = zp_bias(3000, 6000, (7000, 8500), 13)
        self.assertLess(0, bias_3_6, msg)

        bias_6_3 = zp_bias(6000, 3000, (7000, 8500), 13)
        self.assertGreater(0, bias_6_3, msg)
