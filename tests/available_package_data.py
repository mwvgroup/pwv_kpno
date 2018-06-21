#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

#    This file is part of the software package.
#
#    The package is free software: you can redistribute it and/or
#    modify it under the terms of the GNU General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    The package is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General
#    Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with  If not, see <http://www.gnu.org/licenses/>.

"""This file tests that the necessary SuomiNet data files are available within
the package, and that the config file accurately represents what data is
available.
"""

import os
from glob import glob
from datetime import datetime

import unittest
from pytz import utc

from pwv_kpno import _settings as pk_settings
from pwv_kpno import pwv_atm

__authors__ = ['Daniel Perrefort']
__copyright__ = 'Copyright 2017, Daniel Perrefort'

__license__ = 'GPL V3'
__email__ = 'djperrefort@pitt.edu'
__status__ = 'Development'


EXPECTED_YEARS = set(range(2010, datetime.now().year))
EXPECTED_IDS = {'KITT', 'P014', 'SA46', 'SA48', 'AZAM'}


class CorrectDataFiles(unittest.TestCase):
    """Test appropriate SuomiNet data files are included with the package"""

    @classmethod
    def setUpClass(cls):
        """Determine what data files are currently included in the package"""

        cls.data_file_years = set()
        cls.data_file_GPS_ids = set()

        glob_pattern = os.path.join(pk_settings._suomi_dir, '*.plt')
        for fname in glob(glob_pattern):
            cls.data_file_years.add(int(fname[-8: -4]))
            cls.data_file_GPS_ids.add(fname[-15: -11])

    def test_data_file_years(self):
        """Test SuomiNet data files correspond to appropriate years"""

        self.assertEqual(EXPECTED_YEARS, self.data_file_years)

    def test_correct_gps_ids(self):
        """Test SuomiNet data files correspond to appropriate GPS receivers"""

        self.assertEqual(EXPECTED_IDS, self.data_file_GPS_ids)


class CorrectConfigData(unittest.TestCase):
    """Test the Kitt Peak config file for the correct years and SuomiNet ids"""

    def test_config_years(self):
        """Check config file for correct years"""

        config_years = set(pk_settings.available_years)
        self.assertEqual(EXPECTED_YEARS, config_years)

    def test_config_ids(self):
        """Check config file for correct SuomiNet ids"""

        config_ids = set(pk_settings.receivers)
        self.assertEqual(EXPECTED_IDS, config_ids)


class CorrectReturnedYears(unittest.TestCase):
    """Test that the end user is returned data for the correct years"""

    def test_correct_measured_years(self):
        """Checks pwv_atm.measured_pwv() for missing years"""

        err_msg = 'No measured data for year {}.'
        for year in EXPECTED_YEARS:
            measured_data = pwv_atm.measured_pwv(year)
            self.assertTrue(measured_data, err_msg.format(year))

    def test_correct_modeled_years(self):
        """Checks pwv_atm.modeled_pwv() for missing years"""

        err_msg = 'No modeled data for year {}.'
        for year in EXPECTED_YEARS:
            modeled_data = pwv_atm.modeled_pwv(year)
            self.assertTrue(modeled_data, err_msg.format(year))

    def test_removed_bad_kitt_data(self):
        """Test for the removal of Kitt Peak data from jan through mar 2016"""

        data_2016 = pwv_atm.measured_pwv(2016)
        april_2016 = datetime(2016, 4, 1, tzinfo=utc)
        bad_data = data_2016[data_2016['date'] < april_2016]
        self.assertTrue(all(bad_data['KITT'].mask))
