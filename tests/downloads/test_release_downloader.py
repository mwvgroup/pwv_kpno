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


"""Tests for the ``pwv_kpno.downloads.ReleaseDownloader`` class"""

import re
from unittest import TestCase

import requests_mock

from pwv_kpno.downloads import ReleaseDownloader
from tests.utils import TestWithCleanEnv


@requests_mock.Mocker()
@TestWithCleanEnv()
class DownloadURLS(TestCase):
    """Test download_functions retrieve data from the correct URLs"""

    # Expected URLs for each kind of data release. Supports regex.
    conus_daily_url = 'https://www.suominet.ucar.edu/data/staYrDay/*'
    conus_hourly_url = 'https://www.suominet.ucar.edu/data/staYrHr/*'
    global_daily_url = 'https://www.suominet.ucar.edu/data/staYrDayGlob/*'

    def setUp(self):
        """Instantiate a ``ReleaseDownloader`` object for testing"""

        self.downloader = ReleaseDownloader('dummy_receiver_id')

    def test_correct_conus_daily_url(self, mocker):
        """Test ``download_conus_daily`` downloads from the conus daily url"""

        mocker.register_uri('GET', re.compile(self.conus_daily_url))
        self.downloader.download_conus_daily(2020)

    def test_correct_conus_hourly_url(self, mocker):
        """Test ``download_conus_hourly`` downloads from the conus hourly url"""

        mocker.register_uri('GET', re.compile(self.conus_hourly_url))
        self.downloader.download_conus_hourly(2020)

    def test_correct_conus_global_daily_url(self, mocker):
        """Test ``download_global_daily`` downloads from the global daily url"""

        mocker.register_uri('GET', re.compile(self.global_daily_url))
        self.downloader.download_global_daily(2020)


@TestWithCleanEnv()
class DownloadedPathNames(TestCase):
    """Test downloaded files are saved with the correct naming scheme"""

    def setUp(self):
        """Instantiate a ``ReleaseDownloader`` object for testing"""

        self.dummy_rec_name = 'dummy_receiver_id'.upper()
        self.downloader = ReleaseDownloader(self.dummy_rec_name)
        self.dummy_year = 2020

    def assertCorrectFilePath(self, download_func: callable, file_name: str):
        """Assert a given download function downloads to the given file name

        Args:
            download_func: Download function to call with receiver Id and year
            file_name: Name of file that should be created by ``download_func``
        """

        # Allow all possible URL's with SSL
        with requests_mock.Mocker() as mocker:
            mocker.register_uri('GET', re.compile('https://*'), )
            download_func(self.dummy_rec_name, self.dummy_year, verbose=False)

        expected_path = self.downloader.data_dir / file_name
        self.assertTrue(expected_path.exists())

    def test_correct_conus_daily_path_format(self):
        """Test ``download_conus_daily`` uses the correct file pattern"""

        self.assertCorrectFilePath(
            self.downloader.download_conus_daily,
            f'{self.dummy_rec_name}dy_{self.dummy_year}.plt')

    def test_correct_conus_hourly_path_format(self):
        """Test ``download_conus_hourly`` uses the correct file pattern"""

        self.assertCorrectFilePath(
            self.downloader.download_conus_hourly,
            f'{self.downloader.receiver_id}hr_{self.dummy_year}.plt')

    def test_correct_conus_global_daily_path_format(self):
        """Test ``download_global_daily`` uses the correct file pattern"""

        self.assertCorrectFilePath(
            self.downloader.download_global_daily,
            f'{self.dummy_rec_name}gl_{self.dummy_year}.plt')


class Repr(TestCase):
    """Tests for the string representation of ``URLDownloader``"""

    def test_can_be_evaluated(self):
        """Test the class representation can be evaluated"""

        test_class = ReleaseDownloader('dummy_receiver')
        new_class = eval(repr(test_class))

        self.assertEqual(test_class.receiver_id, new_class.receiver_id)
        self.assertEqual(test_class.data_dir, new_class.data_dir)
