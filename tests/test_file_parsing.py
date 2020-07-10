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

"""This file tests the pwv_kpno._download_pwv_data module to ensure SuomiNet
data is downloaded and parsed correctly.
"""

from datetime import datetime
from pathlib import Path
from unittest import TestCase

from pytz import utc

from pwv_kpno import file_parsing

TEST_DATA_DIR = Path(__file__).parent / 'testing_data'


class DateFormatConversion(TestCase):
    """Test the conversion of SuomiNet datetime format to timestamps"""

    def test_round_off_error_correction(self):
        """Test returned timestamps for round off error"""

        # Date with known round off error before bug fix in 0.9.13
        jan_01_2010_01_15 = datetime(2010, 1, 1, 1, 15, tzinfo=utc)
        self.assertEqual(
            file_parsing._suomi_date_to_timestamp(2010, '1.05208'),
            jan_01_2010_01_15.timestamp())

    def test_correct_conversion_for_known_dates(self):
        """Test date format conversion for known dates"""

        error_msg = 'Incorrect _timestamp for {}'
        jan_01_2000_00_15 = datetime(2000, 1, 1, 0, 15, tzinfo=utc)
        self.assertEqual(
            file_parsing._suomi_date_to_timestamp(2000, '1.01042'),
            jan_01_2000_00_15.timestamp(),
            error_msg.format(jan_01_2000_00_15))

        dec_31_2021_23_15 = datetime(2021, 12, 31, 23, 15, tzinfo=utc)
        self.assertEqual(
            file_parsing._suomi_date_to_timestamp(2021, '365.96875'),
            dec_31_2021_23_15.timestamp(),
            error_msg.format(dec_31_2021_23_15))


class SuomiNetFileParsing(TestCase):
    """Test file parsing of SuomiNet data files"""

    def test_column_names(self):
        """Test returned data has correct columns"""

        # Data file with no known formatting issues
        parsed_data = file_parsing.read_suomi_data(TEST_DATA_DIR / 'KITThr_2016.plt')
        expected_columns = ['date', 'KITT', 'KITT_err', 'ZenithDelay', 'SrfcPress', 'SrfcTemp', 'SrfcRH']
        self.assertEqual(expected_columns, parsed_data.colnames)

    def test_dates_are_unique(self):
        """Test for the removal of any duplicate dates"""

        # Data file with known duplicate entries
        parsed_data = file_parsing.read_suomi_data(TEST_DATA_DIR / 'AZAMhr_2015.plt')

        table_entries = len(parsed_data)
        unique_dates = len(set(parsed_data['date']))
        self.assertEqual(table_entries, unique_dates)

    def test_removed_negative_values(self):
        """Test for the removal of negative PWV values"""

        parsed_data = file_parsing.read_suomi_data(TEST_DATA_DIR / 'KITThr_2016.plt')
        is_negative_pwv = any(parsed_data['KITT'] < 0)
        self.assertFalse(is_negative_pwv)

    def test_parse_2010_data(self):
        """Test file parsing of SuomiNet data published in 2010

        In 2010 SuomiNet changed the number of columns in their automatically
        generated data files. This caused the first half of the ascii file
        to have a different number of columns from the second half of the year.
        """

        file_parsing.read_suomi_data(TEST_DATA_DIR / 'SA48dy_2010.plt')
