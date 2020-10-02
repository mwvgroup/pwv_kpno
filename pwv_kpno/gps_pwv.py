# !/usr/bin/env python3
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

"""The ``gps_pwv`` module is responsible for serving SuomiNet GPS data at a
given location. This includes location specific weather data (e.g., temperature
and pressure measurements) and PWV concentrations along the line of sight.

Module API
----------
"""

import warnings
from copy import deepcopy, copy
from typing import Tuple, Union, Collection, List, Dict

import numpy as np
import pandas as pd

from . import _utils as utils
from .downloads import DownloadManager
from .file_parsing import SuomiFileParser
from .types import DataCuts, NumpyArgument, NumpyReturn, Path


class GPSReceiver:
    """Data access object for weather data taken by a SuomiNet GPS system"""

    def __init__(self, receiver_id: str, data_cuts: DataCuts = None, cache_data=True) -> None:
        """Data access object for weather data taken by a SuomiNet GPS system

        The optional ``data_cuts`` argument is expected as a dictionary mapping
        column names to a list of tuples [(cut start, cut end), ...]. Data
        cuts on ``date`` values are exclusive. All other data cuts are inclusive.


        Args:
            receiver_id: SuomiNet Id of a GPS receiver (e.g., KITT)
            data_cuts: Only include data in the given ranges
            cache_data: Optionally keep a cached copy of the data in memory
        """

        self._rec_id = receiver_id.upper()
        self._data_cuts = data_cuts if data_cuts else dict()
        self._cache_data = cache_data
        self._cache = None

    @property
    def receiver_id(self) -> str:
        """SuomiNet Id of the current GPS receiver"""

        return copy(self._rec_id)

    @property
    def data_cuts(self) -> DataCuts:
        """Dictionary of data cuts on returned weather data"""

        return deepcopy(self._data_cuts)

    @data_cuts.setter
    def data_cuts(self, val: DataCuts) -> None:
        """Dictionary of data cuts on returned weather data"""

        self.clear_cache(suppress_errors=True)
        self._data_cuts = val

    @property
    def cache_data(self) -> bool:
        """Boolean indicating whether to store a copy of loaded data in memory"""

        return self._cache_data

    @cache_data.setter
    def cache_data(self, val: bool) -> None:
        """Boolean indicating whether to store a copy of loaded data in memory"""

        if not val:  # Clear any cached data
            self.clear_cache()

        self._cache_data = val

    def clear_cache(self, suppress_errors: bool = False) -> None:
        """Clear any cached data from memory

        Raises an error if caching is turned off for current instance.

        Args:
            suppress_errors: Ignore any errors that are raised

        Raises:
            RuntimeError
        """

        if not (self.cache_data or suppress_errors):
            raise RuntimeError(
                'Data caching is disabled for this instance. '
                'Did you remember to specify `cache_data` at init?')

        self._cache = None

    def _load_rec_data(self) -> pd.DataFrame:
        """Load all available data for the GPS receiver id

        Data from daily data releases is prioritized over hourly data releases

        Returns:
            A pandas DataFrame of SuomiNet weather data
        """

        directory = DownloadManager().data_dir

        # Data release types ordered in terms of priority
        # Prefer global data over daily data over hourly data
        data_types = ('gl', 'dy', 'hr')

        data = []  # Collector for DataFrames with data from each data type
        for dtype in data_types:
            global_files = list(directory.glob('{}{}_*.plt'.format(self._rec_id, dtype)))
            if global_files:
                data.append(pd.concat([SuomiFileParser(f) for f in global_files]))

        if data:
            combined_data = pd.concat(data)
            return combined_data.loc[~combined_data.index.duplicated(keep='first')]

        warnings.warn('No local data found for {}'.format(self._rec_id))

        return pd.DataFrame(columns=[
            'date', 'PWV', 'PWVErr',
            'ZenithDelay', 'SrfcPress', 'SrfcTemp', 'SrfcRH'
        ]).set_index('date')

    def _fetch_cached_data(self) -> pd.DataFrame:
        """Return data for the current GPS receiver. Use cached data if available.

        Returns:
            A pandas DataFrame with GPS weather data
        """

        if self.cache_data:
            if self._cache is None:
                self._cache = self._load_rec_data()

            return deepcopy(self._cache)

        return self._load_rec_data()

    def weather_data(self, year: int = None, month: int = None, day=None, hour=None, apply_cuts=True) -> pd.DataFrame:
        """Return a table of weather data taken by SuomiNet

        Args:
            year: The year of the desired PWV data
            month: The month of the desired PWV data
            day: The day of the desired PWV data
            hour: The hour of the desired PWV data in 24-hour format
            apply_cuts: Return data with data cuts applied

        Returns:
            A pandas DataFrame of modeled PWV values in mm
        """

        data = self._fetch_cached_data()
        if apply_cuts:
            data = utils.apply_data_cuts(data, self._data_cuts)

        return utils.search_data_table(data, year, month, day, hour)

    def check_downloaded_data(self) -> Dict[str, List[int]]:
        """Determine which years of data have been downloaded to the local machine

        Returns:
            A dictionary of the form {<release type>: <list of years>}
        """

        return DownloadManager().check_downloaded_data(self.receiver_id)

    def download_available_data(
            self, year: Union[int, Collection[int]] = None,
            timeout: float = None, force: bool = False, verbose: bool = True) -> None:
        """Download all available SuomiNet data for a given year

        Args:
            year: Year to download data for
            timeout: How long to wait before the request times out
            force: Execute download even if local data already exists
            verbose: Display progress bars for the downloading files
        """

        manager = DownloadManager()
        manager.download_available_data(self.receiver_id, year=year, timeout=timeout, force=force, verbose=verbose)
        self.clear_cache(suppress_errors=True)

    def delete_local_data(self, years: Collection[int] = None, dry_run: bool = False) -> List[Path]:
        """Delete downloaded SuomiNet data from the current environment

         Args:
             years: List of years to delete data from (defaults to all available years)
             dry_run: Returns a list of files that would be deleted without actually deleting them

         Returns:
             - A list of file paths that were deleted
         """

        return DownloadManager().delete_local_data(self.receiver_id, years=years, dry_run=dry_run)

    def __repr__(self) -> str:
        if self.cache_data:
            return 'GPSReceiver(rec_id="{}", data_cuts={}, cache_data=True)'.format(self.receiver_id, self.data_cuts)

        else:
            return 'GPSReceiver(rec_id="{}", data_cuts={})'.format(self.receiver_id, self.data_cuts)


