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

"""This file provides tests for the end user function 'transmission' found in
pwv_kpno/end_user_functions.py
"""

import unittest
from datetime import datetime, timedelta

from astropy.table import Table
from pytz import utc

from pwv_kpno.end_user_functions import _check_transmission_args
from pwv_kpno.end_user_functions import transmission, modeled_pwv


class TestTransmissionArgs(unittest.TestCase):
    """Test pwv_kpno.transmission for raised errors due to bad arguments"""

    pwv_model = modeled_pwv()

    def test_argument_types(self):
        """Test errors raised from function call with wrong argument types"""

        # TypeError for airmass argument (should be float)
        self.assertRaises(TypeError, transmission, 1, 1)
        self.assertRaises(TypeError, transmission, "1", 1)

        # TypeError for airmass argument (should be float or int)
        test_datetime = datetime.utcnow()
        test_datetime = test_datetime.replace(year=2011, tzinfo=utc)
        self.assertRaises(TypeError, transmission, test_datetime, "1")

        # ValueError due to naive datetime with no time zone info
        self.assertRaises(ValueError, transmission, datetime.now(), 1)

    def test_year_out_of_range(self):
        """Test errors from function call with date out of data range

        An error should be raised for dates that are not covered by the locally
        available data files. For the release version of the package, the
        acceptable date range begins with 2010 through the current date.
        """

        early_date = datetime(year=2009, month=12, day=31, tzinfo=utc)
        self.assertRaises(ValueError, transmission, early_date, 1)

        now = datetime.now()
        late_day = now + timedelta(days=1)
        self.assertRaises(ValueError, transmission, late_day, 1)

        late_year = datetime(year=now.year + 1, month=1, day=1, tzinfo=utc)
        self.assertRaises(ValueError, transmission, late_year, 1)

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
