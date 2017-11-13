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

"""This file provides tests for the function "transmission"."""

import unittest
from datetime import datetime, timedelta

import numpy as np
from pytz import utc

from pwv_kpno import transmission
from pwv_kpno.end_user_functions import _check_transmission_args as arg_check
from tests.create_mock_data import create_mock_pwv_model

__author__ = 'Daniel Perrefort'
__copyright__ = 'Copyright 2017, Daniel Perrefort'

__license__ = 'GPL V3'
__email__ = 'djperrefort@gmail.com'
__status__ = 'Development'


class TestTransmissionArgs(unittest.TestCase):
    """Test pwv_kpno.transmission for raised errors due to bad arguments"""

    @classmethod
    def setUpClass(self):

        # Start dates for data gaps
        self.one_day_start = datetime(year=2010, month=1, day=11, tzinfo=utc)
        self.two_day_start = datetime(year=2010, month=2, day=10, tzinfo=utc)
        self.three_day_start = datetime(year=2010, month=4, day=11, tzinfo=utc)
        self.four_day_start = datetime(year=2010, month=8, day=4, tzinfo=utc)

        gaps = [(self.one_day_start, 1), (self.two_day_start, 2),
                (self.three_day_start, 3), (self.four_day_start, 4)]

        self.mock_model = create_mock_pwv_model(year=2010, gaps=gaps)

    def test_argument_types(self):
        """Test errors raised from function call with wrong argument types"""

        test_date = datetime.utcnow()
        test_date = test_date.replace(year=2011, tzinfo=utc)

        # TypeError for date argument (should be datetime)
        self.assertRaises(TypeError, arg_check, "1", 1, self.mock_model)

        # TypeError for airmass argument (should be float or int)
        bad_airmass_args = (test_date, "1", self.mock_model)
        self.assertRaises(TypeError, arg_check, *bad_airmass_args)

        # ValueError due to naive datetime with no time zone info
        bad_datetime_args = (datetime.now(), 1, self.mock_model)
        self.assertRaises(ValueError, arg_check, *bad_datetime_args)

    def test_year_out_of_range(self):
        """Test errors from function call with date out of data range

        An error should be raised for dates that are not covered by the locally
        available data files. For the release version of the package, the
        acceptable date range begins with 2010 through the current date.
        """

        early_date = datetime(year=2009, month=12, day=31, tzinfo=utc)
        self.assertRaises(ValueError, arg_check, early_date, 1, self.mock_model)

        now = datetime.now()
        late_day = now + timedelta(days=1)
        self.assertRaises(ValueError, arg_check, late_day, 1, self.mock_model)

        late_year = datetime(year=now.year + 1, month=1, day=1, tzinfo=utc)
        self.assertRaises(ValueError, arg_check, late_year, 1, self.mock_model)

    def test_data_gap_handeling(self):
        """Test for error due to function call for a datetime without PWV data

        The function 'transmission' should raise an error if it is asked for
        the atmospheric transmission at a datetime that falls within a gap in
        available data spanning three days or more.
        """

        four_day_args = (self.four_day_start, 1, self.mock_model)
        self.assertRaises(ValueError, arg_check, *four_day_args)

        three_day_args = (self.three_day_start, 1, self.mock_model)
        self.assertRaises(ValueError, arg_check, *three_day_args)

        self.assertIsNone(arg_check(self.two_day_start, 1, self.mock_model))
        self.assertIsNone(arg_check(self.one_day_start, 1, self.mock_model))


class TestTransmissionResults(unittest.TestCase):
    """Test pwv_kpno.transmission for the expected returns"""

    mock_model = create_mock_pwv_model(2010)

    def test_airmass_dependence(self):
        """Test that line of sight pwv is directly proportional to airmass"""

        date_35 = self.mock_model['date'][35]
        date_35 = datetime.utcfromtimestamp(date_35).replace(tzinfo=utc)

        date_40 = self.mock_model['date'][40]
        date_40 = datetime.utcfromtimestamp(date_40).replace(tzinfo=utc)

        airmass_2_transm = transmission(date_35, 2, self.mock_model)
        airmass_1_transm = transmission(date_40, 1, self.mock_model)

        same_transmission = np.equal(airmass_1_transm['transmission'],
                                     airmass_2_transm['transmission'])

        self.assertTrue(all(same_transmission))

    def test_interpolation(self):  # Todo
        pass

    def test_column_units(self):
        """Test columns of the returned transmission table for correct units

        Perform the test for the transmission at 2011/01/01 00:00 and an
        airmass of 1.
        """

        sample_transm = transmission(datetime(2011, 1, 1, tzinfo=utc), 1)
        w_units = sample_transm['wavelength'].unit
        t_units = sample_transm['transmission'].unit

        error_msg = 'Wrong units for column "{}"'
        self.assertEqual(w_units, 'angstrom', error_msg.format('wavelength'))
        self.assertEqual(t_units, 'percent', error_msg.format('transmission'))
