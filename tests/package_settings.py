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

"""This file provides tests for the pwv_kpno.package_settings.Settings class"""

from unittest import TestCase

from pwv_kpno.package_settings import Settings

__authors__ = ['Daniel Perrefort']
__copyright__ = 'Copyright 2017, Daniel Perrefort'

__license__ = 'GPL V3'
__email__ = 'djperrefort@pitt.edu'
__status__ = 'Release'


class SettingErrors(TestCase):
    """Test that the Settings class raises errors when appropriate"""

    @classmethod
    def setUpClass(cls):
        cls.settings = Settings()

    def test_change_site_name(self):
        """site_name should be a protected property"""

        with self.assertRaises(RuntimeError):
            self.settings.site_name = 'dummy string'

    def test_change_primary_rec(self):
        """primary_rec should be a protected property"""

        with self.assertRaises(RuntimeError):
            self.settings.primary_rec = 'dummy string'

    def test_set_site_does_not_exist(self):
        """Test for setting pwv_kpno to model a site with no settings"""

        self.assertRaises(ValueError, self.settings.set_site, 'dummy string')
