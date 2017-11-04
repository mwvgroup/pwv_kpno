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
#    along with pwv_kpno.  If not, see <http://www.gnu.org/licenses/>.

import os
import unittest
from datetime import datetime

from astropy.table import Table
from pytz import utc

from pwv_kpno.create_mock_data import create_mock_files
from pwv_kpno.end_user_functions import transmission


class TestTransmissionArgs(unittest.TestCase):
    """Check errors are thrown appropriately by pwv_kpno.transmission"""

    def __init__(self, *args, **kwargs):
        """Create mock data if not already available"""

        super().__init__(*args, **kwargs)

        mock_model_path = 'tests/mock_pwv_model.csv'
        if not os.path.exists(mock_model_path):
            create_mock_files(os.path.dirname(mock_model_path))

        self.mock_pwv_model = Table.read(mock_model_path)

    def test_argument_types(self):
        """Check errors from function call with wrong arg types

        Test that the appropriate errors are raised when transmission is
        called with the wrong argument types.
        """

        with self.assertRaises(TypeError):
            transmission(1, 1)
            transmission("1", 1)

            datetime_object = datetime.utcnow()
            datetime_object = datetime_object.replace(tzinfo=utc)
            transmission(datetime_object, "1")

        # Error should be thrown for a naive datetime with no time zone info
        with self.assertRaises(ValueError):
            transmission(datetime.now(), 1)

    def test_year_out_of_range(self):
        """Check errors from functioncall with date out of range"""

        early_date = datetime(year=2009, month=12, day=31, tzinfo=utc)
        with self.assertRaises(ValueError):
            transmission(date=early_date, airmass=1)

        current_year = datetime.now().year
        late_date = datetime(year=current_year + 1, month=1, day=1, tzinfo=utc)
        with self.assertRaises(ValueError):
            transmission(date=late_date, airmass=1)


if __name__ == '__main__':
    unittest.main()
