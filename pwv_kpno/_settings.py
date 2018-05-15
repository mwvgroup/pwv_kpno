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
#    along with pwv_kpno. If not, see <http://www.gnu.org/licenses/>.


"""This code provides access to package settings through the Settings class.
"""

import json
import os

__author__ = 'Daniel Perrefort'
__copyright__ = 'Copyright 2017, Daniel Perrefort'

__license__ = 'GPL V3'
__email__ = 'djperrefort@pitt.edu'
__status__ = 'Development'


def location_property(f):
    @property
    def wrapper(self, *args, **kwargs):
        
        if self._location is None:
            raise ValueError('No location set to model.')

        return f(self, *args, **kwargs)
    return wrapper


class Settings:
    """Represents pwv_kpno settings for a particular geographical location

    Represents settings for Kitt Peak by default

    Attributes:
        current_loc     : The current location being modeled
        available_loc   : A list of built in locations that can be modeled
        receivers       : A list of SuomiNet receivers used by this location
        primary_rec     : The SuomiNet id code for the primary GPS receiver
        off_site_recs   : Same as receivers but without the primary receiver
        available_years : A list of years with locally available SuomiNet data

    Methods:
        set_location       : Configure pwv_kpno to model a given location
        ignored_timestamps : Returns a 2d list of data cuts for a given receiver
        export_location    : Export package settings for the current location
    """

    _location = None
    _config_data = None
    primary_rec = None

    _file_dir = os.path.dirname(os.path.realpath(__file__))
    _suomi_dir = os.path.join(_file_dir, 'suomi_data')

    # Unformatted paths for various package data
    _loc_dir_unf = os.path.join(_file_dir, 'locations/{}')
    _phosim_dir_unf = os.path.join(_loc_dir_unf, 'atmosphere')
    _config_path_unf = os.path.join(_loc_dir_unf, 'config.json')
    _atm_model_path_unf = os.path.join(_loc_dir_unf, 'atm_model.csv')
    _pwv_model_path_unf = os.path.join(_loc_dir_unf, 'modeled_pwv.csv')
    _pwv_msred_path_unf = os.path.join(_loc_dir_unf, 'measured_pwv.csv')

    @property
    def location(self):
        # Property prevents user from directly setting self.location
        return self._location

    @location_property
    def _loc_dir(self):
        return self._loc_dir_unf.format(self.location)

    @location_property
    def _phosim_dir(self):
        return self._phosim_dir_unf.format(self.location)

    @location_property
    def _config_path(self):
        return self._config_path_unf.format(self.location)

    @location_property
    def _atm_model_path(self):
        return self._atm_model_path_unf.format(self.location)

    @location_property
    def _pwv_model_path(self):
        return self._pwv_model_path_unf.format(self.location)

    @location_property
    def _pwv_msred_path(self):
        return self._pwv_msred_path_unf.format(self.location)

    @property
    def available_loc(self):
        """A list of locations for which pwv_kpno has stored settings"""

        self._loc_dir_unf.format('')
        return next(os.walk(self._loc_dir_unf.format('')))[1]

    def set_location(self, loc_name):
        """Configure pwv_kpno to model the atmosphere at a given location

        Args:
            loc_name (str): The name of a builtin location
        """

        if loc_name not in self.available_loc:
            raise ValueError("No location found for '{}'.".format(loc_name))

        self._location = loc_name
        with open(self._config_path, 'r') as ofile:
            self._config_data = json.load(ofile)

        self.primary_rec = self._config_data['primary']

    @location_property
    def available_years(self):
        """A list of years for which SuomiNet data has been downloaded"""

        return sorted(self._config_data['years'])

    def _replace_years(self, yr_list):
        # Replaces the list of years in the location's config file

        # Note: self._config_path calls @location_property decorator
        with open(self._config_path, 'r+') as ofile:
            current_data = json.load(ofile)
            current_data['years'] = list(set(yr_list))
            ofile.seek(0)
            json.dump(current_data, ofile, indent=2, sort_keys=True)
            ofile.truncate()

    @location_property
    def receivers(self):
        """A list of all GPS receivers associated with this location"""

        return list(self._config_data['receivers'].keys())

    @location_property
    def off_site_recs(self):
        """A list of all enabled, off sight GPS receivers for this location"""

        enabled = []
        for receiver, values in self._config_data['receivers'].items():
            if receiver != self.primary_rec:
                enabled.append(receiver)

        return enabled

    def __repr__(self):
        rep = '<pwv_kpno.Settings, Current Location Name: {}>'
        return rep.format(self.location)

    def ignored_timestamps(self, rec_id):
        """Returns time periods when data from a given receiver is ignored

        Args:
            rec_id (str): The id code of a SuomiNet GPS receiver
        """

        if self._location is None:
            raise ValueError('No location set to model.')

        all_rec_data = self._config_data['receivers']

        try:
            return all_rec_data[rec_id][0]

        except KeyError:
            err_msg = 'Receiver id {} is not affiliated with location {}'
            raise ValueError(err_msg.format(rec_id, self.location))

    def export_location(self, out_path):
        """Export package settings for the current location to a fits file

        Args:
            out_path (str): The desired output directory
        """

        # Todo: Combine data to a single .fits file and write to out_path
        pass

    def import_location(self, in_path):
        """Import package settings from a custom configuration file

        Args:
            in_path (str): The path of the desired
        """

        # Todo: Unpack data from .fits file and write to pwv_kpno/locations
        pass


# This instance is used package wide to access site settings
settings = Settings()
