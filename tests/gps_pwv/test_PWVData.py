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


"""Tests for the ``pwv_kpno.gps_pwv.PWVData`` class"""

from pathlib import Path
from unittest import TestCase

from pwv_kpno.gps_pwv import PWVData, search_data_table
from tests.utils import TestWithCleanEnv

TEST_DATA_DIR = Path(__file__).parent / 'testing_data'


@TestWithCleanEnv(TEST_DATA_DIR)
class WeatherData(TestCase):
    """Tests for the ``PWVData.weather_data`` function"""

    def setUp(self):
        self.test_class = PWVData('KITT')

    def test_filtering_by_args(self):
        """Test returned dates are filtered by kwarg arguments"""

        search_kwargs = {'year': 2010, 'month': 7, 'day': 21, 'hour': 5}
        full_table = self.test_class.weather_data()
        searched_table = search_data_table(full_table, **search_kwargs)

        returned_table = self.test_class.weather_data(**search_kwargs)
        self.assertEqual(searched_table, returned_table)
