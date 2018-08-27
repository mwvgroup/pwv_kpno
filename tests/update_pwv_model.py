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

from datetime import datetime

import numpy as np
import unittest

from pwv_kpno._update_pwv_model import _create_new_pwv_model
from pwv_kpno._update_pwv_model import _linear_regression
from pwv_kpno._update_pwv_model import update_models

__authors__ = ['Daniel Perrefort']
__copyright__ = 'Copyright 2017, Daniel Perrefort'

__license__ = 'GPL V3'
__email__ = 'djperrefort@pitt.edu'
__status__ = 'Development'


class LinearRegression(unittest.TestCase):
    """Tests for pwv_kpno._update_pwv_model._linear_regression"""

    def test_mask_handling(self):
        """Test returned values are masked correctly"""

        m, b = 5, 2  # Slope and y-intercept
        x = np.ma.array([1, 7, 9, 100, -2, -12])
        x.mask = [0, 0, 0, 0, 1, 1]
        y = m * x + b
        sy = sx = np.ma.zeros(x.shape) + .1

        fit, fit_err = _linear_regression(x, y, sx, sy)
        self.assertTrue(np.array_equal(x.mask, fit.mask),
                        'Incorrect mask returned for fit data')

        self.assertTrue(np.array_equal(fit.mask, fit_err.mask),
                        'Fit and fit error have different masks')

    def test_regression(self):
        """Test linear regression determines correct fit parameters"""

        x = np.ma.arange(1, 20, 2)
        x.mask = np.zeros(x.shape)

        m, b = 5, 2  # Slope and y-intercept
        y = m * x + b
        sy = sx = np.zeros(x.shape) + .1

        fit, fit_err = _linear_regression(x, y, sx, sy)
        fit_matches_data = np.all(np.isclose(y, fit))
        self.assertTrue(fit_matches_data)


class CalcAvgPwvModel(unittest.TestCase):
    """Tests for pwv_kpno._update_pwv_model._create_new_pwv_model"""

    def test_positive_pwv(self):
        """Test all PWV values are >= 0"""

        model = _create_new_pwv_model(debug=True)
        are_negative_values = np.any(model['pwv'] <= 0)
        self.assertFalse(are_negative_values)


class UpdateModelsArgs(unittest.TestCase):
    """Test update_models function for raised errors due to bad arguments"""

    def test_argument_errors(self):
        """Test errors raised from function call with wrong argument types"""

        self.assertRaises(TypeError, update_models, "2011")
        self.assertRaises(TypeError, update_models, 2011.5)
        self.assertRaises(ValueError, update_models, 2009)
        self.assertRaises(ValueError, update_models, datetime.now().year + 1)
