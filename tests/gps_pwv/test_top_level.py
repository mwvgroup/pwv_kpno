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


"""Tests for top level functions of the ``gps_pwv`` module"""

from datetime import datetime
from pathlib import Path
from unittest import TestCase

import pandas as pd

from pwv_kpno.gps_pwv import load_rec_data, search_data_table
from tests.utils import TestWithCleanEnv

TEST_DATA_DIR = Path(__file__).parent.parent / 'testing_data'


def create_test_data():
    return pd.DataFrame(
        {'PWV': [1, 2, 3]},
        index=[datetime(2015, 1, 1), datetime(2015, 2, 2), datetime(2017, 3, 3)])


class ApplyDataCuts(TestCase):
    """Tests for ``apply_data_cuts``"""

    def setUp(self) -> None:
        self.test_data = create_test_data()


class SearchDataTables(TestCase):
    """Tests for ``search_data_table``"""

    def setUp(self) -> None:
        self.test_data = create_test_data()

    def test_raises_for_invalid_month(self):
        """Test for ValueError is raised for bad ``month`` argument"""

        err_msg = 'No error raised for month {}'
        for bad_month in [-3, 0, 13]:
            with self.assertRaises(ValueError, msg=err_msg.format(bad_month)):
                search_data_table(self.test_data, month=bad_month)

    def test_raises_for_invalid_day(self):
        """Test for ValueError is raised for bad ``day`` argument"""

        err_msg = 'No error raised for day {}'
        for bad_day in [-3, 0, 32]:
            with self.assertRaises(ValueError, msg=err_msg.format(bad_day)):
                search_data_table(self.test_data, day=bad_day)

    def test_raises_for_invalid_hour(self):
        """Test for ValueError is raised for bad ``hour`` argument"""

        err_msg = 'No error raised for hour {}'
        for bad_hour in [-3, 24, 30]:
            with self.assertRaises(ValueError, msg=err_msg.format(bad_hour)):
                search_data_table(self.test_data, hour=bad_hour)

    def test_filter_by_year(self):
        """Test searched table only includes searched for years"""

        test_year = 2015
        searched_years = search_data_table(self.test_data, year=test_year).index.year
        self.assertTrue((searched_years == test_year).all())

    def test_now_kwargs_returns_passed_df(self):
        """Test the original dataframe is returned when no kwargs are specified"""

        pd.testing.assert_frame_equal(self.test_data, search_data_table(self.test_data))


@TestWithCleanEnv(TEST_DATA_DIR)
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
