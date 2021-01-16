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


"""Tests for top level functions of the ``pwv_kpno.transmission`` module"""

from unittest import TestCase

import numpy as np
import pandas as pd

from pwv_kpno.transmission import bin_transmission, calc_pwv_eff, calc_pwv_los


class CalcPWVEff(TestCase):
    """Tests for the ``calc_pwv_eff`` function"""

    def test_pwv_1_exp_1(self):
        """Test the return is the same as the input for norm_pwv = exp = 1"""

        test_val = 16
        self.assertEqual(test_val, calc_pwv_eff(test_val, 1, 1))

    def test_pwv_los_2(self):
        """Default arguments should be such that PWV Eff is 1 when PWV los is 2"""

        self.assertEqual(1, calc_pwv_eff(2))

    @staticmethod
    def test_array_support():
        """Test function executes successfully for list arguments"""

        test_args = [1, 2]
        expected_returns = [calc_pwv_eff(p) for p in test_args]
        np.testing.assert_equal(expected_returns, calc_pwv_eff([1, 2]))


class CalcPWVLos(TestCase):
    """Tests for the ``calc_pwv_los`` function"""

    @staticmethod
    def test_is_inverse_of_calc_pwv_eff():
        """Test the function is the inverse of ``calc_pwv_los``"""

        test_pwv_los = 4
        np.testing.assert_approx_equal(
            test_pwv_los, calc_pwv_los(calc_pwv_eff(test_pwv_los)))

    @staticmethod
    def test_array_support():
        """Test function executes successfully for list arguments"""

        test_args = [1, 2]
        expected_returns = [calc_pwv_los(p) for p in test_args]
        np.testing.assert_equal(expected_returns, calc_pwv_los([1, 2]))


class BinTransmission(TestCase):
    """Tests for the ``_bin_transmission`` function"""

    def setUp(self) -> None:
        """Create Pandas Series representing dummy transmission values"""

        self.resolution = 3  # Resolution to test at
        self.test_transmission = pd.Series(1, index=np.arange(10))

    def test_returned_wavelengths_match_resolution(self):
        """Test returned wavelength values match expected wavelengths for the given resolution"""

        # Get binned wavelengths from tested function

        binned_wavelengths = bin_transmission(self.test_transmission, self.resolution).index.values

        # Calculated expected wavelengths
        expected_wavelengths = np.arange(
            self.test_transmission.index.min() + self.resolution / 2,
            self.test_transmission.index.max(),
            self.resolution)

        # noinspection PyTypeChecker
        np.testing.assert_equal(expected_wavelengths, binned_wavelengths)

    def test_wave_kwarg_override(self):
        """Test the ``wave`` argument overrides the use of ``transmission.index``"""

        # Get binned wavelengths from tested function
        wave = self.test_transmission.index + 100
        binned_wavelengths = bin_transmission(self.test_transmission, self.resolution, wave=wave).index.values

        # Calculated expected wavelengths
        # noinspection PyArgumentList
        expected_wavelengths = np.arange(
            wave.min() + self.resolution / 2,
            wave.max(),
            self.resolution)

        # noinspection PyTypeChecker
        np.testing.assert_equal(expected_wavelengths, binned_wavelengths)

    def test_requested_resolution_higher_than_sampling(self):
        """Test a ValueError is raised when binning at a resolution above the sampled transmission values"""

        with self.assertRaises(ValueError):
            bin_transmission(self.test_transmission, resolution=.01)
