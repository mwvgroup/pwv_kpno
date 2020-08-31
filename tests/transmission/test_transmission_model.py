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


"""Tests for the ``pwv_kpno.transmission.TransmissionModel`` class"""

from unittest import TestCase

import numpy as np

from pwv_kpno.transmission import TransmissionModel


class TransmissionCall(TestCase):
    """Tests for the evaluation of the transmission model"""

    def setUp(self):
        """Create a dummy ``Transmission`` object"""

        self.pwv = [0, 2, 4]
        wave = np.arange(1000, 2000, 100)
        sim_trans = [
            np.ones_like(wave),
            np.full_like(wave, .5),
            np.zeros_like(wave)
        ]

        self.transmission = TransmissionModel(self.pwv, wave, sim_trans)

    def test_interpolation_on_grid_point(self):
        """Test interpolation result matches sampled values at the grid points"""

        test_pwv = self.pwv[1]

        returned_trans = self.transmission(test_pwv)
        np.testing.assert_equal(self.transmission._samp_transmission[1], returned_trans)

    def test_default_wavelengths_match_init(self):
        """Test return values are index by init wavelengths by default"""

        np.testing.assert_equal(self.transmission(4).index.to_numpy(), self.transmission.samp_wave)

    def test_interpolates_for_given_wavelengths(self):
        """Test an interpolation is performed for specified wavelengths when given"""

        test_pwv = self.pwv[1]
        test_wave = np.arange(1000, 1500, 50)

        returned_wave = self.transmission(test_pwv, wave=test_wave).index.values
        np.testing.assert_equal(returned_wave, test_wave)


class IncompatibleInitArguments(TestCase):
    """Test the user is alerted at init if arguments have incompatible shapes"""

    def runTest(self):
        """Instantiate a ``TransmissionModel`` with malformed arguments"""

        with self.assertRaises(ValueError) as cm:
            TransmissionModel(
                samp_pwv=[1, 2],
                samp_wave=[100, 200],
                samp_transmission=[[1, ], [2, ]]  # Expected (2, 2) array
            )

        self.assertEqual(str(cm.exception), 'Dimensions of init arguments do not match.')


class AccessibleInitParams(TestCase):
    """Test init kwargs are accessible from instances"""

    @classmethod
    def setUpClass(cls):
        """Create a dummy ``Transmission`` object"""

        cls.samp_pwv = [0, 2, 4]
        cls.samp_wave = np.arange(1000, 2000, 100)
        cls.samp_transmission = [
            np.ones_like(cls.samp_wave),
            np.full_like(cls.samp_wave, .5),
            np.zeros_like(cls.samp_wave)
        ]

        cls.transmission = TransmissionModel(cls.samp_pwv, cls.samp_wave, cls.samp_transmission)

    def test_samp_pwv_access(self):
        """Test property access for ``samp_pwv`` init kwarg"""

        np.testing.assert_equal(self.transmission.samp_pwv, self.samp_pwv)

    def test_samp_wave_access(self):
        """Test property access for ``samp_wave`` init kwarg"""

        np.testing.assert_equal(self.transmission.samp_wave, self.samp_wave)

    def test_samp_transmission_access(self):
        """Test property access for ``samp_transmission`` init kwarg"""

        np.testing.assert_equal(self.transmission.samp_transmission, self.samp_transmission)
