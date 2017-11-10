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

from pwv_kpno import measured_pwv
import unittest
from datetime import datetime

from astropy.table import Table
from pytz import utc


from pwv_kpno.end_user_functions import _check_transmission_args
from pwv_kpno.end_user_functions import transmission, modeled_pwv


class TestErrorRaising(unittest.TestCase):
    """Check errors are thrown appropriately by pwv_kpno.transmission"""

    pwv_model = modeled_pwv()

    def test_argument_types(self):
        """Test errors from function call with wrong arg types

        Test that the appropriate errors are raised when transmission is
        called with the wrong argument types.
        """

        with self.assertRaises(TypeError):
            transmission(1, 1)
            transmission("1", 1)

            datetime_object = datetime.utcnow()
            datetime_object = datetime_object.replace(year=2011, tzinfo=utc)
            transmission(datetime_object, "1")

        # Error should be thrown for a naive datetime with no time zone info
        with self.assertRaises(ValueError):
            transmission(datetime.now(), 1)

    def test_year_out_of_range(self):
        """Test errors from function call with date out of range"""

        early_date = datetime(year=2009, month=12, day=31, tzinfo=utc)
        with self.assertRaises(ValueError):
            transmission(date=early_date, airmass=1)

        current_year = datetime.now().year
        late_date = datetime(year=current_year + 1, month=1, day=1, tzinfo=utc)
        with self.assertRaises(ValueError):
            transmission(date=late_date, airmass=1)

    def data_gap_handeling(self):  # Todo

        one_day_gap_begin = datetime(year=2010, month=1, day=11, tzinfo=utc)
        two_day_gap_begin = datetime(year=2010, month=2, day=10, tzinfo=utc)
        three_day_gap_begin = datetime(year=2010, month=4, day=11, tzinfo=utc)
        four_day_gap_begin = datetime(year=2010, month=8, day=4, tzinfo=utc)

        # Should return the interpolated transmission function
        self.assertIsInstance(transmission(one_day_gap_begin, 1), Table)
        self.assertIsInstance(transmission(two_day_gap_begin, 1), Table)

        with self.assertRaises(ValueError):
            _check_transmission_args(three_day_gap_begin, 1, self.pwv_model)

        with self.assertRaises(ValueError):
            _check_transmission_args(four_day_gap_begin, 1, self.pwv_model)


class TestDataRetrieval(unittest.TestCase):
    """Tests to ensure appropriate errors are thrown by pwv_kpno.measure_pwv"""

    all_local_pwv_data = measured_pwv()

    def test_checks_for_valid_year(self):
        """Test for correct errors due to bad year argument"""

        self.assertRaises(ValueError, measured_pwv, -2010)
        self.assertRaises(ValueError, measured_pwv, 2009)
        self.assertRaises(ValueError, measured_pwv, datetime.now().year + 1)
        self.assertRaises(TypeError, measured_pwv, '2009')
        self.assertRaises(TypeError, measured_pwv, 2009.0)

    def test_checks_for_valid_month(self):
        """Test for correct errors due to bad month argument"""

        self.assertRaises(ValueError, measured_pwv, month=-3)
        self.assertRaises(ValueError, measured_pwv, month=0)
        self.assertRaises(ValueError, measured_pwv, month=13)
        self.assertRaises(ValueError, measured_pwv, month=20)
        self.assertRaises(TypeError, measured_pwv, month='12')
        self.assertRaises(TypeError, measured_pwv, month=12.0)
        self.assertTrue(measured_pwv(month=12))

    def test_checks_for_valid_day(self):
        """Test for correct errors due to bad day argument"""

        self.assertRaises(ValueError, measured_pwv, day=-3)
        self.assertRaises(ValueError, measured_pwv, day=0)
        self.assertRaises(ValueError, measured_pwv, day=32)
        self.assertRaises(ValueError, measured_pwv, day=40)
        self.assertRaises(TypeError, measured_pwv, day='17')
        self.assertRaises(TypeError, measured_pwv, day=17.0)
        self.assertTrue(measured_pwv(day=17))

    def test_checks_for_valid_hour(self):
        """Test for correct errors due to bad hour argument"""

        self.assertRaises(ValueError, measured_pwv, hour=-3)
        self.assertRaises(ValueError, measured_pwv, hour=24)
        self.assertRaises(ValueError, measured_pwv, hour=30)
        self.assertRaises(TypeError, measured_pwv, hour='12')
        self.assertRaises(TypeError, measured_pwv, hour=12.0)
        self.assertTrue(measured_pwv(hour=17))

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