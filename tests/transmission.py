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

"""This file provides tests for the function "transmission"."""

import unittest
from datetime import datetime, timedelta

import numpy as np
from pytz import utc

from pwv_kpno._transmission import _trans_for_date
from pwv_kpno._transmission import trans_for_date
from pwv_kpno._transmission import _raise_transmission_args
from pwv_kpno._transmission import _raise_available_data
from pwv_kpno._transmission import _raise_pwv
from _create_mock_data import create_mock_pwv_model

__authors__ = ['Daniel Perrefort']
__copyright__ = 'Copyright 2017, Daniel Perrefort'

__license__ = 'GPL V3'
__email__ = 'djperrefort@pitt.edu'
__status__ = 'Development'


class TransmissionErrors(unittest.TestCase):
    """Test pwv_kpno.transmission for raised errors due to bad arguments"""

    def test_argument_types(self):
        """Test errors raised from function call with wrong argument types"""

        test_date = datetime(2011, 1, 5, 12, 47, tzinfo=utc)

        # TypeError for date argument (should be datetime)
        self.assertRaises(TypeError, _raise_transmission_args, "1", 1)

        # TypeError for airmass argument (should be float or int)
        self.assertRaises(TypeError, _raise_transmission_args, test_date, "1")

        # ValueError due to naive datetime with no time zone info
        self.assertRaises(ValueError, _raise_transmission_args,
                          datetime.now(), 1)

    def test_argument_values(self):
        """Test errors raise from function call with date out of data range

        An error should be raised for dates that are not covered by the locally
        available data files. For the release version of the package, the
        acceptable date range begins with 2010 through the current date.
        """

        early_day = datetime(year=2009, month=12, day=31, tzinfo=utc)
        self.assertRaises(ValueError, _raise_transmission_args, early_day, 1)

        now = datetime.now()
        late_day = now + timedelta(days=1)
        self.assertRaises(ValueError, _raise_transmission_args, late_day, 1)

        late_year = datetime(year=now.year + 1, month=1, day=1, tzinfo=utc)
        self.assertRaises(ValueError, _raise_transmission_args, late_year, 1)

    def test_data_gap_handling(self):
        """Test errors raised from function call for datetime without PWV data

        The function 'transmission' should raise an error if it is asked for
        the atmospheric transmission at a datetime that falls within a gap in
        available data spanning three days or more.
        """

        # Start dates for data gaps
        one_day_start = datetime(year=2010, month=1, day=11, tzinfo=utc)
        three_day_start = datetime(year=2010, month=4, day=11, tzinfo=utc)

        gaps = [(one_day_start, 1), (three_day_start, 3)]
        mock_model = create_mock_pwv_model(year=2010, gaps=gaps)

        self.assertRaises(ValueError, _raise_available_data,
                          one_day_start, mock_model)
        self.assertRaises(ValueError, _raise_available_data,
                          three_day_start, mock_model)


class TransmissionPwvErrors(unittest.TestCase):
    """Test pwv_kpno.transmission_pwv for raised errors due to bad arguments"""

    def test_argument_types(self):
        """Test errors raised from function call with wrong argument types"""

        self.assertIsNone(_raise_pwv(13))
        self.assertIsNone(_raise_pwv(13.0))

    def test_argument_values(self):
        """Test errors raised from function call with out of range values

        PWV concentrations should be between 0 and 30.1 mm (inclusive). This
        is due to the range of the atmospheric models.
        """

        self.assertRaises(ValueError, _raise_pwv, -1)

        # Check value that uses interpolation
        self.assertIsNone(_raise_pwv(15.0))

        # Check value outside domain that uses extrapolation
        self.assertIsNone(_raise_pwv(30.5))


class TransmissionResults(unittest.TestCase):
    """Test pwv_kpno.transmission for the expected returns"""

    mock_model = create_mock_pwv_model(2010)

    def test_airmass_dependence(self):
        """Test that line of sight pwv is directly proportional to airmass"""

        date_35 = self.mock_model['date'][35]
        date_35 = datetime.utcfromtimestamp(date_35).replace(tzinfo=utc)

        date_40 = self.mock_model['date'][40]
        date_40 = datetime.utcfromtimestamp(date_40).replace(tzinfo=utc)

        airmass_2_transm = _trans_for_date(date_35, 2, self.mock_model)
        airmass_1_transm = _trans_for_date(date_40, 1, self.mock_model)

        same_transmission = np.equal(airmass_1_transm['transmission'],
                                     airmass_2_transm['transmission'])

        self.assertTrue(all(same_transmission))

    def test_column_units(self):
        """Test columns of the returned transmission table for correct units

        Perform the test for the transmission at 2011/01/01 00:00 and an
        airmass of 1.
        """

        sample_transm = trans_for_date(datetime(2011, 1, 1, tzinfo=utc), 1)
        w_units = sample_transm['wavelength'].unit
        t_units = sample_transm['transmission'].unit

        error_msg = 'Wrong units for column "{}"'
        self.assertEqual(w_units, 'angstrom', error_msg.format('wavelength'))
        self.assertEqual(t_units, None, error_msg.format('transmission'))
