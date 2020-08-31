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


"""Tests for the ``pwv_kpno.transmission.CrossSectionTransmission`` class"""

from unittest import TestCase

import numpy as np

from pwv_kpno.transmission import CrossSectionTransmission


class PhysicalConstants(TestCase):
    """Tests for the values of physical constants used in the transmission model"""

    def test_avogadros_constant(self):
        """Test value of Avogadro's constant to three significant figures"""

        np.testing.assert_approx_equal(CrossSectionTransmission.n_a, 6.03E23, significant=3)

    def test_h2o_density(self):
        """Test value of H2O density (g / cm ** 3) to three significant figures"""

        np.testing.assert_approx_equal(CrossSectionTransmission.h2o_density, 1, significant=3)

    def test_h2o_molar_mass(self):
        """Test value of H2O molar mass (g / mol) to three significant figures"""

        np.testing.assert_approx_equal(CrossSectionTransmission.h2o_molar_mass, 18, significant=3)

    def test_num_density_conversion(self):
        """Test the value of the optical depth conversion value to three significant figures"""
        conversion = CrossSectionTransmission._num_density_conversion()
        np.testing.assert_approx_equal(conversion, 3.34e+21, significant=3)

    def test_one_mm_in_cm(self):
        """Test exact value of one mm in cm"""

        self.assertEqual(CrossSectionTransmission.one_mm_in_cm, 10)
