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

No external HTTP requests are made by these tests.
"""

import os
import re
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

import requests
import requests_mock

import pwv_kpno
from pwv_kpno import downloads, gps_pwv
from tests.utils import TestWithCleanEnv


@TestWithCleanEnv()
class FindDataDir(TestCase):
    """Tests for the ``find_data_dir`` function"""

    def test_directory_no_env_variable(self):
        """Test return directory is inside package if not in environment"""

        del os.environ['SUOMINET_DIR']
        default_data_dir = Path(pwv_kpno.__file__).resolve().parent / 'suomi_data'
        self.assertEqual(default_data_dir, downloads.find_data_dir())

    def test_directory_with_env_variable(self):
        """Test return directory defaults to environmental definition"""

        expected_dir = os.environ['SUOMINET_DIR']
        self.assertEqual(
            Path(expected_dir), downloads.find_data_dir(),
            f'Returned path did not equal environmental variable: {expected_dir}')

    def test_directory_is_resolves(self):
        """Test returned path object is resolved"""

        data_dir = downloads.find_data_dir()
        self.assertEqual(data_dir.resolve(), data_dir)


@requests_mock.Mocker()
@TestWithCleanEnv()
class SuomiDownloaderURLS(TestCase):
    """Test ``SuomiDownloader`` retrieves data from the correct URLs"""

    # Expected URLs for each kind of data release. Supports regex.
    conus_daily_url = 'https://www.suominet.ucar.edu/data/staYrDay/*'
    conus_hourly_url = 'https://www.suominet.ucar.edu/data/staYrHr/*'
    global_daily_url = 'https://www.suominet.ucar.edu/data/staYrDayGlob/*'

    def test_connection_errors_are_raised(self, mocker):
        """Test connection errors are not caught silently by the downloader"""

        url = 'http://test.com'
        mocker.register_uri('GET', url, exc=requests.exceptions.ConnectTimeout)

        func_args = dict(url=url, path=Path('./test'), timeout=1)
        self.assertRaises(
            requests.exceptions.ConnectTimeout,
            downloads._download_suomi_data,
            **func_args
        )

    def test_correct_conus_daily_url(self, mocker):
        """Test ``download_conus_daily`` downloads from the conus daily url"""

        mocker.register_uri('GET', re.compile(self.conus_daily_url))
        downloads.download_conus_daily('dummy_rec', 2020)

    def test_correct_conus_hourly_url(self, mocker):
        """Test ``download_conus_hourly`` downloads from the conus hourly url"""

        mocker.register_uri('GET', re.compile(self.conus_hourly_url))
        downloads.download_conus_hourly('dummy_rec', 2020)

    def test_correct_conus_global_daily_url(self, mocker):
        """Test ``download_global_daily`` downloads from the global daily url"""

        mocker.register_uri('GET', re.compile(self.global_daily_url))
        downloads.download_global_daily('dummy_rec', 2020)


@TestWithCleanEnv()
class SuomiDownloaderPaths(TestCase):
    """Test ``SuomiDownloader`` saves files with the correct naming scheme"""

    def setUp(self):
        self.dummy_rec_name = 'dummy_rec'
        self.dummy_year = 2020

    def assertCorrectFilePath(self, download_func: callable, file_name: str):
        """Assert a given download function downloads to the given file name

        Args:
            download_func: Download function to call with receiver Id and year
            file_name: Name of file that should be created by ``download_func``
        """

        with requests_mock.Mocker() as mocker:
            mocker.register_uri('GET', re.compile('https://*'), )
            download_func(self.dummy_rec_name, self.dummy_year)

        expected_path = Path(os.environ['SUOMINET_DIR']) / file_name
        self.assertTrue(expected_path.exists())

    def test_correct_conus_daily_path_format(self):
        """Test ``download_conus_daily`` uses the correct file pattern"""

        self.assertCorrectFilePath(
            downloads.download_conus_daily,
            f'{self.dummy_rec_name}dy_{self.dummy_year}.plt')

    def test_correct_conus_hourly_path_format(self):
        """Test ``download_conus_hourly`` uses the correct file pattern"""

        self.assertCorrectFilePath(
            downloads.download_conus_hourly,
            f'{self.dummy_rec_name}hr_{self.dummy_year}.plt')

    def test_correct_conus_global_daily_path_format(self):
        """Test ``download_global_daily`` uses the correct file pattern"""

        self.assertCorrectFilePath(
            downloads.download_global_daily,
            f'{self.dummy_rec_name}gl_{self.dummy_year}.plt')


class DataParsingReset(TestCase):
    """Test the ``data_management`` signals the ``GPSReceiver`` class when
    new data is downloaded."""

    def tearDown(self):
        """Reset the ``GPSReceiver`` reload attribute"""

        gps_pwv.GPSReceiver._reload_from_download[0] = False

    @staticmethod
    def call_arbitrary_download():
        """Call a download from a dummy URL"""

        dummy_url = 'https://some.url.com'
        with TemporaryDirectory() as tempdir:
            dummy_path = Path(tempdir) / 'dummy_path'

            with requests_mock.Mocker() as mocker:
                mocker.register_uri('GET', re.compile('https://*'), )
                downloads._download_suomi_data(
                    dummy_url, dummy_path)

    def runTest(self):
        """Test ``GPSReceiver._reload_from_download`` is updated after a download"""

        self.call_arbitrary_download()
        self.assertTrue(gps_pwv.GPSReceiver._reload_from_download[0])