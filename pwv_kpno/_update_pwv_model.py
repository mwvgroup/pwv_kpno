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
from scipy.odr import Model, RealData, ODR

from ._download_pwv_data import update_local_data
from ._read_pwv_data import _get_measured_data
from ._settings import Settings, PWV_MODEL_PATH

__author__ = 'Daniel Perrefort'
__copyright__ = 'Copyright 2017, Daniel Perrefort'

__license__ = 'GPL V3'
__email__ = 'djperrefort@pitt.edu'
__status__ = 'Development'

CURRENT_LOCATION = Settings().current_location


def _linear_func(params, x):
    """Apply a linear function to a given array

    Args:
        params (tuple): The slope and intercept of the linear function
        x      (Array): The data to be mapped by the linear function

    Returns:
        params[0] * x + params[1]
    """

    return np.poly1d(params)(x)


def _gen_pwv_model(x, y, sx, sy):
    """Optimize and apply a linear regression

    Generates a linear model f using orthogonal distance regression and returns
    the applied model f(x)

    Args:
        x  (Column): The independent variable of the regression
        y  (Column): The dependent variable of the regression
        x  (Column): Standard deviations of x
        y  (Column): Standard deviations of y

    Returns:
        The applied linear regression on x as a masked array
    """

    # Identify rows with data for both KITT and receiver
    primary_index = np.logical_not(y.mask)
    receiver_index = np.logical_not(x.mask)
    matching_indices = np.logical_and(primary_index, receiver_index)

    # Create objects for orthogonal distance regression (ODR)
    linear_model = Model(_linear_func)
    data = RealData(x=x[matching_indices],
                    y=y[matching_indices],
                    sx=sx[matching_indices],
                    sy=sy[matching_indices])

    odr = ODR(data, linear_model, beta0=[1., 0.])
    fit_results = odr.run()

    applied_fit = _linear_func(fit_results.beta, x)
    applied_fit = np.round(applied_fit, 1)
    applied_fit = np.ma.masked_where(x.mask, applied_fit)

    return applied_fit


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
    primary = CURRENT_LOCATION.primary_receiver
    receiver_list = CURRENT_LOCATION.enabled_receivers

    # Generate the fit parameters
    site_models = []
    for receiver in receiver_list:
        if receiver != primary:
            modeled_pwv = _gen_pwv_model(x=pwv_data[receiver],
                                         y=pwv_data[primary],
                                         sx=pwv_data[receiver + '_err'],
                                         sy=pwv_data[primary + '_err'])

            site_models.append(modeled_pwv)

    # Supplement KITT data with averaged fits
    avg_pwv = np.ma.average(site_models, axis=0)
    sup_data = np.ma.where(pwv_data[primary].mask, avg_pwv, pwv_data[primary])

    out = Table([pwv_data['date'], sup_data, pwv_data['KITT_err']],
                names=['date', 'pwv', 'pwv_err'])

    out = out[out['pwv'] > 0]
    out['pwv'] = np.round(out['pwv'], 2)
    out['pwv_err'] = np.round(out['pwv_err'], 2)

    location_name = CURRENT_LOCATION.name
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
