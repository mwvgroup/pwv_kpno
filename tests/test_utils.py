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

import warnings
from datetime import datetime
from pathlib import Path
from unittest import TestCase

import numpy as np
import pandas as pd

# noinspection PyProtectedMember
from pwv_kpno._utils import apply_data_cuts, linear_regression, search_data_table
from tests.wrappers import TestWithCleanEnv

TEST_DATA_DIR = Path(__file__).parent.parent / 'testing_data'


class ApplyDataCuts(TestCase):
    """Tests for ``apply_data_cuts``"""

    def setUp(self):
        self.test_data = pd.DataFrame({'PWV': np.arange(0, 10)})
        self.data_cuts = {'PWV': [(4, 8)]}

    def test_data_is_cut(self):
        """Test returned data satisfies data cuts"""

        cut_data = apply_data_cuts(self.test_data, self.data_cuts)
        is_within_bounds = (4 <= cut_data.PWV) & (cut_data.PWV <= 8)
        self.assertTrue(is_within_bounds.all())

    def test_empty_data(self):
        """Test an error is not raised when the dataframe is empty"""

        apply_data_cuts(pd.DataFrame({'PWV': []}), self.data_cuts)

    def test_empty_datacuts(self):
        """Test the original data is returned if datacuts is an empty dict"""

        cut_data = apply_data_cuts(self.test_data.copy(), dict())
        pd.testing.assert_frame_equal(cut_data, self.test_data)


class LinearRegression(TestCase):
    """Tests for the ``linear_regression`` function"""

    @staticmethod
    def test_empty_data():
        """Test the fit will not raise an error or warning for empty data"""

        with warnings.catch_warnings():
            warnings.filterwarnings('error')
            linear_regression([], [], [], [])

    @staticmethod
    def test_fit_recovers_linear_parameters():
        """Test the linear regression recovers fit parameters from mock data"""

        sim_params = np.array([10, 2])
        x = np.arange(1, 10)
        y = sim_params[1] * x + sim_params[0]
        fit_result = linear_regression(x=x, y=y, sx=.1 * x, sy=.1 * y)
        np.testing.assert_array_almost_equal(fit_result.beta, sim_params)


class SearchDataTables(TestCase):
    """Tests for ``search_data_table``"""

    def setUp(self) -> None:
        self.test_data = pd.DataFrame(
            {'PWV': [1, 2, 3]},
            index=[datetime(2015, 1, 1), datetime(2015, 2, 2), datetime(2017, 3, 3)])

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
