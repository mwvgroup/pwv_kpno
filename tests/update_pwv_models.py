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

from astropy.table import Table
import numpy as np
import unittest

from pwv_kpno._update_pwv_model import _linear_regression
from pwv_kpno._update_pwv_model import update_models
from pwv_kpno._update_pwv_model import _fit_offsite_receiver

__author__ = 'Daniel Perrefort'
__copyright__ = 'Copyright 2017, Daniel Perrefort'

__license__ = 'GPL V3'
__email__ = 'djperrefort@pitt.edu'
__status__ = 'Development'


class LinearRegression(unittest.TestCase):
    """Tests for pwv_kpno._update_pwv_model._linear_regression"""

    def test_mask_handling(self):
        """Test returned values are masked correctly"""

        m, b = 5, 2  # Slope and y-intercept
        x = np.ma.array([1, 3, 100, 7, 9, -12, 13, 15, 17, 19])
        x.mask = [0, 0, 1, 0, 0, 1, 0, 0, 0, 0]
        y = m * x + b
        sy = sx = np.ma.zeros(x.shape) + .1

        fit, fit_err = _linear_regression(x, y, sx, sy)
        self.assertTrue(np.array_equal(x.mask, fit.mask),
                        'Incorrect mask returned for fit data')

        self.assertTrue(np.array_equal(fit.mask, fit_err.mask),
                        'Fit and fit error have different masks')

    def test_regression(self):
        """Test linear regression determines correct fit parameters"""

        m, b = 5, 2  # Slope and y-intercept
        x = np.arange(1, 20, 2)
        y = m * x + b
        sy = sx = np.zeros(x.shape) + .1

        fit, fit_err = _linear_regression(x, y, sx, sy)
        fit_matches_data = np.all(np.isclose(y, fit))
        self.assertTrue(fit_matches_data)


class FitOffsiteReceiver(unittest.TestCase):
    """Tests for pwv_kpno._update_pwv_model._fit_offsite_receiver"""

    def setUp(self):

        m, b = 5, 2  # Slope and y-intercept
        test_data = Table()
        test_data['primary'] = np.arange(-5, 20, 2)
        test_data['secondary'] = m * test_data['primary'] + b
        test_data['primary_err'] = np.zeros(13) + 0.1
        test_data['secondary_err'] = test_data['primary_err']

        self.mod_pwv, self.mod_err = \
            _fit_offsite_receiver(test_data, 'primary', 'secondary')

    def test_mask_neative_pwv(self):
        """Test for correct masking of negative PWV values"""

        indices = np.where(self.mod_pwv < 0)
        correct_mask = np.all(self.mod_pwv.mask[indices])
        self.assertTrue(correct_mask, 'Found unmasked negative values.')

    def test_same_returned_masks(self):
        """Test the returned PWV values and their errors have the same mask"""

        same_mask = np.array_equal(self.mod_pwv.mask, self.mod_err.mask)
        self.assertTrue(same_mask,
                        'Returned different masks for PWV and error values')

# Todo: test calc_avg_pwv_model (Test model for negative values)

class UpdateModelsArgs(unittest.TestCase):
    """Test update_models function for raised errors due to bad arguments"""

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
