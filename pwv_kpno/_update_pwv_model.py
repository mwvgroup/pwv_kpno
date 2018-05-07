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

"""This document updates the PWV model using new data downloaded from SuomiNet.
Linear functions are fitted to relate the PWV level at secondary locations
to the PWV level at the primary location. The resulting polynomials are then
used to supplement gaps in PWV measurements taken at the primary location.
"""

from datetime import datetime

from astropy.table import Table
import numpy as np

from ._download_pwv_data import update_local_data
from ._read_pwv_data import _get_measured_data
from ._settings import Settings, PWV_MODEL_PATH


def _update_pwv_model():
    """Create a new model for the PWV level at Kitt Peak

    Create first order polynomials relating the PWV measured by GPS receivers
    near Kitt Peak to the PWV measured at Kitt Peak (one per off site receiver)
    Use these polynomials to supplement PWV measurements taken at Kitt Peak for
    times when no Kitt Peak data is available. Write the supplemented PWV
    data to a csv file at PWV_TAB_DIR/measured.csv.
    """

    # Credit belongs to Jessica Kroboth for suggesting the use of a linear fit
    # to supplement PWV measurements when no Kitt Peak data is available.

    # Read the local PWV data from file
    pwv_data = _get_measured_data()
    current_location = Settings().current_location
    primary = current_location.primary_receiver
    receiver_list = current_location.enabled_receivers
    print(pwv_data.colnames)
    print(receiver_list)

    # Generate the fit parameters
    for receiver in receiver_list:
        if receiver != primary:
            # Identify rows with data for both KITT and receiver
            primary_index = np.logical_not(pwv_data[primary].mask)
            receiver_index = np.logical_not(pwv_data[receiver].mask)
            matching_indices = np.logical_and(primary_index, receiver_index)

            # Generate and apply a first order fit
            fit_data = pwv_data[primary, receiver][matching_indices]
            fit = np.polyfit(fit_data[receiver], fit_data[primary], deg=1)

            # np.poly1d does not maintain masks
            pwv_data[receiver + '_fit'] = np.poly1d(fit)(pwv_data[receiver])
            pwv_data[receiver + '_fit'].mask = pwv_data[receiver].mask

    # Average together the modeled PWV values from all receivers except KITT
    cols = [pwv_data[rec_name + '_fit'] for rec_name in receiver_list]
    avg_pwv = np.ma.average(cols, axis=0)

    # Supplement KITT data with averaged fits
    sup_data = np.ma.where(pwv_data[primary].mask, avg_pwv, pwv_data[primary])

    out = Table([pwv_data['date'], sup_data], names=['date', 'pwv'])
    out = out[out['pwv'] > 0]

    location_name = Settings().current_location.name
    out.write(PWV_MODEL_PATH.format(location_name), overwrite=True)


def update_models(year=None):
    """Download data from SuomiNet and update the locally stored PWV model

    Update the locally available SuomiNet data by downloading new data from
    the SuomiNet website. Use this data to create an updated model for the PWV
    level at Kitt Peak. If a year is provided, only update data for that year.
    If not, download any published data that is not available on the local
    machine. Data for years from 2010 through 2017 is included with this
    package version by default.

    Args:
        year (int): A Year from 2010 onward

    Returns:
        A list of years for which models where updated
    """

    # Check for valid args
    if not (isinstance(year, int) or year is None):
        raise TypeError("Argument 'year' must be an integer")

    if isinstance(year, int):
        if year < 2010:
            raise ValueError('Cannot update models for years prior to 2010')

        elif year > datetime.now().year:
            msg = 'Cannot update models for years greater than current year'
            raise ValueError(msg)

    # Update the local SuomiData and PWV models
    updated_years = update_local_data(year)
    _update_pwv_model()
    return sorted(updated_years)