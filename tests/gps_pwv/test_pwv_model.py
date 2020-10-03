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


"""Tests for the ``pwv_kpno.gps_pwv.PWVModel`` class"""

from unittest import TestCase

import numpy as np
import pandas as pd

from pwv_kpno.gps_pwv import PWVModel, GPSReceiver


# noinspection PyPropertyAccess
class ReceiverIdHandling(TestCase):
    """Test related to the access and formatting of receiver Id's"""

    def setUp(self):
        """Create a mock pwv model for testing"""

        self.primary = GPSReceiver('REC1')
        self.secondaries = [GPSReceiver('REC2'), GPSReceiver('REC3')]
        self.model = PWVModel(self.primary, self.secondaries)

    def test_primary_rec_not_settable(self):
        """Test the ``primary`` attribute has no setter"""

        with self.assertRaises(AttributeError):
            self.model.primary = GPSReceiver('NEW_PRIMARY')

    def test_secondary_recs_not_settable(self):
        """Test the ``secondaries`` attribute has no setter"""

        with self.assertRaises(AttributeError):
            self.model.secondaries = [GPSReceiver('NEW_REC_1')]


class FitToSecondary(TestCase):
    """Tests for the _fit_to_secondary`` function"""

    @staticmethod
    def test_fit_recovers_simulated_data():
        """Test fit recovers simulated data"""

        # If the secondary data is a subset of the primary data, the
        # fit should recover the secondary data
        secondary = pd.DataFrame({
            'PWV': np.arange(0., 10.),
            'PWVErr': np.full(10, .1)
        })
        primary = secondary.iloc[0:8].copy()

        applied_fit, errors = PWVModel._fit_primary_to_secondary(primary, secondary)
        pd.testing.assert_series_equal(applied_fit, secondary.PWV)


class Repr(TestCase):
    """Tests for the string representation of ``PWVModel``"""

    def test_can_be_evaluated(self):
        """Test the class representation can be evaluated"""

        primary = GPSReceiver('PRIM')
        secondaries = [GPSReceiver('SEC1'), GPSReceiver('SEC2')]
        eval(repr(PWVModel(primary, secondaries)))