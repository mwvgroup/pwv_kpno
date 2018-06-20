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
from scipy.odr import RealData, ODR, polynomial

from ._download_pwv_data import update_local_data
from ._settings import settings

__authors__ = ['Daniel Perrefort']
__copyright__ = 'Copyright 2017, Daniel Perrefort'

__license__ = 'GPL V3'
__email__ = 'djperrefort@pitt.edu'
__status__ = 'Development'


def _linear_regression(x, y, sx, sy):
    """Optimize and apply a linear regression using masked arrays

    Generates a linear fit f using orthogonal distance regression and returns
    the applied model f(x).

    Args:
        x  (MaskedArray): The independent variable of the regression
        y  (MaskedArray): The dependent variable of the regression
        sx  (MaskedArray): Standard deviations of x
        sy  (MaskedArray): Standard deviations of y

    Returns:
        The applied linear regression on x as a masked array
        The uncertainty in the applied linear regression as a masked array
    """

    x = np.ma.array(x)  # This type cast will propagate into returns
    y = np.ma.array(y)  # It also ensures that x, y have a .mask attribute

    # Fit data with orthogonal distance regression (ODR)
    indices = ~np.logical_or(x.mask, y.mask)
    data = RealData(x=x[indices], y=y[indices], sx=sx[indices], sy=sy[indices])
    odr = ODR(data, polynomial(1), beta0=[0., 1.])
    fit_results = odr.run()

    fit_pass = 'Numerical error detected' not in fit_results.stopreason
    assert fit_pass, 'Numerical error detected'

    b, m = fit_results.beta
    applied_fit = m * x + b
    applied_fit.mask = np.logical_or(x.mask, applied_fit <= 0)

    error = np.minimum(1 + 0.1 * x, 3)
    error.mask = applied_fit.mask

    return applied_fit, error


def _calc_avg_pwv_model(pwv_data, primary_rec):
    """Determines a PWV model using each off site receiver and averages them

    Args:
        pwv_data (Table): A table of pwv data

    Returns:
        A masked array of the averaged PWV model
        A masked array of the error in the averaged model
    """

    off_site_receivers = settings.off_site_recs
    receiver = off_site_receivers.pop()
    modeled_pwv, modeled_err = _linear_regression(
        x=pwv_data[receiver],
        y=pwv_data[primary_rec],
        sx=pwv_data[receiver + '_err'],
        sy=pwv_data[primary_rec + '_err']
    )

    for receiver in off_site_receivers:
        mod_pwv, mod_err = _linear_regression(
            x=pwv_data[receiver],
            y=pwv_data[primary_rec],
            sx=pwv_data[receiver + '_err'],
            sy=pwv_data[primary_rec + '_err']
        )

        modeled_pwv = np.ma.vstack((modeled_pwv, mod_pwv))
        modeled_err = np.ma.vstack((modeled_err, mod_err))

    # Average PWV models from different sites
    avg_pwv = np.ma.average(modeled_pwv, axis=0)
    sum_quad = np.ma.sum(modeled_err ** 2, axis=0)
    n = len(off_site_receivers) - np.sum(modeled_pwv.mask, axis=0)
    avg_pwv_err = np.ma.divide(np.ma.sqrt(sum_quad), n)
    avg_pwv_err.mask = avg_pwv.mask  # np.ma.divide throws off the mask

    return avg_pwv, avg_pwv_err


def _create_new_pwv_model(debug=False):
    """Create a new model for the PWV level at Kitt Peak

    Create first order polynomials relating the PWV measured by GPS receivers
    near Kitt Peak to the PWV measured at Kitt Peak (one per off site receiver)
    Use these polynomials to supplement PWV measurements taken at Kitt Peak for
    times when no Kitt Peak data is available. Write the supplemented PWV
    data to a csv file at PWV_TAB_DIR/measured.csv.
    """

    pwv_data = Table.read(settings._pwv_measred_path)
    if not settings.off_site_recs:
        return pwv_data

    primary_rec = settings.primary_rec
    avg_pwv, avg_pwv_err = _calc_avg_pwv_model(pwv_data, primary_rec)

    # Supplement KITT data with averaged fits
    mask = pwv_data[primary_rec].mask
    sup_data = np.ma.where(mask, avg_pwv, pwv_data[primary_rec])
    sup_err = np.ma.where(mask, avg_pwv_err, pwv_data[primary_rec + '_err'])
    sup_data.mask = np.logical_and(mask, avg_pwv.mask)

    # Remove any masked values
    indices = ~sup_data.mask
    dates = pwv_data['date'][indices]
    sup_data = np.round(sup_data[indices], 3)
    sup_err = np.round(sup_err[indices], 3)

    out = Table([dates, sup_data, sup_err], names=['date', 'pwv', 'pwv_err'])
    if debug:
        return out

    out.write(settings._pwv_model_path, overwrite=True)


def update_models(year=None, timeout=None):
    """Download data from SuomiNet and update the locally stored PWV model

    Update the modeled PWV column density for Kitt Peak by downloading new data
    releases from the SuomiNet website. If a year is provided, use only data
    for that year. If not, download any published data that is not available on
    the local machine.

    Args:
        year      (int): A Year from 2010 onward
        timeout (float): Optional seconds to wait while connecting to SuomiNet

    Returns:
        A list of years for which models where updated
    """

    # Check for valid args
    if not (isinstance(year, int) or year is None):
        raise TypeError("Argument 'year' must be an integer")

    if year is not None:
        if year < 2010:
            raise ValueError('Cannot update models for years prior to 2010')

        elif year > datetime.now().year:
            msg = 'Cannot update models for years greater than current year'
            raise ValueError(msg)

    # Update the local SuomiData and PWV models
    updated_years = sorted(update_local_data(year, timeout))
    _create_new_pwv_model()

    return updated_years
