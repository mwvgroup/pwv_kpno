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

import unittest
from datetime import datetime

from astropy.table import Table
from pytz import utc

from pwv_kpno import measured_pwv
from pwv_kpno.end_user_functions import _check_search_args


class TestDataRetrievalArgs(unittest.TestCase):
    """Test pwv_kpno.transmission for raised errors due to bad arguments"""

    all_local_pwv_data = measured_pwv()

    def test_checks_for_valid_year(self):
        """Test for correct errors due to bad year argument"""

        next_year = datetime.now().year + 1
        self.assertRaises(ValueError, _check_search_args, -2010)
        self.assertRaises(ValueError, _check_search_args, 2009)
        self.assertRaises(ValueError, _check_search_args, next_year)
        self.assertRaises(TypeError, _check_search_args, '2009')
        self.assertRaises(TypeError, _check_search_args, 2009.0)

    def test_checks_for_valid_month(self):
        """Test for correct errors due to bad month argument"""

        self.assertRaises(ValueError, _check_search_args, month=-3)
        self.assertRaises(ValueError, _check_search_args, month=0)
        self.assertRaises(ValueError, _check_search_args, month=13)
        self.assertRaises(ValueError, _check_search_args, month=20)
        self.assertRaises(TypeError, _check_search_args, month='12')
        self.assertRaises(TypeError, _check_search_args, month=12.0)

    def test_checks_for_valid_day(self):
        """Test for correct errors due to bad day argument"""

        self.assertRaises(ValueError, _check_search_args, day=-3)
        self.assertRaises(ValueError, _check_search_args, day=0)
        self.assertRaises(ValueError, _check_search_args, day=32)
        self.assertRaises(ValueError, _check_search_args, day=40)
        self.assertRaises(TypeError, _check_search_args, day='17')
        self.assertRaises(TypeError, _check_search_args, day=17.0)

    def test_checks_for_valid_hour(self):
        """Test for correct errors due to bad hour argument"""

        self.assertRaises(ValueError, _check_search_args, hour=-3)
        self.assertRaises(ValueError, _check_search_args, hour=24)
        self.assertRaises(ValueError, _check_search_args, hour=30)
        self.assertRaises(TypeError, _check_search_args, hour='12')
        self.assertRaises(TypeError, _check_search_args, hour=12.0)

    def test_returned_tz_info(self):
        """Test if datetimes in the returned data are timezone aware"""

        tzinfo = self.all_local_pwv_data['date'][0].tzinfo
        self.assertTrue(tzinfo == utc, 'Datetimes should be UTC aware')

    def test_returned_column_order(self):
        """Test the column order of the table returned by measured_pwv()"""

        self.assertTrue(self.all_local_pwv_data.colnames[0] == 'date',
                        'First column of measured_pwv() should be "date"')

        self.assertTrue(self.all_local_pwv_data.colnames[1] == 'KITT',
                        'Second column of measured_pwv() should be "KITT"')

    def test_returned_date_range(self):
        """Test that SuomiNet data is available only for the appropriate years

        Each package distribution should contain all necessary SuomiNet data
        for 2010 through the previous year.
        """

        earliest_date = min(self.all_local_pwv_data['date'])
        earliest_date = earliest_date.replace(tzinfo=None)

        expected_earliest_date = datetime(2010, 1, 1, 0, 15)
        msg = 'Expected earliest date in data to be {}. Found {}.'
        self.assertTrue(earliest_date == expected_earliest_date,
                        msg.format(expected_earliest_date, earliest_date))

        msg = 'No SuomiNet data found for {}'
        for year in range(2010, datetime.now().year):
            data_for_year = measured_pwv(year)
            self.assertTrue(data_for_year, msg.format(year))

        current_year = datetime.now().year
        msg = 'There should be no data for the current year ({})'
        self.assertFalse(measured_pwv(current_year), msg.format(current_year))

    def _check_attrs(self, table, **kwargs):
        """Check value of datetime attributes from 'date' column of a table

        Iterate through the 'date' column of a table and check that all
        attribute values match those specified by **kwargs.

        Args:
            table    (Table): A table with a 'date' column
            **kwargs      (): datetime attributes and values

        Returns:
            True or False
        """

        assert (len(kwargs), 'No attributes specified')
        for obj in table['date']:
            for param_name, param_value in kwargs.items():
                if getattr(obj, param_name) != param_value:
                    return False

        return True

    def assert_filter(self, kwargs):
        """Assert if measured_pwv results are correctly filtered by kwargs"""

        msg = 'measured_pwv returned incorrect dates. kwargs: {}'
        self.assertTrue(self._check_attrs(measured_pwv(**kwargs), **kwargs),
                        msg.format(kwargs))

    def test_filtering_by_args(self):
        """Test if results are correctly filtered for multiple kwarg combos"""

        self.assert_filter({'year': 2010})
        self.assert_filter({'month': 7})
        self.assert_filter({'day': 21})
        self.assert_filter({'hour': 5})
        self.assert_filter({'year': 2011, 'month': 4, 'day': 30, 'hour': 21})