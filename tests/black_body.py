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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with pwv_kpno. If not, see <http://www.gnu.org/licenses/>.

"""This file tests functions related to black body modeling"""

import unittest

from astropy import units as u
from astropy.modeling.blackbody import blackbody_lambda
import numpy as np

from pwv_kpno.black_body import bias_pwv
from pwv_kpno.black_body import sed
from pwv_kpno.black_body import magnitude


class BlackbodySED(unittest.TestCase):
    """Tests for the function blackbody.sed"""

    wavelengths = np.arange(7000, 10001, 1000)  # Angstroms
    temp = 10000  # Kelvin
    pwv = 13  # mm

    def test_units(self):
        """Tests black body model for correct units"""

        modeled_sed = sed(self.temp, self.wavelengths, 13)
        sed_units = modeled_sed[0].unit
        expected_units = u.erg / (u.angstrom * u.cm * u.cm * u.s)

        msg = "Returned SED has incorrect units ({})"
        self.assertEqual(sed_units, expected_units, msg.format(sed_units))

    def test_zero_pwv(self):
        """Tests returned SED has no atmospheric features for pwv = 0"""

        returned_sed = sed(self.temp, self.wavelengths, 0)

        expected_sed = blackbody_lambda(self.wavelengths, self.temp)
        expected_sed *= (4 * np.pi * u.sr)

        sed_is_same = np.equal(returned_sed, expected_sed)
        self.assertTrue(sed_is_same,
                        "SED does not match ideal black body for pwv = 0")
