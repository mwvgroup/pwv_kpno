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

"""This file tests the ``pwv_kpno.defaults`` module."""

from unittest import TestCase, skip

from pwv_kpno import transmission


class TestReceiverAvailability(TestCase):
    """Test availability of default data access objects"""

    def test_azam(self):
        """Test AZAM receiver has correct receiver Id"""

        from pwv_kpno.defaults import azam
        self.assertEqual(azam.receiver_id, 'AZAM')

    def test_ctio(self):
        """Test CTIO receiver has correct receiver Id"""

        from pwv_kpno.defaults import ctio
        self.assertEqual(ctio.receiver_id, 'CTIO')

    def test_kitt(self):
        """Test KITT receiver has correct receiver Id"""

        from pwv_kpno.defaults import kitt
        self.assertEqual(kitt.receiver_id, 'KITT')

    def test_p014(self):
        """Test P014 receiver has correct receiver Id"""

        from pwv_kpno.defaults import p014
        self.assertEqual(p014.receiver_id, 'P014')

    def test_sa46(self):
        """Test SA46 receiver has correct receiver Id"""

        from pwv_kpno.defaults import sa46
        self.assertEqual(sa46.receiver_id, 'SA46')

    def test_sa48(self):
        """Test SA48 receiver has correct receiver Id"""

        from pwv_kpno.defaults import sa48
        self.assertEqual(sa48.receiver_id, 'SA48')


class TestTransmissionModelAvailability(TestCase):
    """Test availability of default transmission models"""

    def test_v1_transmission(self):
        """Test v1 transmission is a ``CrossSectionTransmission`` instance"""

        from pwv_kpno.defaults import v1_transmission
        self.assertIsInstance(v1_transmission, transmission.CrossSection)

    @skip('V2 transmission not implemented yet')
    def test_v2_transmission(self):
        """Test v1 transmission is a ``TransmissionModel`` instance"""

        from pwv_kpno.defaults import v2_transmission
        self.assertIsInstance(v2_transmission, transmission.TransmissionModel)


class TestPWVModelAvailability(TestCase):
    """Test availability of PWV model for Kitt Peak"""

    def test_kitt_model(self):
        """Test Kitt Peak model has correct secondary receivers"""

        from pwv_kpno.defaults import kitt_model
        secondaries = [r.receiver_id for r in kitt_model.secondaries]
        expected = ('AZAM', 'P014', 'SA46', 'SA48')
        self.assertSequenceEqual(secondaries, expected)
