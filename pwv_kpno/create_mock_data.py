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

"""This code creates mock data used for unit testing."""

import os
from datetime import datetime, timedelta

from astropy.table import Table


def create_mock_pwv_model(out_path, overwrite=True):
    """Creates a file of demo PWV values for unit testing

    Creates a table with the columns "date" and "pwv" and writes it to the
    given path. Dates span 2010 in 30 minute increments (just like actual
    SuomiNet data) with data gaps of 1, 2, 3, and 4 days. All values in the
    "pwv" column are set to 25.0.

    Args:
        out_path  (str): The output path of
        overwrite (bool): Whether to overwrite existing files
    """

    start_date = datetime(2009, 12, 31, 23, 45)
    end_date = datetime(2011, 1, 1)
    total_time_intervals = (end_date - start_date).days * 24 * 60 // 30

    out_table = Table(names=['date', 'pwv'], dtype=[datetime, float])
    for i in range(total_time_intervals):
        start_date += timedelta(minutes=30)
        out_table.add_row([start_date.timestamp(), 25.0])

    day = 24 * 2  # number of 30 min intervals in a day
    gap_indices = []
    gap_indices.extend(range(10 * day, 11 * day))  # 01-11
    gap_indices.extend(range(40 * day, 42 * day))  # 02-10 through 02-11
    gap_indices.extend(range(100 * day, 103 * day))  # 04-11 through 04-13
    gap_indices.extend(range(215 * day, 219 * day))  # 08-04 through 04-07

    out_table.remove_rows(gap_indices)
    out_table.write(out_path, overwrite=overwrite)


def create_mock_suominet_data(out_dir):

    line_format = '{:0.5f}  25\n'
    intervals_in_day = 48  # number of 30 min intervals in a day

    kitt_out_file = open(os.path.join(out_dir, 'KITThr_2010'), 'w')
    azam_out_file = open(os.path.join(out_dir, 'AZAMhr_2010'), 'w')
    p014_out_file = open(os.path.join(out_dir, 'P014hr_2010'), 'w')


    for integer_day in range(1, 366):
        for i in range(intervals_in_day):
            decimal_days = (15 + 30 * i) / (60 * 24)
            date = integer_day + round(decimal_days, 5)
            kitt_out_file.write(line_format.format(date))
            azam_out_file.write(line_format.format(date))
            p014_out_file.write(line_format.format(date))


if __name__ == '__main__':
    create_mock_pwv_model('./mock_pwv_model.csv')
    create_mock_suominet_data('.')
