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


"""Tests for the ``gps_pwv`` module"""

from datetime import datetime
from pathlib import Path
from unittest import TestCase

import numpy as np

from pwv_kpno.gps_pwv import _search_data_table, GPSReceiver
from tests.utils import TestWithCleanEnv

TEST_DATA_DIR = Path(__file__).parent / 'testing_data'


class TableSearchingErrors(TestCase):
    """Test that _check_date_time_args raises the appropriate errors

    _check_date_time_args is responsible for checking the arguments for both
    pwv_kpno.pwv_atm.measured_pwv and pwv_kpno.pwv_atm.modeled_pwv"""

    def test_raises_for_invalid_year(self):
        """Test for correct errors due to bad year argument"""

        next_year = datetime.now().year + 1
        self.assertRaises(ValueError, _search_data_table, year=next_year)

    def test_raises_for_invalid_month(self):
        """Test for ValueError is raised for bad ``month`` argument"""

        err_msg = 'No error raised for month {}'
        for bad_month in [-3, 0, 13]:
            self.assertRaises(
                ValueError, _search_data_table, month=bad_month,
                msg=err_msg.format(bad_month))

    def test_raises_for_invalid_day(self):
        """Test for ValueError is raised for bad ``day`` argument"""

        err_msg = 'No error raised for day {}'
        for bad_day in [-3, 0, 32]:
            self.assertRaises(
                ValueError, _search_data_table, day=bad_day,
                msg=err_msg.format(bad_day))

    def test_raises_for_invalid_hour(self):
        """Test for ValueError is raised for bad ``hour`` argument"""

        err_msg = 'No error raised for hour {}'
        for bad_hour in [-3, 24, 30]:
            self.assertRaises(
                ValueError, _search_data_table, hour=bad_hour,
                msg=err_msg.format(bad_hour))


class AttributesAreAccessible(TestCase):
    """Test receiver values for the ``GPSReceiver`` are get/settable"""

    def setUp(self):
        self.primary = 'REC1'
        self.secondaries = ('REC2', 'REC3')
        self.receiver = GPSReceiver(primary=self.primary, secondaries=self.secondaries)

    def test_primary_rec_accessible(self):
        """Test the primary receiver is accessible through the
        ``primary`` attribute
        """

        self.assertEqual(self.primary, self.receiver.primary)

    def test_primary_rec_is_settable(self):
        """Test the ``primary`` attribute has a setter"""

        new_primary = 'new_primary'
        self.receiver.primary = new_primary
        self.assertEqual(new_primary, self.receiver.primary)

    def test_secondary_recs_accessible(self):
        """Test the secondary receivers are accessible through the
        ``secondaries`` attribute
        """

        self.assertEqual(self.secondaries, self.receiver.secondaries)

    def test_secondary_recs_are_settable(self):
        """Test the ``secondaries`` attribute has a setter"""

        new_secondaries = ('dummy1', 'dummy2')
        self.receiver.secondaries = new_secondaries
        self.assertEqual(new_secondaries, self.receiver.secondaries)


@TestWithCleanEnv(TEST_DATA_DIR)
class ModeledPWV(TestCase):
    """Tests for the 'GPSReceiver.modeled_pwv' function"""

    def setUp(self):
        self.receiver = GPSReceiver('KITT')

    def test_returned_column_names(self):
        """Test returned table has two columns named ``date`` and the
        primary receiver Id
        """

        returned_column_order = self.receiver.modeled_pwv().colnames
        expected_col_order = ['date', self.receiver.primary]
        self.assertListEqual(expected_col_order, returned_column_order)

    def test_filtering_by_args(self):
        """Test returned dates are filtered by kwarg arguments"""

        search_kwargs = {'year': 2010, 'month': 7, 'day': 21, 'hour': 5}
        full_table = self.receiver.modeled_pwv()
        searched_table = _search_data_table(full_table, **search_kwargs)
        returned_table = self.receiver.modeled_pwv(**search_kwargs)
        self.assertEqual(searched_table, returned_table)

    def test_units(self):
        """Test columns for appropriate units"""

        expected_units = {'date': 'UTC', self.receiver.primary: 'mm'}
        data_table = self.receiver.modeled_pwv()
        for column, unit in expected_units.items():
            self.assertEqual(unit, data_table[column].unit)


@TestWithCleanEnv(TEST_DATA_DIR)
class WeatherData(TestCase):
    """Tests for the ``GPSReceiver.weather_data`` function"""

    def setUp(self):
        self.receiver = GPSReceiver('KITT')

    def test_returned_column_names(self):
        """Test returned table has two columns named ``date`` and the
        primary receiver Id
        """

        returned_column_order = self.receiver.weather_data().colnames
        expected_col_order = ['date', 'pwv', 'temperature', 'pressure', 'humidity']
        self.assertListEqual(expected_col_order, returned_column_order)

    def test_filtering_by_args(self):
        """Test returned dates are filtered by kwarg arguments"""

        search_kwargs = {'year': 2010, 'month': 7, 'day': 21, 'hour': 5}
        full_table = self.receiver.weather_data()
        searched_table = _search_data_table(full_table, **search_kwargs)
        returned_table = self.receiver.weather_data(**search_kwargs)
        self.assertEqual(searched_table, returned_table)

    def test_units(self):
        """Test columns for appropriate units"""

        expected_units = {'date': 'UTC', 'pwv': 'mm', 'temperature': 'k',
                          'pressure': 'bar', 'humidity': '%'}

        data_table = self.receiver.weather_data()
        for column, unit in expected_units.items():
            self.assertEqual(unit, data_table[column].unit)


class PWVDateInterpolation(TestCase):
    """Tests for the ``GPSReceiver.interp_pwv_date`` function"""

    def setUp(self):
        self.receiver = GPSReceiver('KITT')

    def test_error_for_out_of_bounds(self):
        """Test a value error is raised when interpolating for an out of bounds date"""

        max_date = max(self.receiver.modeled_pwv()['date'])
        out_of_bounds_date = max_date + 1
        self.assertRaises(ValueError, self.receiver.interp_pwv_date, out_of_bounds_date)

    def test_error_for_no_nearby_data(self):
        """Test an error is raised if no modeled PWV values are available
        within a given range of the requested datetime
        """

        self.fail()

    def test_recovers_model_at_grid_points(self):
        """Test interpolation recovers grid points of the modeled PWV"""

        modeled_pwv = self.receiver.modeled_pwv()
        target_date = modeled_pwv['date'][0]
        target_pwv = modeled_pwv['pwv'][0]
        interpolated_pwv = self.receiver.interp_pwv_date(target_date)
        self.assertEqual(target_pwv, interpolated_pwv)

    def test_return_matches_linear_interpolation(self):
        """Test the returned PWV is consistent with a linear interpolation"""

        modeled_pwv = self.receiver.modeled_pwv()
        test_date = 1594467199  # July 11th, 2020
        expected_pwv = np.interp(test_date, modeled_pwv['date'], modeled_pwv['pwv'])
        returned_pwv = self.receiver.interp_pwv_date(test_date)
        self.assertEqual(expected_pwv, returned_pwv)
