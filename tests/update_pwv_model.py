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

import warnings
from datetime import datetime
from unittest import TestCase

import numpy as np
import requests

from pwv_kpno._update_pwv_model import _create_new_pwv_model
from pwv_kpno._update_pwv_model import _linear_regression
from pwv_kpno._update_pwv_model import update_models

__authors__ = ['Daniel Perrefort']
__copyright__ = 'Copyright 2017, Daniel Perrefort'

__license__ = 'GPL V3'
__email__ = 'djperrefort@pitt.edu'
__status__ = 'Release'

try:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        req = requests.get('http://www.suominet.ucar.edu', verify=False)
    SUOMINET_OFFLINE = req.status_code != 200

except requests.exceptions.ConnectionError:
    SUOMINET_OFFLINE = True


class LinearRegression(TestCase):
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


class CalcAvgPwvModel(TestCase):
    """Tests for pwv_kpno._update_pwv_model._create_new_pwv_model"""

    def test_positive_pwv(self):
        """Test all PWV values are >= 0"""

        model = _create_new_pwv_model(debug=True)
        are_negative_values = np.any(model['pwv'] <= 0)
        self.assertFalse(are_negative_values)


class UpdateModelsArgs(TestCase):
    """Test update_models function for raised errors due to bad arguments"""

    @classmethod
    def setUpClass(cls):
        cls.call_1_years = update_models()
        cls.call_2_years = update_models()

    def test_future_year(self):
        """
        An error should be raised if the user trys to update data
        from the future
        """

        self.assertRaises(ValueError, update_models, [datetime.now().year + 1])

    def test_succesive_calls(self):
        """
        First call should return [current year - 1, current year]
        second call should return [current year]
        """

        current_year = datetime.now().year
        expected_return_1 = [current_year - 1, current_year]
        expected_return_2 = [current_year]

        try:
            # Python 2.7
            self.assertItemsEqual(self.call_1_years, expected_return_1)
            self.assertItemsEqual(self.call_2_years, expected_return_2)

        except AttributeError:
            # Python 3
            self.assertCountEqual(self.call_1_years, expected_return_1)
            self.assertCountEqual(self.call_2_years, expected_return_2)

    def test_empy_years_arg(self):
        """When passed an empty list update_models should return []"""

        years_list = update_models([])
        try:
            # Python 2.7
            self.assertItemsEqual(years_list, [])

        except AttributeError:
            # Python 3
            self.assertCountEqual(years_list, [])
