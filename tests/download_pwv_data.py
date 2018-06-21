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

"""This file tests that SuomiNet data is downloaded and parsed correctly."""

import os
from datetime import datetime

import unittest
from pytz import utc
import requests

from pwv_kpno._download_pwv_data import _download_data_for_year
from pwv_kpno._download_pwv_data import _read_file
from pwv_kpno._download_pwv_data import _suomi_date_to_timestamp
from pwv_kpno._serve_pwv_data import timestamp
from pwv_kpno._settings import Settings

__authors__ = ['Daniel Perrefort']
__copyright__ = 'Copyright 2017, Daniel Perrefort'

__license__ = 'GPL V3'
__email__ = 'djperrefort@pitt.edu'
__status__ = 'Development'

try:
    req = requests.get('http://www.suominet.ucar.edu')
    SUOMINET_OFFLINE = req.status_code != 200

except requests.exceptions.ConnectionError:
    SUOMINET_OFFLINE = True


@unittest.skipIf(SUOMINET_OFFLINE, 'SuomiNet.ucar.edu Unreachable')
class SuomiNetDataDownload(unittest.TestCase):
    """Tests data is downloaded correctly by _download_suomi_data_for_year"""

    @classmethod
    def setUpClass(cls):
        """Download data from SuomiNet for 2012 and 2015"""

        cls.data_2012 = _download_data_for_year(2012)
        cls.data_2015 = _download_data_for_year(2015)

    def test_column_names(self):
        """Test downloaded data for correct columns"""

        bad_column_msg = 'Wrong columns for year={}'
        expected_2015_cols = {'date', 'KITT', 'KITT_err', 'P014', 'P014_err',
                              'SA46', 'SA46_err', 'SA48', 'SA48_err', 'AZAM',
                              'AZAM_err'}

        expected_2012_cols = expected_2015_cols - {'KITT', 'KITT_err'}

        retrieved_2015_cols = set(self.data_2015.colnames)
        self.assertEqual(retrieved_2015_cols, expected_2015_cols,
                         bad_column_msg.format(2015))

        retrieved_2012_cols = set(self.data_2012.colnames)
        self.assertEqual(retrieved_2012_cols, expected_2012_cols,
                         bad_column_msg.format(2012))

    def test_year_values(self):
        """Test data was downloaded for the correct years"""

        error_msg = 'Wrong data downloaded for year {}'
        first_2012_date = datetime.utcfromtimestamp(self.data_2012['date'][0])
        first_2015_date = datetime.utcfromtimestamp(self.data_2015['date'][0])

        self.assertEqual(first_2012_date.year, 2012, error_msg.format(2012))
        self.assertEqual(first_2015_date.year, 2015, error_msg.format(2015))


class DateFormatConversion(unittest.TestCase):
    """Tests conversion of SuomiNet datetime format to timestamps"""

    def test_roundoff_error(self):
        """Test returned timestamps for round off error"""

        # Dates with known round off error before bug fix in 0.9.13
        jan_01_2010_01_15 = datetime(2010, 1, 1, 1, 15, tzinfo=utc)
        jan_01_2010_02_45 = datetime(2010, 1, 1, 2, 45, tzinfo=utc)
        jan_01_2010_04_15 = datetime(2010, 1, 1, 4, 15, tzinfo=utc)

        error_msg = 'Incorrect timestamp for {}'
        self.assertEqual(_suomi_date_to_timestamp(2010, '1.05208'),
                         timestamp(jan_01_2010_01_15),
                         error_msg.format(jan_01_2010_01_15))

        self.assertEqual(_suomi_date_to_timestamp(2010, '1.11458'),
                         timestamp(jan_01_2010_02_45),
                         error_msg.format(jan_01_2010_02_45))

        self.assertEqual(_suomi_date_to_timestamp(2010, '1.17708'),
                         timestamp(jan_01_2010_04_15),
                         error_msg.format(jan_01_2010_04_15))

    def test_dates_out_of_data_range(self):
        """Test timestamp calculation for dates outside SuomiNet data range"""

        jan_01_2000_00_15 = datetime(2000, 1, 1, 0, 15, tzinfo=utc)
        dec_31_2021_23_15 = datetime(2021, 12, 31, 23, 15, tzinfo=utc)

        error_msg = 'Incorrect timestamp for {}'
        self.assertEqual(_suomi_date_to_timestamp(2000, '1.01042'),
                         timestamp(jan_01_2000_00_15),
                         error_msg.format(jan_01_2000_00_15))

        self.assertEqual(_suomi_date_to_timestamp(2021, '365.96875'),
                         timestamp(dec_31_2021_23_15),
                         error_msg.format(dec_31_2021_23_15))


class SuomiNetFileParsing(unittest.TestCase):
    """Tests file parsing by create_pwv_models._read_file"""

    @classmethod
    def setUpClass(cls):
        """Read in SuomiNet data from data files included with the package"""

        cls.kitt_hr_path = 'KITThr_2016.plt'
        cls.kitt_dy_path = 'KITTdy_2016.plt'
        cls.azam_hr_path = 'AZAMhr_2015.plt'
        cls.p014_dy_path = 'P014dy_2012.plt'

        data_dir = Settings()._suomi_dir
        cls.kitt_hr_data = _read_file(os.path.join(data_dir, cls.kitt_hr_path))
        cls.kitt_dy_data = _read_file(os.path.join(data_dir, cls.kitt_dy_path))
        cls.azam_hr_data = _read_file(os.path.join(data_dir, cls.azam_hr_path))
        cls.p014_hr_data = _read_file(os.path.join(data_dir, cls.p014_dy_path))

    def test_column_names(self):
        """Test returned data has correct columns"""

        kitt_cols = self.kitt_hr_data.colnames
        azam_cols = self.azam_hr_data.colnames
        p014_cols = self.p014_hr_data.colnames

        self.assertEqual(kitt_cols, ['date', 'KITT', 'KITT_err'])
        self.assertEqual(azam_cols, ['date', 'AZAM', 'AZAM_err'])
        self.assertEqual(p014_cols, ['date', 'P014', 'P014_err'])

    def test_dates_are_unique(self):
        """Test for the removal of any duplicate dates"""

        table_entries = len(self.azam_hr_data)
        unique_dates = len(set(self.azam_hr_data['date']))

        msg = 'Duplicate dates not filtered out when parsing AZAMhr_2015.plt'
        self.assertEqual(table_entries, unique_dates, msg)

    def test_removed_negative_values(self):
        """Test for the removal of negative PWV values"""

        msg = 'Negative PWV values were returned when parsing {}'
        is_negative_kitt_data = any(self.kitt_hr_data['KITT'] < 0)
        is_negative_azam_data = any(self.azam_hr_data['AZAM'] < 0)
        is_negative_p014_data = any(self.p014_hr_data['P014'] < 0)

        self.assertFalse(is_negative_kitt_data, msg.format(self.kitt_hr_path))
        self.assertFalse(is_negative_azam_data, msg.format(self.azam_hr_path))
        self.assertFalse(is_negative_p014_data, msg.format(self.p014_dy_path))

    @staticmethod
    def test_parse_2010_data():
        """Test file parsing of SuomiNet data published in 2010

        In 2010 SuomiNet changed the number of columns in their automatically
        generated data files. This caused the first half of the ascii file
        to have a different number of columns from the second half of the year.
        """

        hr_path = os.path.join(Settings()._suomi_dir, 'SA48dy_2010.plt')
        _read_file(hr_path)
