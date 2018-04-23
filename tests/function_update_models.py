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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with pwv_kpno. If not, see <http://www.gnu.org/licenses/>.

"""This file tests that SuomiNet data is downloaded and parsed correctly."""

from datetime import datetime

import unittest

from pwv_kpno._pwv_data import update_models

__author__ = 'Daniel Perrefort'
__copyright__ = 'Copyright 2017, Daniel Perrefort'

__license__ = 'GPL V3'
__email__ = 'djperrefort@gmail.com'
__status__ = 'Development'


class UpdateModelsArgs(unittest.TestCase):
    """Test pwv_kpno.update_models for raised errors due to bad arguments"""

    def test_argument_errors(self):
        """Test errors raised from function call with wrong argument types"""

        self.assertRaises(TypeError, update_models, "2011")
        self.assertRaises(TypeError, update_models, 2011.5)
        self.assertRaises(ValueError, update_models, 2009)
        self.assertRaises(ValueError, update_models, datetime.now().year + 1)

    def test_returns(self):
        """Tests that update_models returns the correct objects"""

        self.assertEquals(update_models(2010), [2010])
        self.assertEquals(update_models(2013), [2013])
        self.assertEquals(update_models(2015), [2015])
