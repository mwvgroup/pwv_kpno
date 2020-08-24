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

import numpy as np
from pytz import utc

from pwv_kpno import file_parsing
from tests.utils import TestWithCleanEnv

TEST_DATA_DIR = Path(__file__).parent / 'testing_data'


class SuomiDateToTimestamp(TestCase):
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


class ParsePathStem(TestCase):
    """Tests for the ``_parse_path_stem`` function"""

    def setUp(self):
        """Define a dummy file path"""

        self.receiver_id = 'RECI'
        self.year = 2020
        self.test_path = Path('{}dy_{}'.format(self.receiver_id, self.year))

    def test_correct_receiver(self):
        """Test the correct receiver Id is recovered from the file path"""

        receiver_id, year = file_parsing._parse_path_stem(self.test_path)
        self.assertEqual(self.receiver_id, receiver_id)

    def test_correct_year(self):
        """Test the correct year is recovered from the file path"""

        receiver_id, year = file_parsing._parse_path_stem(self.test_path)
        self.assertEqual(self.year, year)


class SuomiNetFileParsing(TestCase):
    """Test file parsing of SuomiNet data files"""

    def test_column_names(self):
        """Test returned data has correct columns"""

        # Data file with no known formatting issues
        parsed_data = file_parsing.read_suomi_file(TEST_DATA_DIR / 'KITThr_2016.plt')
        expected_columns = ['PWV', 'PWVErr', 'ZenithDelay', 'SrfcPress', 'SrfcTemp', 'SrfcRH']
        np.testing.assert_array_equal(expected_columns, parsed_data.columns)

    def test_indexed_by_date(self):
        """Test the index is named ``date``"""

        parsed_data = file_parsing.read_suomi_file(TEST_DATA_DIR / 'KITThr_2016.plt')
        self.assertEqual('date', parsed_data.index.name)

    def test_index_is_unique(self):
        """Test for the removal of any duplicate dates"""

        # Data file with known duplicate entries
        parsed_data = file_parsing.read_suomi_file(TEST_DATA_DIR / 'AZAMhr_2015.plt')
        self.assertFalse(parsed_data.index.duplicated().any())

    def test_removed_negative_values(self):
        """Test for the removal of negative PWV values"""

        parsed_data = file_parsing.read_suomi_file(TEST_DATA_DIR / 'KITThr_2016.plt')
        self.assertFalse(any(parsed_data['PWV'] < 0))

    def test_parse_2010_data(self):
        """Test file parsing of SuomiNet data published in 2010

        In 2010 SuomiNet changed the number of columns in their automatically
        generated data files. This caused the first half of the ascii file
        to have a different number of columns from the second half of the year.
        """

        file_parsing.read_suomi_file(TEST_DATA_DIR / 'SA48dy_2010.plt')


@TestWithCleanEnv(TEST_DATA_DIR)
class LoadRecDirectory(TestCase):
    """Tests for the ``load_rec_directory`` function"""

    def test_empty_dataframe_columns(self):
        """Test returned DataFrame has correct column names"""

        # Use a fake receiver Id should return an empty dataframe
        data = file_parsing.load_rec_directory('dummy_receiver')
        expected_columns = ['PWV, PWVErr', 'ZenithDelay', 'SrfcPress', 'SrfcTemp', 'SrfcRH']
        self.assertListEqual(expected_columns, list(data.columns))

    def test_empty_dataframe_index(self):
        """Test the returned DataFrame is indexed by ``date``"""

        # Use a fake receiver Id should return an empty dataframe
        data = file_parsing.load_rec_directory('dummy_receiver')
        self.assertEqual('date', data.index.name)

    def test_warns_on_empty_data(self):
        """Test a warning is raised for an empty data frame"""

        with self.assertWarns(Warning):
            file_parsing.load_rec_directory('dummy_receiver')

    def test_expected_years_are_parsed(self):
        """Test data is returned from all available data files for a given receiver"""

        azam_data = file_parsing.load_rec_directory('AZAM')
        self.assertEqual(2015, azam_data.index.min().year, '2015 data missing from return')
        self.assertEqual(2016, azam_data.index.max().year, '2016 data missing from return')
