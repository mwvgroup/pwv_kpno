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

"""This code creates a mock PWV model used for unit testing."""

from datetime import datetime, timedelta

from astropy.table import Table
from pytz import utc

from pwv_kpno._serve_pwv_data import timestamp

__authors__ = ['Daniel Perrefort']
__copyright__ = 'Copyright 2017, Daniel Perrefort'

__license__ = 'GPL V3'
__email__ = 'djperrefort@pitt.edu'
__status__ = 'Development'


def create_mock_pwv_model(year, gaps=None):
    """Create a mock model for the PWV level at Kitt Peak for airmass 1

    Return a table with the columns "date" and "pwv". Included dates span the
    given year in 30 minute increments and are represented as UTC timestamps.
    PWV values are calculated as the index of its position in the table mod 15.
    Gaps in the returned data can be included via the gaps argument.

    Args:
        year  (int): The year of the desired model
        gaps (list): [(start day as datetime, gap length in days as int), ]

    Returns:
        The modeled data set as an astropy table
    """

    start_date = datetime(year - 1, 12, 31, 23, 45, tzinfo=utc)
    end_date = datetime(year + 1, 1, 1, tzinfo=utc)
    total_time_intervals = (end_date - start_date).days * 24 * 60 // 30

    out_table = Table(names=['date', 'pwv'], dtype=[float, float])
    for i in range(total_time_intervals):
        start_date += timedelta(minutes=30)
        out_table.add_row([timestamp(start_date), i % 15])

    if gaps is not None:
        intervals = 48  # number of 30 min intervals in a day
        gap_indices = []

        for date, length in gaps:
            gap_start = (date - start_date).days
            gap_end = gap_start + length
            gap_range = range(gap_start * intervals, gap_end * intervals)
            gap_indices.extend(gap_range)

        out_table.remove_rows(gap_indices)

    return out_table
