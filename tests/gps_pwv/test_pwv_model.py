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


"""Tests for the ``pwv_kpno.gps_pwv.PWVModel`` class"""

from pathlib import Path
from unittest import TestCase
import pandas as pd
import numpy as np

from pwv_kpno.gps_pwv import PWVModel, search_data_table
from tests.utils import TestWithCleanEnv

TEST_DATA_DIR = Path(__file__).parent / 'testing_data'


class AttributeAccess(TestCase):
    """Test receiver values for the ``PWVModel`` are read only"""

    def setUp(self):
        self.primary = 'REC1'
        self.secondaries = {'REC2', 'REC3'}
        self.receiver = PWVModel(primary=self.primary, secondaries=self.secondaries)

    def test_primary_rec_accessible(self):
        """Test the primary receiver is accessible through the ``primary`` attribute"""

        self.assertEqual(self.primary, self.receiver.primary)

    def test_primary_rec_not_settable(self):
        """Test the ``primary`` attribute has no setter"""

        with self.assertRaises(AttributeError):
            self.receiver.primary = 'NEW_PRIMARY'

    def test_secondary_recs_accessible(self):
        """Test the secondary receivers are accessible through the ``secondaries`` attribute"""

        self.assertEqual(self.secondaries, self.receiver.secondaries)

    def test_secondary_recs_not_settable(self):
        """Test the ``secondaries`` attribute has no setter"""

        with self.assertRaises(AttributeError):
            self.receiver.secondaries = {'NEW_REC_1', 'NEW_REC_2'}


@TestWithCleanEnv(TEST_DATA_DIR)
class ModeledPWV(TestCase):
    """Tests for the 'PWVModel.modeled_pwv' function"""

    def setUp(self):
        self.receiver = PWVModel('KITT')

    def test_filtering_by_args(self):
        """Test returned dates are filtered by kwarg arguments"""

        search_kwargs = {'year': 2010, 'month': 7, 'day': 21, 'hour': 5}
        full_table = self.receiver.modeled_pwv()
        searched_table = search_data_table(full_table, **search_kwargs)
        returned_table = self.receiver.modeled_pwv(**search_kwargs)
        pd.testing.assert_frame_equal(searched_table, returned_table)

    def test_returned_column_names(self):
        """Test returned table has two columns named ``date`` and the
        primary receiver Id
        """

        returned_column_order = self.receiver.modeled_pwv().columns.values
        expected_col_order = ['PWV', 'PWVErr']
        np.testing.assert_equal(expected_col_order, returned_column_order)


class PWVDateInterpolation(TestCase):
    """Tests for the ``PWVModel.interp_pwv_date`` function"""

    def setUp(self):
        self.receiver = PWVModel('KITT')

    def test_error_for_out_of_bounds(self):
        """Test a value error is raised when interpolating for an out of bounds date"""

        max_date = max(self.receiver.modeled_pwv()['date'])
        out_of_bounds_date = max_date + 1
        self.assertRaises(ValueError, self.receiver.interp_pwv_date, out_of_bounds_date)

    def test_error_for_no_nearby_data(self):
        """Test an error is raised if no modeled PWV values are available
        within a given range of the requested datetime
        """

        self.fail()

    def test_recovers_model_at_grid_points(self):
        """Test interpolation recovers grid points of the modeled PWV"""

        modeled_pwv = self.receiver.modeled_pwv()
        target_date = modeled_pwv['date'][0]
        target_pwv = modeled_pwv['pwv'][0]
        interpolated_pwv = self.receiver.interp_pwv_date(target_date)
        self.assertEqual(target_pwv, interpolated_pwv)

    def test_return_matches_linear_interpolation(self):
        """Test the returned PWV is consistent with a linear interpolation"""

        modeled_pwv = self.receiver.modeled_pwv()
        test_date = 1594467199  # July 11th, 2020
        expected_pwv = np.interp(test_date, modeled_pwv['date'], modeled_pwv['pwv'])
        returned_pwv = self.receiver.interp_pwv_date(test_date)
        self.assertEqual(expected_pwv, returned_pwv)


class Repr(TestCase):
    """Tests for the string representation of ``PWVModel``"""

    def test_can_be_evaluated(self):
        """Test the class representation can be evaluated"""

        primary = 'PRIM'
        secondaries = {'SEC1', 'SEC2'}
        receiver = eval(repr(PWVModel(primary, secondaries)))

        self.assertEqual(primary, receiver.primary, 'Incorrect primary receiver.')
        self.assertEqual(secondaries, receiver.secondaries, 'Incorrect secondary receivers.')
