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


"""Tests for the ``pwv_kpno.gps_pwv.GPSReceiver`` class"""

from unittest import TestCase, skip

from pwv_kpno.gps_pwv import GPSReceiver


class SetupMixin:

    def setUp(self):
        """Create a mock pwv model for testing"""

        self.primary = 'REC1'
        self.data_cuts = {'PWV': [(2, 8)]}
        self.receiver = GPSReceiver(self.primary, self.data_cuts, cache_data=True)


# noinspection PyPropertyAccess
class ReceiverIdUppercase(SetupMixin, TestCase):

    def test_id_is_uppercase(self):
        """Test receivers are stored in uppercase"""

        receiver = GPSReceiver('rec1')
        self.assertTrue(receiver.rec_id.isupper(), 'Receiver Id is not uppercase.')

    def test_id_non_muatable(self):
        receiver = GPSReceiver('rec1')
        with self.assertRaises(AttributeError):
            receiver.rec_id = 'rec2'


class CacheClearing(SetupMixin, TestCase):

    def test_clear_raises_error_when_cache_disabled(self):
        self.receiver.cache_data = False
        with self.assertRaises(RuntimeError):
            self.receiver.clear_cache()

    def test_cache_is_cleared(self):
        self.receiver._cache = True  # Assign anything that isn't None
        self.receiver.clear_cache()
        self.assertIsNone(self.receiver._cache, 'Cache was not reset to None')


@skip
# @TestWithCleanEnv(TEST_DATA_DIR)
class LoadRecDirectory(TestCase):
    """Tests for the ``load_rec_data`` function"""

    def test_empty_dataframe_columns(self):
        """Test returned DataFrame has correct column names"""

        # Use a fake receiver Id should return an empty dataframe
        data = load_rec_data('dummy_receiver')
        expected_columns = ['PWV, PWVErr', 'ZenithDelay', 'SrfcPress', 'SrfcTemp', 'SrfcRH']
        self.assertListEqual(expected_columns, list(data.columns))

    def test_empty_dataframe_index(self):
        """Test the returned DataFrame is indexed by ``date``"""

        # Use a fake receiver Id should return an empty dataframe
        data = load_rec_data('dummy_receiver')
        self.assertEqual('date', data.index.name)

    def test_warns_on_empty_data(self):
        """Test a warning is raised for an empty data frame"""

        with self.assertWarns(Warning):
            load_rec_data('dummy_receiver')

    def test_expected_years_are_parsed(self):
        """Test data is returned from all available data files for a given receiver"""

        azam_data = load_rec_data('AZAM')
        self.assertEqual(2015, azam_data.index.min().year, '2015 data missing from return')
        self.assertEqual(2016, azam_data.index.max().year, '2016 data missing from return')
