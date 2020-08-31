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


"""Tests for the ``pwv_kpno.downloads.DownloadManager`` class"""

import re
from datetime import datetime
from pathlib import Path
from unittest import TestCase

import numpy as np
import requests
import requests_mock
import yaml

from pwv_kpno.downloads import DownloadManager
from tests.utils import TestWithCleanEnv

TEST_DATA_DIR = Path(__file__).parent.parent / 'testing_data'
TEST_DATA_CONFIG = TEST_DATA_DIR / 'test_data.yml'


@TestWithCleanEnv(TEST_DATA_DIR)
class CheckDownloadedReceivers(TestCase):
    """Tests for the ``check_downloaded_receivers`` function"""

    def setUp(self):
        """Read the contents of ``test_data.yml``"""

        with TEST_DATA_CONFIG.open() as infile:
            test_data_config = yaml.load(infile, yaml.SafeLoader)
            self.test_data_receivers = list(test_data_config.keys())

    def test_return_matches_test_data(self):
        """Tests returned receiver list matches test data set"""

        self.assertListEqual(
            self.test_data_receivers,
            DownloadManager().check_downloaded_receivers())


@TestWithCleanEnv(TEST_DATA_DIR)
class CheckDownloadedData(TestCase):
    """Tests for the ``check_downloaded_data`` function"""

    def setUp(self):
        """Read the contents of ``test_data.yml``"""

        with TEST_DATA_CONFIG.open() as infile:
            self.test_data_config = yaml.load(infile, yaml.SafeLoader)

    def test_return_matches_test_data(self):
        """Test the returned years match test data for KITT"""

        test_receiver = 'KITT'

        self.assertDictEqual(
            self.test_data_config[test_receiver],
            DownloadManager().check_downloaded_data(test_receiver))


@requests_mock.Mocker()
@TestWithCleanEnv()
class DownloadAvailableData(TestCase):
    """Tests for the ``download_available_data`` function"""

    def test_default_years_span_2010_through_present(self, mocker):
        """Test returned years default to 2010 through present year"""

        # We register all possible urls so that every data download attempt
        # will be considered a "success"
        mocker.register_uri('GET', re.compile('https://*'))

        returned_years = DownloadManager().download_available_data('dummy_id')
        expected_years = np.arange(2010, datetime.now().year + 1).tolist()
        self.assertListEqual(expected_years, returned_years)

    def test_only_passed_years_are_requested(self, mocker):
        """Test URL requests are only performed for the given years"""

        # Only register the years we want to test. Other years will raise an error
        years = [2011, 2012, 2018]
        for year in years:
            mocker.register_uri('GET', re.compile(f'https://.*{year}\.plt'))

        # Will raise error if URL for an unregistered year is requested
        returned_years = DownloadManager().download_available_data('dummy_id', years)

        # All test years should be returned as successful
        self.assertListEqual(years, returned_years)

    def test_only_successful_years_are_returned(self, mocker):
        """Test returned years only includes successful downloads"""

        # Setup up the year 2012 to succeed and 2013 to fail
        mocker.register_uri('GET', re.compile(f'https://.*2012\.plt'))
        mocker.register_uri('GET', re.compile(f'https://.*2013\.plt'), exc=requests.exceptions.HTTPError)
        returned_years = DownloadManager().download_available_data('dummy_id', [2012, 2013])
        self.assertListEqual([2012], returned_years)


@TestWithCleanEnv()
class DeleteLocalData(TestCase):
    """Tests for the ``delete_local_data`` function"""

    def setUp(self) -> None:
        """Create dummy files to delete during tests"""

        self.download_manager = DownloadManager()

        # Create dummy SuomiNet data files
        self.file_list = []
        for receiver in ('rec1', 'rec2'):
            for data_type in ('hr', 'dy', 'gl'):
                for year in range(2010, 2016):
                    fname = '{}{}_{}.plt'.format(receiver, data_type, year)
                    dummy_file = self.download_manager.data_dir / fname
                    dummy_file.touch()
                    self.file_list.append(dummy_file)

        # Create a dummy NON-SuomiNet data file
        self.non_suomi_file = self.download_manager.data_dir / 'non_suomi_file.plt'
        self.non_suomi_file.touch()

    def test_dry_run_leaves_files(self):
        """Test a dry run does not delete any files"""

        self.download_manager.delete_local_data('rec1', dry_run=True)
        for file in self.file_list:
            self.assertTrue(file.exists(), 'File was deleted: {}'.format(file))

    def test_deletes_given_years(self):
        """Test files are only deleted for the given years"""

        yr_to_del = (2010, 2011)
        self.download_manager.delete_local_data('rec1', years=yr_to_del)
        for file in  self.file_list:
            year = int(file.stem[-4:])
            if 'rec1' in file.stem and year in yr_to_del:
                self.assertFalse(file.exists())

            else:
                self.assertTrue(file.exists())

    def test_defaults_to_all_years(self):
        """Test all years are deleted by default"""

        self.download_manager.delete_local_data('rec1')
        for file in self.download_manager.data_dir.glob('*.plt'):
            if 'rec1' in file.stem:
                self.assertFalse(file.exists())

            else:
                self.assertTrue(file.exists())

    def test_non_suomi_files_are_safe(self):
        """Test non-suominet data files are not deleted"""

        self.download_manager.delete_local_data('rec1')
        self.assertTrue(self.non_suomi_file.exists(), 'Non-SuomiNet file was deleted')


class Repr(TestCase):
    """Tests for the string representation of ``URLDownloader``"""

    def test_can_be_evaluated(self):
        """Test the class representation can be evaluated"""

        test_class = DownloadManager('dummy_receiver')
        new_class = eval(repr(test_class))

        self.assertEqual(test_class.data_dir, new_class.data_dir)