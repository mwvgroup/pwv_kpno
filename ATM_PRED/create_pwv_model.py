#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
#
#    This file is part of the ATM_PRED module.
#
#    The ATM_PRED module is free software: you can redistribute it and/or
#    modify it under the terms of the GNU General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    The ATM_PRED module is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along
#    with the ATM_PRED module. If not, see <http://www.gnu.org/licenses/>.

""" This will be a module level description for this document
"""

from os.path import basename as _basename
import numpy as np
from astropy.time import Time

__author__ = 'Jessica Kroboth'
__email__ = ''
__copyright__ = 'Copyright 2017, Jessica Kroboth'
__license__ = 'GPL V3'
__status__ = 'Development'


def _get_data(path):
    """Returns SuomiNet data from a file path as a numpy array

    Expects data files from http://www.suominet.ucar.edu/data.html
    under the "Specific station - All year hourly" row. The returned
    array has column names 'date', 'pwv', 'pres', 'temp', and 'hum'.

    Args:
        path (str): File path to be read

    Returns:
        data (numpy.ndarray): Numpy array with data from file
    """

    data = np.genfromtxt(path, usecols=(1, 2, 7, 8, 9),
                         names=('date', 'pwv', 'pres', 'temp', 'hum'),
                         dtype=((np.str_, 16), float, float, float, float))

    data = np.unique(data)  # Remove duplicate entries
    return data


def _get_date_list(*data_arrays):
    """Construct a sorted list of unique dates from a collection of arrays

    Given multiple numpy arrays, create a sorted list of the unique dates found
    in all of the arrays. Expects arrays returned by '_get_data'.

    Args:
        data_arrays (numpy.ndarray): Numpy array returned by '_get_data'

    Returns:
        mjd (list): Sorted list of unique datetimes expressed in MJD
    """

    datetimes = np.concatenate([array['date'] for array in data_arrays])
    # [array['date'] for array in data_arrays] is a list of arrays each having
    # only the datetime info; np.concatenate combines these into a single array

    unique_datetimes = np.unique(datetimes)
    mjd = sorted([Time(t, format='isot').mjd for t in unique_datetimes])

    return mjd


def _pad_data(dates, data):
    """Pad and mask an array of PWV values to match a list of dates

    Given an array of PWV measurments and their corresponding datetimes, pad
    the array so that there is an entry for every datetime in a given list.
    Expects the first argument to be a return from 'get_dates' and the second
    second argument to be from '_get_data'.

    Args:
        dates (list): A list of unique datetimes returned by 'get_dates'
        data  (numpy.ndarray): An array returned by '_get_data'

    Returns:
        padded_data (list): A padded data array
    """

    mask, pwv_list = [], []

    # Get the times for the current site and express them in mjd format
    times_mjd = [Time(elt[0], format='isot').mjd for elt in data]

    for date in dates:
        if date in times_mjd:
            time = Time(date, format='mjd').isot[:-7]
            ind = np.where(data['date'] == time)
            pwv = data[ind]['pwv']

            if len(pwv) == 1 and pwv > 0:  # Eliminate cases with multiple values
                pwv_list.append(np.asscalar(pwv))
                mask.append(0)
                continue

        mask.append(1)
        pwv_list.append(1)  # Filler value

    padded_data = np.ma.masked_array(data=pwv_list, mask=mask)
    return padded_data


def combine_data(files):
    """Combine the data from a list of file paths into a single masked array
    """

    if not isinstance(files, list) or not files:
        raise Exception('Argument must be a non-empty list')

    # Seperate the kitt data from other data
    try:
        # Get file paths
        kitt_path = next(f for f in files if _basename(f)[:4].upper() == 'KITT')
        other_paths = list(set(files) - set([kitt_path]))

        # Read data from file paths
        kitt_data = _get_data(kitt_path)
        other_data = [_get_data(f) for f in other_paths]

        # Get list of unique dates
        dates = _get_date_list(kitt_data, *other_data)

        # Pad the KITT data.
        kitt_padded = _pad_data(dates, kitt_data)
        if not other_data:
            return kitt_padded

        # Pad the other data
        padded_list = [_pad_data(dates, site) for site in other_data]
        other_padded = np.ma.mean(padded_list, 0)

        # Combine the data arrays
        data, mask = [], []
        for i, val in enumerate(kitt_padded.data):
            if not kitt_padded.mask[i]:
                data.append(val)
                mask.append(False)

            elif not other_padded.mask[i]:
                data.append(other_padded.data[i])
                mask.append(False)

            else:
                data.append(1)
                mask.append(True)

        combined_array = np.ma.masked_array(data=data, mask=mask)

        return dates, combined_array

    except StopIteration:
        other_data = [_get_data(f) for f in files]
        dates = _get_date_list(*other_data)
        padded_list = [_pad_data(dates, site) for site in other_data]
        other_padded = np.ma.mean(padded_list, 0)
        return dates, other_padded
