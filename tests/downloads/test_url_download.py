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


"""Tests for the ``pwv_kpno.downloads.URLDownload`` class"""

import os
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

import requests
import requests_mock

import pwv_kpno
from pwv_kpno.downloads import URLDownload
from tests.wrappers import TestWithCleanEnv


@TestWithCleanEnv()
class DataDir(TestCase):
    """Tests that the ``data_dir`` property points to the correct location"""

    def test_user_provided_directory(self):
        """Test directory equals innit argument when given"""

        with TemporaryDirectory() as temp_dir:
            self.assertEqual(Path(temp_dir), URLDownload(temp_dir).data_dir)

    def test_env_variable_defined_directory(self):
        """Test directory defaults to env variable if not given at innit"""

        downloader = URLDownload()
        expected_dir = os.environ['SUOMINET_DIR']
        self.assertEqual(
            Path(expected_dir), downloader.data_dir,
            f'Returned path did not equal environmental variable: {expected_dir}')

    def test_no_env_variable(self):
        """Test return directory is inside package if not in environment"""

        del os.environ['SUOMINET_DIR']
        downloader = URLDownload()

        default_data_dir = Path(pwv_kpno.__file__).resolve().parent / 'suomi_data'
        self.assertEqual(default_data_dir, downloader.data_dir)

    def test_directory_is_resolved(self):
        """Test returned path object is resolved"""

        downloader = URLDownload()
        self.assertEqual(downloader.data_dir.resolve(), downloader.data_dir)


@TestWithCleanEnv()
@requests_mock.Mocker()
class DownloadSuomiUrl(TestCase):
    """Tests for the ``download_suomi_url`` function"""

    def test_connection_errors_not_caught(self, mocker: requests_mock.Mocker):
        """Test connection errors are not caught silently"""

        url = 'http://test.com'
        mocker.register_uri('GET', url, exc=requests.exceptions.ConnectTimeout)

        with self.assertRaises(requests.exceptions.ConnectTimeout):
            URLDownload().download_suomi_url(url=url, fname='test.plt', verbose=False)

    @staticmethod
    def test_queries_correct_url(mocker: requests_mock.Mocker):
        """Test only the given URL is queried"""

        url = 'http://test.com'
        mocker.register_uri('GET', url)  # Will raise error for any other URL
        URLDownload().download_suomi_url(url, 'dummy_name', verbose=False)

    def test_saves_to_correct_file_name(self, mocker: requests_mock.Mocker):
        """Test downloads are written to a file with the correct name"""

        # Register dummy URL
        url = 'http://test.com'
        mocker.register_uri('GET', url)

        # Execute mock download
        downloader = URLDownload()
        fname = 'test_file.plt'
        expected_path = downloader.data_dir / fname

        # Downloaded file should exist with correct file name
        URLDownload().download_suomi_url(url, fname, verbose=False)
        self.assertTrue(expected_path.exists())


class Repr(TestCase):
    """Tests for the string representation of ``URLDownloader``"""

    def test_can_be_evaluated(self):
        """Test the class representation can be evaluated"""

        test_class = URLDownload()
        new_class = eval(repr(test_class))
        self.assertEqual(test_class.data_dir, new_class.data_dir)