class PWVModel:
    """Handles the modeling of PWV for times when direct measurements are not
    available from a given GPS receiver.
    """

    # noinspection PyMissingConstructor
    def __init__(self, primary: GPSReceiver, secondaries: Collection[GPSReceiver] = None,
                 data_cuts: DataCuts = None) -> None:
        """Model the PWV at a given GPS receivers using measurements from other, nearby receivers.

        Args:
            primary: SuomiNet Id of the receiver to access
            secondaries: Secondary receivers used to supplement periods with missing primary data
            data_cuts: Only include data in the given ranges
        """

        self._primary = primary
        self._data_cuts = data_cuts if data_cuts else dict()
        self._secondaries = secondaries
        self._pwv_model = None  # Place holder for lazy loading

        if primary in self._secondaries:
            raise ValueError('Primary receiver cannot be listed as a secondary receiver')

    @property
    def primary(self) -> GPSReceiver:
        """The primary GPS receiver to retrieve PWV data for"""

        return self._primary

    @property
    def secondaries(self) -> Collection[GPSReceiver]:
        """Secondary GPS receivers used to model the PWV concentration at
         the primary GPS location when primary data is not available.
         """

        return self._secondaries

    ###########################################################################
    # PWV is modeled by separately fitting the primary PWV as a function of
    # the PWV measured by each secondary receiver and then averaging the result
    ###########################################################################

    @staticmethod
    def _fit_primary_to_secondary(
            primary_data: pd.DataFrame, secondary_data: pd.DataFrame) -> Tuple[pd.Series, pd.Series]:
        """Apply a linear fit to the primary PWV data as a function of the PWV at a secondary location

        Args:
            primary_data: SuomiNet data from the primary receiver
            secondary_data: SuomiNet data from the secondary receiver

        Returns:
            - The fitted PWV (mm)
            - Error values for the fitted PWV
        """

        # Get subset of primary / secondary data with datetimes that overlap
        joined_data = primary_data \
            .join(secondary_data, lsuffix='Primary', rsuffix='Secondary') \
            .dropna(subset=['PWVPrimary', 'PWVErrPrimary', 'PWVSecondary', 'PWVErrSecondary'])

        # Evaluate the fit
        b, m = utils.linear_regression(
            joined_data['PWVSecondary'],
            joined_data['PWVPrimary'],
            joined_data['PWVErrSecondary'],
            joined_data['PWVErrPrimary']).beta

        # Apply the linear regression
        applied_fit = m * secondary_data.PWV + b
        residuals = joined_data['PWVPrimary'] - applied_fit
        errors = pd.Series(residuals.std(), name='fitted_err', index=applied_fit.index)

        return applied_fit, errors

    def _calc_avg_pwv_model(self) -> pd.DataFrame:
        """Determines a PWV model using each off site receiver and averages them

        Returns:
            A DataFrame with modeled PWV values and the associated errors over time
        """

        primary_data = self.primary.weather_data()

        # Fit fit the primary receiver's PWV data as function of each secondary
        # receiver and accumulate the results
        fitted_pwv = pd.DataFrame()
        fitted_error = pd.DataFrame()
        for secondary_rec in self.secondaries:
            secondary_data = secondary_rec.weather_data()

            try:
                _fitted_pwv, _fitted_error = self._fit_primary_to_secondary(primary_data, secondary_data)

            except RuntimeError:  # Failed ODR regression
                warnings.warn('Linear regression failed for {}. Dropped from model'.format(secondary_rec))

            else:
                fitted_pwv[secondary_rec] = _fitted_pwv
                fitted_error[secondary_rec] = _fitted_error

        # Average PWV models from different sites
        # noinspection PyTypeChecker
        out_data = pd.DataFrame({
            'PWV': fitted_pwv.mean(axis=1),
            'PWVErr': np.sqrt((fitted_error ** 2).sum(axis=1)) / len(fitted_error)
        })

        if out_data.empty:
            warnings.warn('No overlapping PWV data between primary and secondary '
                          'receivers. Cannot model PWV for times when primary '
                          'receiver is offline')

        # Upsert data from the primary receiver
        out_data = pd.concat([out_data[~out_data.index.isin(primary_data.index)], primary_data[['PWV', 'PWVErr']]])
        return out_data.dropna().sort_index()

    def modeled_pwv(self, year: int = None, month: int = None, day=None, hour=None) -> pd.DataFrame:
        """Return a table of the modeled PWV at the primary GPS site

        Return the modeled precipitable water vapor level at the primary
        GPS site. PWV measurements are reported in units of millimeters.
        Results can be optionally refined by year, month, day, and hour.

        Args:
            year: The year of the desired PWV data
            month: The month of the desired PWV data
            day: The day of the desired PWV data
            hour: The hour of the desired PWV data in 24-hour format

        Returns:
            A pandas DataFrame of modeled PWV values in mm
        """

        if self._pwv_model is None:
            self._pwv_model = self._calc_avg_pwv_model()

        return utils.search_data_table(self._pwv_model, year, month, day, hour)

    def __call__(self, date: NumpyArgument, interp_limit: int = None,
                 method: str = 'linear', order: int = None) -> NumpyReturn:
        """Evaluate the PWV model for a given datetime

        Args:
            date: UTC datetime object or timestamp
            interp_limit: Require measured values within the given time
                interval, otherwise result will be nan
                (Defined in units of 30 min).
            method: interpolation technique to use. Supported methods include
                'linear' 'nearest', 'zero', 'slinear', 'quadratic', 'cubic',
                'spline', 'barycentric', 'polynomial'
            order: Order of interpolation if using ‘polynomial’ or ‘spline’

        Returns:
            Line of sight PWV concentration at the given datetime
        """

        if method == 'linear':
            method = 'index'

        valid_methods = (
            'index', 'nearest', 'zero', 'slinear', 'quadratic', 'cubic',
            'spline', 'barycentric', 'polynomial')

        if method not in valid_methods:
            raise ValueError('Invalid interpolation method: {}'.format(method))

        # Resample modeled values onto a uniform sampling of time values
        # Credit: https://stackoverflow.com/a/47148740
        pwv_model = self.modeled_pwv()
        old_index = pwv_model.index
        new_index = pd.date_range(old_index.min(), old_index.max(), freq='30min')
        uniform_model = pwv_model.reindex(old_index.union(new_index))

        # We loose some efficiency here because we have to interpolate more
        # values than necessary (because of the resampling). However, the
        # resampling allows us to enforce physically meaningful interpolation
        # limits. Fortunately, interpolation is relatively cheap.
        uniform_model.loc[date] = np.nan
        interp_data = uniform_model.interpolate(method=method, limit=interp_limit, order=order).loc[date]

        if interp_data.isna().any():
            warnings.warn('Some values were outside the permitted interpolation range')

        return interp_data

    def __repr__(self) -> str:
        return 'PWVModel(primary="{}", secondaries={})'.format(self.primary, self.secondaries)
