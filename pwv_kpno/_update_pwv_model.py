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

"""This document updates the modeled PWV using new data downloaded from
SuomiNet. Linear functions are fitted to relate the PWV level at secondary
locations to the PWV level at the primary location. The resulting polynomials
are then used to supplement gaps in PWV measurements taken at the primary
location.
"""

import warnings
from datetime import datetime

import numpy as np
from astropy.table import Table
from scipy.odr import ODR, RealData, polynomial

from ._download_pwv_data import update_local_data
from .package_settings import settings

__authors__ = ['Daniel Perrefort']
__copyright__ = 'Copyright 2017, Daniel Perrefort'

__license__ = 'GPL V3'
__email__ = 'djperrefort@pitt.edu'
__status__ = 'Release'

warnings.filterwarnings("ignore",
                        message='Empty data detected for ODR instance.')


def _linear_regression(x, y, sx, sy):
    """Optimize and apply a linear regression using masked arrays

    Generates a linear fit f using orthogonal distance regression and returns
    the applied model f(x). If y is completely masked, return y and sy.

    Args:
        x   (MaskedArray): The independent variable of the regression
        y   (MaskedArray): The dependent variable of the regression
        sx  (MaskedArray): Standard deviations of x
        sy  (MaskedArray): Standard deviations of y

    Returns:
        The applied linear regression on x as a masked array
        The uncertainty in the applied linear regression as a masked array
    """

    x = np.ma.array(x)  # This type cast will propagate into returns
    y = np.ma.array(y)  # It also ensures that x, y have a .mask attribute

    if y.mask.all():
        return y, sy

    # Fit data with orthogonal distance regression (ODR)
    indices = ~np.logical_or(x.mask, y.mask)
    data = RealData(x=x[indices], y=y[indices], sx=sx[indices], sy=sy[indices])
    odr = ODR(data, polynomial(1), beta0=[0., 1.])
    fit_results = odr.run()

    fit_fail = 'Numerical error detected' in fit_results.stopreason
    if fit_fail:
        raise RuntimeError(fit_results.stopreason)

    # Apply the linear regression
    b, m = fit_results.beta
    applied_fit = m * x + b
    applied_fit.mask = np.logical_or(x.mask, applied_fit <= 0)

    std = np.ma.std(y[indices] - m * x[indices] - b)
    error = np.ma.zeros(applied_fit.shape) + std
    error.mask = applied_fit.mask

    return applied_fit, error


def _calc_avg_pwv_model(pwv_data, primary_rec):
    """Determines a PWV model using each off site receiver and averages them

    Args:
        pwv_data (Table): A table of pwv measurements

    Returns:
        A masked array of the averaged PWV model
        A masked array of the error in the averaged model
    """

    off_site_receivers = settings.supplement_rec

    pwv_arrays, err_arrays = [], []
    for receiver in off_site_receivers:
        mod_pwv, mod_err = _linear_regression(
            x=pwv_data[receiver],
            y=pwv_data[primary_rec],
            sx=pwv_data[receiver + '_err'],
            sy=pwv_data[primary_rec + '_err']
        )
        pwv_arrays.append(mod_pwv)
        err_arrays.append(mod_err)

    modeled_pwv = np.ma.vstack(pwv_arrays)
    modeled_err = np.ma.vstack(err_arrays)

    if np.all(modeled_pwv.mask):
        warnings.warn('No overlapping PWV data between primary and secondary '
                      'receivers. Cannot model PWV for times when primary '
                      'receiver is offline')

    # Average PWV models from different sites
    avg_pwv = np.ma.average(modeled_pwv, axis=0)
    sum_quad = np.ma.sum(modeled_err ** 2, axis=0)
    n = len(off_site_receivers) - np.sum(modeled_pwv.mask, axis=0)
    avg_pwv_err = np.ma.divide(np.ma.sqrt(sum_quad), n)
    avg_pwv_err.mask = avg_pwv.mask  # np.ma.divide throws off the mask

    return avg_pwv, avg_pwv_err


def _create_new_pwv_model(debug=False):
    """Create a new model for the PWV level at the current site

    Create first order polynomials relating the PWV measured by the current
    site's supplementary receivers to its primary receiver (one per off site
    receiver). Use these polynomials to supplement PWV measurements taken by
    the primary receiver times when it is unavailable. Write the supplemented
    PWV data to a csv file at settings._pwv_modeled_path.
    """

    pwv_data = Table.read(settings._pwv_measured_path)
    if not settings.supplement_rec:
        return pwv_data

    primary_rec = settings.primary_rec
    avg_pwv, avg_pwv_err = _calc_avg_pwv_model(pwv_data, primary_rec)

    # Supplement primary data with averaged fits
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

    out.write(settings._pwv_modeled_path, overwrite=True)


def _get_years_to_download(years=None):
    """Return a list of years to download data for

    If the years argument is not provided, include all years from the earliest
    available data onward. If no data is available then start from 2010.

    If a list of years is provided, return the list minus any years that are
    already downloaded. Always include the most recent year in the provided
    list.

    Args:
        years (list): A list of years that a user is requesting to download

    Returns:
        A list of years without data already on the current machine
    """

    available_years = settings._downloaded_years
    current_year = datetime.now().year
    if years is None:
        if not available_years:
            starting_year = 2010
            ending_year = datetime.now().year

        else:
            starting_year = min(available_years)
            ending_year = max(available_years)

        all_years = set(range(starting_year, current_year + 1))
        download_years = all_years - set(available_years)
        download_years.add(ending_year)

    else:
        if any((year > current_year for year in years)):
            raise ValueError(
                'Cannot update models for years greater than the current year.'
            )

        download_years = years

    return sorted(download_years)


def update_models(years=None, timeout=None):
    # type: (list, float) -> list[int]
    """Download data from SuomiNet and update the locally stored PWV model

    Update the modeled PWV column density for the current site by downloading
    new data releases from the SuomiNet website. Suominet organizes its data
    by year. If the years argument is not provided, download any missing
    data from the earliest available date on the current machine through the
    present day.

    Args:
        years    (list): A list of integer years to download
        timeout (float): Optional seconds to wait while connecting to SuomiNet

    Returns:
        A list of years for which models where updated
    """

    download_years = _get_years_to_download(years)

    updated_years = []
    for year in download_years:
        if update_local_data(year, timeout):
            updated_years.append(year)

    _create_new_pwv_model()
    all_years = settings._downloaded_years + updated_years
    settings._replace_years(all_years)
    return updated_years
