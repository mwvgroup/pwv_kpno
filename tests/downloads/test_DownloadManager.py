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


"""Tests for the downloading of data from remote SuomiNet servers.
No external HTTP requests are made by this module.
"""

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
        """Tests returned years matche test data for KITT"""

        test_receiver = 'KITT'

        self.assertDictEqual(
            self.test_data_config[test_receiver],
            DownloadManager().check_downloaded_data(test_receiver))
