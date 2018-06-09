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


"""This code provides access to package settings through the Settings class."""

import json
import os
import shutil

__author__ = 'Daniel Perrefort'
__copyright__ = 'Copyright 2017, Daniel Perrefort'

__license__ = 'GPL V3'
__email__ = 'djperrefort@pitt.edu'
__status__ = 'Development'


class ModelingConfigError(Exception):
    pass


def location_property(f):
    @property
    def wrapper(self, *args, **kwargs):
        if self._location is None:
            raise ModelingConfigError(
                'No location has been set for pwv_kpno model.')

        return f(self, *args, **kwargs)

    return wrapper


def raise_missing_files(dir_path):
    """Raises an error if a given directory is missing package config files

    Args:
         dir_path: A directory to check for missing config files
    """

    files = os.listdir(dir_path)
    err_msg = 'Missing {} in loc_dir.'
    file_list = ['atm_model.csv', 'config.json',
                 'measured_pwv.csv', 'modeled_pwv.csv']

    for fname in file_list:
        if fname not in files:
            raise FileNotFoundError(err_msg.format(fname))


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
        set_location    : Configure pwv_kpno to model a given location
        export_location : Export package settings for the current location
    """

    _location = None  # The name of the current location
    _config_data = None  # Data from the locations config file

    def __init__(self):
        _file_dir = os.path.dirname(os.path.realpath(__file__))
        self._suomi_dir = os.path.join(_file_dir, 'suomi_data')
        self._loc_dir_unf = os.path.join(_file_dir, 'locations/{}')
        self._config_path_unf = os.path.join(self._loc_dir_unf, 'config.json')

    @property
    def location(self):
        return self._location

    @location_property
    def primary_rec(self):
        return self._config_data['primary_rec']

    @location_property
    def _loc_dir(self):
        return self._loc_dir_unf.format(self.location)

    @location_property
    def _config_path(self):
        return self._config_path_unf.format(self.location)

    @property
    def _phosim_dir(self):
        return os.path.join(self._loc_dir, 'atmosphere')

    @property
    def _atm_model_path(self):
        return os.path.join(self._loc_dir, 'atm_model.csv')

    @property
    def _pwv_model_path(self):
        return os.path.join(self._loc_dir, 'modeled_pwv.csv')

    @property
    def _pwv_msred_path(self):
        return os.path.join(self._loc_dir, 'measured_pwv.csv')

    @property
    def available_loc(self):
        """A list of locations for which pwv_kpno has stored settings"""

        self._loc_dir_unf.format('')
        return next(os.walk(self._loc_dir_unf.format('')))[1]

    def set_location(self, loc):
        """Configure pwv_kpno to model the atmosphere at a given location

        Accepts the name of a builtin location OR a directory containing custom
        configuration files.

        Args:
            loc (str): The name or directory of location to model
        """

        if loc in self.available_loc:
            config_path = self._config_path_unf.format(loc)

        elif os.path.isdir(loc):
            raise_missing_files(loc)
            config_path = os.path.join(loc, 'config.json')

        else:
            raise ValueError('err msg')

        with open(config_path, 'r') as ofile:
            self._config_data = json.load(ofile)

        self._location = self._config_data['loc_name']

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
            json.dump(current_data, ofile, indent=4, sort_keys=True)
            ofile.truncate()

    @location_property
    def receivers(self):
        """A list of all GPS receivers associated with this location"""

        # list used instead of .copy for python 2.7 compatibility
        rec_list = list(self._config_data['sup_rec'])
        rec_list.append(self._config_data['primary_rec'])
        return sorted(rec_list)

    @location_property
    def off_site_recs(self):
        """A list of all enabled, off sight GPS receivers for this location"""

        return sorted(self._config_data['sup_rec'])

    def __repr__(self):
        rep = '<pwv_kpno.Settings, Current Location Name: {}>'
        return rep.format(self.location)

    def _data_cuts(self, rec_id):
        """Returns restrictions on what SuomiNet measurements to include

        Args:
            rec_id (str): The id code of a SuomiNet GPS receiver
        """

        if self._location is None:
            raise ValueError('No location set to model.')

        return self._config_data['data_cuts'][rec_id]

    def _date_cuts(self, rec_id):
        """Returns time periods when data from a given receiver is ignored

        Args:
            rec_id (str): The id code of a SuomiNet GPS receiver
        """

        if self._location is None:
            raise ValueError('No location set to model.')

        return self._config_data['date_cuts'][rec_id]

    def export_location(self, out_dir):
        """Export package settings for the current location to a new directory

        Args:
            out_dir (str): The desired output directory
        """

        os.mkdir(out_dir)
        atm_path = os.path.join(out_dir, 'atm_model.csv')
        shutil.copyfile(self._atm_model_path, atm_path)
        config_path = os.path.join(out_dir, 'config.json')
        shutil.copyfile(self._config_path, config_path)
        measured_path = os.path.join(out_dir, 'measured_pwv.csv')
        shutil.copyfile(self._pwv_msred_path, measured_path)
        model_path = os.path.join(out_dir, 'modeled_pwv.csv')
        shutil.copyfile(self._pwv_model_path, model_path)


# This instance should be used package wide to access site settings
settings = Settings()
