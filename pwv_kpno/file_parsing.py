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
#    along with pwv_kpno.  If not, see <http://www.gnu.org/licenses/>.

"""The ``file_parsing`` module is responsible for parsing files written
in the SuomiNet file format and applying data cuts to corresponding data.
"""

from datetime import datetime, timedelta
from pathlib import Path
from typing import Union

import numpy as np
from astropy.table import Table, unique

from .types import PathLike


@np.vectorize
def _suomi_date_to_timestamp(year: int, days: Union[str, float]) -> float:
    """Convert the SuomiNet date format into UTC timestamp

    SuomiNet dates are stored as decimal days in a given year. For example,
    February 1st, 00:15 would be 36.01042.

    Args:
        year: The year of the desired timestamp
        days: The number of days that have passed since january 1st

    Returns:
        The seconds from UTC epoch to the provided date as a float
    """

    jan_1st = datetime(year=year, month=1, day=1)
    date = jan_1st + timedelta(days=float(days) - 1)

    # Correct for round off error in SuomiNet date format
    date = date.replace(second=0, microsecond=0)
    while date.minute % 5:
        date += timedelta(minutes=1)

    timestamp = (date - datetime(1970, 1, 1)).total_seconds()
    return timestamp


def apply_data_cuts(data: Table, data_cuts: dict, exclusive: bool) -> Table:
    """Apply data cuts from settings to a table of SuomiNet measurements

    Args:
        data: A table containing data from a SuomiNet data file
        data_cuts: Dict of tuples with (upper, lower) bounds for each column

    Returns:
        A copy of the data with applied data cuts
    """

    for param_name, cut_list in data_cuts.items():
        for start, end in cut_list:
            indices = (start < data[param_name]) & (data[param_name] < end)

            if exclusive:
                indices = ~indices

            data = data[indices]

    return data


def _parse_path_stem(path):
    """"""

    receiver_id = path.stem[:4]
    year = int(path.stem[-4:])
    return receiver_id, year


def read_suomi_data(path: PathLike, data_cuts: dict = None) -> Table:
    """Return PWV measurements from a SuomiNet data file as an astropy table

    Datetimes are expressed as UNIX timestamps and PWV is measured
    in millimeters.

    Data is removed from the array for dates where:
        1. The PWV level is negative (the GPS receiver is offline)
        2. Dates are duplicates with unequal measurements

    Args:
        path: File path to be read
        data_cuts: Dict of tuples with (upper, lower) bounds for each column

    Returns:
        An astropy Table with data from path
    """

    path = Path(path)
    receiver_id, year = _parse_path_stem(path)

    names = ['date', receiver_id, receiver_id + '_err', 'ZenithDelay',
             'SrfcPress', 'SrfcTemp', 'SrfcRH']

    data = np.genfromtxt(
        path,
        names=names,
        usecols=range(0, len(names)),
        dtype=[float for _ in names])

    data = Table(data)
    data = data[data[receiver_id] > 0]

    # SuomiNet rounds their error and can report an error of zero
    # We compensate by adding an error of 0.025
    data[receiver_id + '_err'] = np.round(data[receiver_id + '_err'] + 0.025, 3)

    if data:
        data = unique(data, keys='date', keep='none')
        data['date'] = _suomi_date_to_timestamp(year, data['date'])

    if data_cuts:
        # _apply_data_cuts expects column 'date' to have already
        # been converted from the suominet format to timestamps
        data = apply_data_cuts(data, data_cuts)

    return data