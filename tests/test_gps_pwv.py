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

from pwv_kpno.gps_pwv import search_data_table

TEST_DATA_DIR = Path(__file__).parent / 'testing_data'


class TableSearchingErrors(TestCase):
    """Test that _check_date_time_args raises the appropriate errors

    _check_date_time_args is responsible for checking the arguments for both
    pwv_kpno.pwv_atm.measured_pwv and pwv_kpno.pwv_atm.modeled_pwv"""

    def test_raises_for_invalid_year(self):
        """Test for correct errors due to bad year argument"""

        next_year = datetime.now().year + 1
        self.assertRaises(ValueError, search_data_table, year=next_year)

    def test_raises_for_invalid_month(self):
        """Test for ValueError is raised for bad ``month`` argument"""

        err_msg = 'No error raised for month {}'
        for bad_month in [-3, 0, 13]:
            self.assertRaises(
                ValueError, search_data_table, month=bad_month,
                msg=err_msg.format(bad_month))

    def test_raises_for_invalid_day(self):
        """Test for ValueError is raised for bad ``day`` argument"""

        err_msg = 'No error raised for day {}'
        for bad_day in [-3, 0, 32]:
            self.assertRaises(
                ValueError, search_data_table, day=bad_day,
                msg=err_msg.format(bad_day))

    def test_raises_for_invalid_hour(self):
        """Test for ValueError is raised for bad ``hour`` argument"""

        err_msg = 'No error raised for hour {}'
        for bad_hour in [-3, 24, 30]:
            self.assertRaises(
                ValueError, search_data_table, hour=bad_hour,
                msg=err_msg.format(bad_hour))
