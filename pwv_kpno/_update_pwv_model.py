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
from ._settings import Settings

__author__ = 'Daniel Perrefort'
__copyright__ = 'Copyright 2017, Daniel Perrefort'

__license__ = 'GPL V3'
__email__ = 'djperrefort@pitt.edu'
__status__ = 'Development'

SETTINGS = Settings()


def _linear_regression(x, y, sx, sy):
    """Optimize and apply a linear regression

    Generates a linear fit f using orthogonal distance regression and returns
    the applied model f(x).

    Args:
        x  (ndarray): The independent variable of the regression
        y  (ndarray): The dependent variable of the regression
        x  (ndarray): Standard deviations of x
        y  (ndarray): Standard deviations of y

    Returns:
        The applied linear regression on x as a masked array
        The uncertainty in the applied linear regression as a masked array
    """

    # Identify rows with data for both KITT and receiver
    indices = ~np.logical_or(x.mask, y.mask)
    data = RealData(x=x[indices], y=y[indices], sx=sx[indices], sy=sy[indices])

    # Fit data with orthogonal distance regression (ODR)
    linear_func = lambda params, xx: np.poly1d(params)(xx)
    linear_model = Model(linear_func)
    odr = ODR(data, linear_model, beta0=[1., 0.])
    fit_results = odr.run()

    applied_fit = linear_func(fit_results.beta, x)
    applied_fit = np.ma.masked_where(x.mask, applied_fit)

    m, b = fit_results.beta
    sm, sb = fit_results.sd_beta
    error = np.sqrt((x * sm) ** 2 + (m * sx) ** 2 + sb ** 2)

    applied_fit.mask = np.logical_or(applied_fit.mask, applied_fit < 0)
    error.mask = np.logical_or(error.mask, applied_fit < 0)
    assert np.array_equal(applied_fit.mask, error.mask)

    return applied_fit, error


def _fit_offsite_receiver(pwv_data, receiver):
    """Model the primary location's PWV using data from a secondary receiver

    Args:
        pwv_data (Table): A table of PWV measurements
        receiver   (str): SuomiNet id code for the secondary receiver

    Returns:
        The modeled PWV level at the primary location
        The error in the modeled values
    """

    primary_rec = SETTINGS.primary_receiver
    assert primary_rec != receiver, 'Cannot fit primary receiver to itself.'
    mod_pwv, mod_err = _linear_regression(x=pwv_data[receiver],
                                          y=pwv_data[primary_rec],
                                          sx=pwv_data[receiver + '_err'],
                                          sy=pwv_data[primary_rec + '_err'])

    mod_pwv.mask = np.logical_and(mod_pwv.mask, [mod_pwv < 0])
    mod_err.mask = mod_pwv.mask  # _linear_regression returns identical masks

    return mod_pwv, mod_err


def _update_pwv_model():
    """Create a new model for the PWV level at Kitt Peak

    Create first order polynomials relating the PWV measured by GPS receivers
    near Kitt Peak to the PWV measured at Kitt Peak (one per off site receiver)
    Use these polynomials to supplement PWV measurements taken at Kitt Peak for
    times when no Kitt Peak data is available. Write the supplemented PWV
    data to a csv file at PWV_TAB_DIR/measured.csv.
    """

    pwv_data = _get_measured_data()
    off_site_receivers = SETTINGS.off_site_receivers
    if not off_site_receivers:
        return pwv_data

    receiver = off_site_receivers.pop()
    modeled_pwv, modeled_err = _fit_offsite_receiver(pwv_data, receiver)
    for receiver in off_site_receivers:
        mod_pwv, mod_err = _fit_offsite_receiver(pwv_data, receiver)
        modeled_pwv = np.ma.vstack((modeled_pwv, mod_pwv))
        modeled_err = np.ma.vstack((modeled_err, mod_err))

    # Average PWV models from different sites
    avg_pwv = np.average(modeled_pwv, axis=0)
    sum_quad = np.ma.sum(modeled_err ** 2, axis=0)
    n = len(off_site_receivers) - np.ma.sum(modeled_pwv.mask, axis=0)
    avg_pwv_err = np.ma.divide(np.ma.sqrt(sum_quad), n)
    avg_pwv_err.mask = avg_pwv.mask

    # Supplement KITT data with averaged fits
    primary_rec = SETTINGS.primary_receiver
    mask = pwv_data[primary_rec].mask
    sup_data = np.ma.where(mask, avg_pwv, pwv_data[primary_rec])
    sup_err = np.ma.where(mask, avg_pwv_err, pwv_data[primary_rec + '_err'])

    # Remove any masked values
    indices = ~sup_data.mask
    dates = pwv_data['date'][indices]
    sup_data = np.round(sup_data[indices], 2)
    sup_err = np.round(sup_err[indices], 2)

    out = Table([dates, sup_data, sup_err], names=['date', 'pwv', 'pwv_err'])
    out.write(SETTINGS._pwv_model_path, overwrite=True)


def update_models(year=None):
    """Download data from SuomiNet and update the locally stored PWV model

    Update the modeled PWV column density for Kitt Peak by downloading new data
    releases from the SuomiNet website. If a year is provided, use only data
    for that year. If not, download any published data that is not available on
    the local machine.

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
    updated_years = sorted(update_local_data(year))
    _update_pwv_model()

    return updated_years
