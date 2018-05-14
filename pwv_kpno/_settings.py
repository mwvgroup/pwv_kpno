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
import shutil

__author__ = 'Daniel Perrefort'
__copyright__ = 'Copyright 2017, Daniel Perrefort'

__license__ = 'GPL V3'
__email__ = 'djperrefort@pitt.edu'
__status__ = 'Development'


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
    _loc_dir = os.path.join(_file_dir, 'locations/{}')

    # Unformatted paths for various package data
    _phosim_dir_unf = os.path.join(_loc_dir, 'atmosphere')
    _config_path_unf = os.path.join(_loc_dir, 'config.json')
    _atm_model_path_unf = os.path.join(_loc_dir, 'atm_model.csv')
    _pwv_model_path_unf = os.path.join(_loc_dir, 'modeled_pwv.csv')
    _pwv_msred_path_unf = os.path.join(_loc_dir, 'measured_pwv.csv')

    @property
    def location(self):
        # Property prevents user from directly setting self.location
        return self._location

    def _raise_location_defined(self):
        # Todo: Change this function to a property style decorator

        if self._location is None:
            # Todo: Not really a value error - change to more descriptive error
            raise ValueError('No location set to model.')

    @property
    def _phosim_dir(self):
        self._raise_location_defined()
        return self._phosim_dir_unf.format(self.location)

    @property
    def _atm_model_path(self):
        self._raise_location_defined()
        return self._atm_model_path_unf.format(self.location)

    @property
    def _pwv_model_path(self):
        self._raise_location_defined()
        return self._pwv_model_path_unf.format(self.location)

    @property
    def _pwv_msred_path(self):
        self._raise_location_defined()
        return self._pwv_msred_path_unf.format(self.location)

    @property
    def available_loc(self):
        """A list of locations for which pwv_kpno has stored settings"""

        self._loc_dir.format('')
        return next(os.walk(self._loc_dir.format('')))[1]

    def set_location(self, loc_name, config_path=None):
        """Configure pwv_kpno to model the atmosphere at a given location

        Args:
            loc_name    (str): The name of the location
            config_path (str): The path to the configuration files if loc_name
                                is not a built in location
        """

        is_builtin_name = loc_name in self.available_loc
        if is_builtin_name and config_path:
            raise ValueError(
                'Cannot import location with same name as a builtin location.')

        elif not (is_builtin_name or config_path):
            raise ValueError(
                "No builtin location '{}'.".format(loc_name))

        elif is_builtin_name:
            config_path = self._config_path_unf.format(loc_name)

        with open(config_path, 'r') as ofile:
            self._config_data = json.load(ofile)

        self._location = loc_name
        self.primary_rec = self._config_data['primary']

    @property
    def available_years(self):
        """A list of years for which SuomiNet data has been downloaded"""

        self._raise_location_defined()
        return sorted(self._config_data['years'])

    def _replace_years(self, yr_list):
        # Replaces the list of years in the location's config file

        self._raise_location_defined()
        config_path = self._config_path_unf.format(self.location)
        with open(config_path, 'r+') as ofile:
            current_data = json.load(ofile)
            current_data['years'] = list(set(yr_list))
            ofile.seek(0)
            json.dump(current_data, ofile, indent=2, sort_keys=True)
            ofile.truncate()

    @property
    def receivers(self):
        """A list of all GPS receivers associated with this location"""

        self._raise_location_defined()
        return list(self._config_data['receivers'].keys())

    @property
    def off_site_recs(self):
        """A list of all enabled, off sight GPS receivers for this location"""

        self._raise_location_defined()
        enabled = []
        for receiver, settings in self._config_data['receivers'].items():
            if settings[0] and receiver != self.primary_rec:
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

        self._raise_location_defined()
        all_rec_data = self._config_data['receivers']

        try:
            rec_data = all_rec_data[rec_id]

        except KeyError:
            err_msg = 'Receiver id {} is not affiliated with location {}'
            raise ValueError(err_msg.format(rec_id, self.location))

        return rec_data[1]

    def export_location(self, out_dir):
        """Export package settings for the current location to a directory

        Args:
            out_dir (str): The desired output directory
        """

        self._raise_location_defined()
        shutil.copytree(self._loc_dir, out_dir)


# This instance is used package wide to access site settings
settings = Settings()
