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

from unittest import TestCase

from pwv_kpno.gps_pwv import GPSReceiver
from tests.wrappers import TestWithCleanEnv, TEST_DATA_DIR


class SetupMixin:
    """Creates a dummy ``GPSReceiver`` object for testing"""

    def setUp(self):
        """Create a mock pwv model for testing"""

        self.primary = 'KITT'
        self.data_cuts = {'PWV': [(2, 8)]}
        self.receiver = GPSReceiver(self.primary, self.data_cuts, cache_data=True)


# noinspection PyPropertyAccess
class ReceiverId(SetupMixin, TestCase):
    """Test accessibility and formatting of the ``receiver_id`` attribute"""

    def test_id_is_uppercase(self):
        """Test receiver Id is forced to be uppercase"""

        receiver = GPSReceiver('rec1')
        self.assertTrue(receiver.receiver_id.isupper(), 'Receiver Id is not uppercase.')

    def test_receiver_id_non_muatable(self):
        """Test the ``receiver_id`` object is not settable"""

        with self.assertRaises(AttributeError):
            self.receiver.receiver_id = 'rec2'


class CacheClearing(SetupMixin, TestCase):
    """Test that various methods clear cached data from memory"""

    def test_clear_raises_error_when_cache_disabled(self):
        """Test an error is thrown when clearing the cache with caching disabled"""

        self.receiver.cache_data = False
        with self.assertRaises(RuntimeError):
            self.receiver.clear_cache()

    def test_clear_cache_func(self):
        """Test the ``clear_cache`` function resets the class' cache"""

        self.receiver._cache = True  # Assign anything that isn't None
        self.receiver.clear_cache()
        self.assertIsNone(self.receiver._cache, 'Cache was not reset to None')

    def test_cache_data_attr(self):
        """Test setting the ``cache_data`` attribute resets the class' cache"""

        self.receiver._cache = True  # Assign anything that isn't None
        self.receiver.cache_data = False
        self.assertIsNone(self.receiver._cache, 'Cache was not reset to None')

    def test_data_cuts_attr(self):
        """Test setting the ``data_cuts`` attribute resets the class' cache"""

        self.receiver._cache = True  # Assign anything that isn't None
        self.receiver.data_cuts = dict()
        self.assertIsNone(self.receiver._cache, 'Cache was not reset to None')


@TestWithCleanEnv(TEST_DATA_DIR)
class LoadRecDirectory(SetupMixin, TestCase):
    """Tests for the ``load_rec_data`` function"""

    def test_empty_dataframe_columns(self):
        """Test returned DataFrame has correct column names"""

        # Use a fake receiver Id should return an empty dataframe
        data = self.receiver._load_rec_data()
        expected_columns = ['PWV', 'PWVErr', 'ZenithDelay', 'SrfcPress', 'SrfcTemp', 'SrfcRH']
        self.assertListEqual(expected_columns, list(data.columns))

    def test_empty_dataframe_index(self):
        """Test the returned DataFrame is indexed by ``date``"""

        # Use a fake receiver Id should return an empty dataframe
        data = self.receiver._load_rec_data()
        self.assertEqual('date', data.index.name)

    def test_warns_on_empty_data(self):
        """Test a warning is raised for an empty data frame"""

        receiver = GPSReceiver('dummy_receiver')
        with self.assertWarns(Warning):
            receiver._load_rec_data()

    def test_expected_years_are_parsed(self):
        """Test data is returned from all available data files for a given receiver"""

        azam_data = GPSReceiver('AZAM').weather_data()
        self.assertEqual(2015, azam_data.index.min().year, '2015 data missing from return')
        self.assertEqual(2016, azam_data.index.max().year, '2016 data missing from return')


class Repr(TestCase):
    """Tests for the string representation of ``URLDownloader``"""

    def test_can_be_evaluated(self):
        """Test the class representation can be evaluated"""

        test_class = GPSReceiver('TESTID', data_cuts={'PWV': [(1, 2)]}, cache_data=False)
        new_class = eval(repr(test_class))
        self.assertEqual(new_class.receiver_id, test_class.receiver_id)
        self.assertEqual(new_class.data_cuts, test_class.data_cuts)
        self.assertEqual(new_class.cache_data, test_class.cache_data)
