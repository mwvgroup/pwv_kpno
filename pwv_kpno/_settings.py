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


"""This code provides access to package settings for a given location through
the Settings class.
"""

import json
import os
import shutil

__author__ = 'Daniel Perrefort'
__copyright__ = 'Copyright 2017, Daniel Perrefort'

__license__ = 'GPL V3'
__email__ = 'djperrefort@pitt.edu'
__status__ = 'Development'


def available_loc():
    """A list of locations for which pwv_kpno has stored settings"""

    file_dir = os.path.dirname(os.path.realpath(__file__))
    return next(os.walk(os.path.join(file_dir, 'locations')))[1]


class Settings:
    """Represents pwv_kpno settings for a particular geographical location

    Represents settings for Kitt Peak by default

    Attributes:
        location_name      : The name of this location (eg. 'kitt_peak')
        primary_receiver   : The SuomiNet id code for the primary GPS receiver
        receivers          : A list of all associated SuomiNet ids
        off_site_receivers : A list of all associated SuomiNet ids other than
                              the primary receiver
        available_years    : A list of years for which SuomiNet data has been
                              downloaded

    Methods:
        ignored_timestamps : Returns time periods when data from a given
                              receiver is ignored
        export_location    : Export package settings for the current location
                              to a directory

    """

    def __init__(self, location='kitt_peak'):

        file_dir = os.path.dirname(os.path.realpath(__file__))
        _loc_dir = os.path.join(file_dir, 'locations/{}'.format(location))

        self._loc_dir = _loc_dir
        self._suomi_dir = os.path.join(file_dir, 'suomi_data')
        self._phosim_dir = os.path.join(_loc_dir, 'atmosphere')
        self._config_path = os.path.join(_loc_dir, 'config.json')
        self._atm_model_path = os.path.join(_loc_dir, 'atm_model.csv')
        self._pwv_model_path = os.path.join(_loc_dir, 'modeled_pwv.csv')
        self._pwv_msred_path = os.path.join(_loc_dir, 'measured_pwv.csv')

        with open(self._config_path, 'r') as ofile:
            self._config_data = json.load(ofile)

        self.location_name = location
        self.primary_receiver = self._config_data['primary']

    @property
    def available_years(self):
        """A list of years for which SuomiNet data has been downloaded"""

        return self._config_data['years']

    def _replace_years(self, yr_list):
        """Replaces the list of years in the location's config file"""

        with open(self._config_path, 'r+') as ofile:
            current_data = json.load(ofile)
            current_data['years'] = list(set(yr_list))
            ofile.seek(0)
            json.dump(current_data, ofile, indent=2, sort_keys=True)
            ofile.truncate()

    @property
    def receivers(self):
        """A list of all GPS receivers associated with this location"""

        return list(self._config_data['receivers'].keys())

    @property
    def off_site_receivers(self):
        """A list of all enabled, off sight GPS receivers for this location"""

        enabled = []
        for receiver, settings in self._config_data['receivers'].items():
            if settings[0] and receiver != self.primary_receiver:
                enabled.append(receiver)

        return enabled

    def __repr__(self):
        rep = '<pwv_kpno.Settings Location Name: {}>'
        return rep.format(self.location_name)

    def ignored_timestamps(self, rec_id):
        """Returns time periods when data from a given receiver is ignored

        Args:
            rec_id (str): The id code of a SuomiNet GPS receiver
        """

        try:
            rec_data = self._config_data[rec_id]

        except IndexError:
            err_msg = 'Receiver id {} is not affiliated with location {}'
            raise ValueError(err_msg.format(rec_id, self.location_name))

        return rec_data[1]

    def export_location(self, out_dir):
        """Export package settings for the current location to a directory

        Args:
            out_dir (str): The desired output directory
        """

        shutil.copytree(self._loc_dir, out_dir)
