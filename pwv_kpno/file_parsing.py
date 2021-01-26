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

"""The ``file_parsing`` module is responsible for parsing plain text files
written in the SuomiNet file format. For more information on the recommended
way to access locally available SuomiNet data, see the :ref:`gps_pwv` module.

Module API
----------
"""

from datetime import datetime, timedelta
from functools import partial
from pathlib import Path
from typing import Tuple, Union

import numpy as np
import pandas as pd

from .types import PathLike


class SuomiFileParser:
    """File parser for data written in the SuomiNet file format"""

    def __new__(cls, path: PathLike) -> pd.DataFrame:
        # noinspection PyArgumentList,PyTypeChecker
        return cls.__call__(cls, path)

    @staticmethod
    def suomi_date_to_timestamp(year: int, days: Union[str, float]) -> float:
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

    @staticmethod
    def parse_path_stem(path: Path) -> Tuple[str, int]:
        """Return the receiver Id and year from a SuomiNet file name

        Args:
            path: Path of the file

        Returns:
            - The receiver Id
            - The year
        """

        receiver_id = path.stem[:4]
        year = int(path.stem[-4:])
        return receiver_id, year

    def __call__(self, path: PathLike) -> pd.DataFrame:
        """Return PWV measurements from a SuomiNet data file as a pandas DataFrame

        Datetimes are expressed as UNIX timestamps and PWV is measured
        in millimeters.

        Data is removed from the array for dates where:
            1. The PWV level is negative (the GPS receiver is offline)
            2. Dates are duplicates with unequal measurements

        Args:
            path: File path to be read

        Returns:
            An pandas DataFrame with data from the specified path
        """

        path = Path(path)
        names = ['date', 'PWV', 'PWVErr', 'ZenithDelay', 'SrfcPress', 'SrfcTemp', 'SrfcRH']
        data = pd.read_csv(
            path,
            names=names,
            usecols=range(0, len(names)),
            delim_whitespace=True,
            index_col=False)

        # Remove masked PWV values, but not other masked data
        clean_data = data \
            .replace(-99.9, np.nan) \
            .replace({'PWV': -9.9, '*': -99.9}, {'PWV': np.nan}) \
            .dropna(subset=['PWV']) \
            .drop_duplicates(subset='date', keep=False) \
            .set_index('date')

        # Convert time values from SuomiNet format to UTC timestamps
        receiver_id, year = self.parse_path_stem(path)
        date_conversion = partial(self.suomi_date_to_timestamp, year)
        clean_data.index = clean_data.index.map(date_conversion)
        clean_data.index = pd.to_datetime(clean_data.index, unit='s', utc=True)

        # SuomiNet rounds their error and can report an error of zero
        # We compensate by adding an error of 0.025
        clean_data['PWVErr'] = np.round(clean_data['PWVErr'] + 0.025, 3)

        return clean_data
