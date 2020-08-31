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


# noinspection PyMethodMayBeStatic
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


class TransmissionCall(TestCase):
    """Tests for the evaluation of the transmission function"""

    def setUp(self):
        # These numbers are not physical but it doesn't matter for our purpose here
        wavelengths = np.array([1000, 2000])
        self.cross_sections = np.array([2, 2])
        self.transmission = CrossSectionTransmission(wavelengths, self.cross_sections)

    def test_beer_lambert(self):
        """Test transmission values obey the Beer-Lambert law"""

        pwv = 4
        modeled_trans = self.transmission(pwv)
        beer_lambert_trans = np.exp(-pwv * self.cross_sections * CrossSectionTransmission._num_density_conversion())
        np.testing.assert_equal(modeled_trans, beer_lambert_trans)

    def test_default_wavelengths_match_init(self):
        """Test return values are index by init wavelengths by default"""

        np.testing.assert_equal(self.transmission(4).index.to_numpy(), self.transmission.samp_wave)

    def test_interpolates_for_given_wavelengths(self):
        """Test an interpolation is performed for specified wavelengths when given"""

        test_pwv = 4
        test_wave = np.arange(1000, 1500, 50)

        returned_wave = self.transmission(test_pwv, wave=test_wave).index.values
        np.testing.assert_equal(returned_wave, test_wave)

