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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with pwv_kpno. If not, see <http://www.gnu.org/licenses/>.


"""This code allows users to modify package settings. While some of this code
is already being used in the package, much of it is provided as a framework for
future development.
"""

# Todo: Write tests
# Todo: Write rst documentation

from datetime import datetime
import json
import os
import shutil
from warnings import warn

from astropy.table import Table

__author__ = 'Daniel Perrefort'
__copyright__ = 'Copyright 2017, Daniel Perrefort'

__license__ = 'GPL V3'
__email__ = 'djperrefort@gmail.com'
__status__ = 'Development'

FILE_DIR = os.path.dirname(os.path.realpath(__file__))
LOC_PATH = os.path.join(FILE_DIR, 'locations')
CONFIG_PATH = os.path.join(LOC_PATH, '{}/config.json')


def _get_config_data(location_name):
    """Retrieves settings from a location's config file

    Each location has its own directory in pwv_kpno/locations/
    """

    path = CONFIG_PATH.format(location_name)
    with open(path, 'r') as ofile:
        return json.load(ofile)


class Receiver:
    """Represents a single SuomiNet GPS receiver

    Attributes:
        id                : The 4 character SuomiNet ID code for this receiver
        location          : The Location this receiver is associated with
        enabled           : If data from this receiver is being used for its
                            location
        ignore_timestamps : A 2d list of timestamps to ignore data for
        ignore_datetimes  : ignore_timestamps represented as datetime objects
    """

    def __init__(self):
        self.id = None
        self.enabled = None
        self.location = None
        self.ignore_timestamps = []

    @property
    def ignore_datetimes(self):
        """A 2d list of datetimes for which data from this receiver is ignored

        eg. [[start_datetime, end_datetime], ...]
        """

        out_list = []
        for end_time, start_time in self.ignore_timestamps:
            out_list.append([datetime.utcfromtimestamp(end_time),
                             datetime.utcfromtimestamp(start_time)])

        return out_list


class Location:
    """Package settings for a collection of SuomiNet GPS receivers

    Entries with an asterisk are underdevelopment and not functional

    Attributes:
        name              : The name of this location (eg. 'kitt_peak')
        available_years   : A list of Years for which SuomiNet data has been
                            downloaded for this location
        primary_receiver  : The id code of this location's primary GPS receiver
        all_receivers     : A list of all GPS receiver ids associated with
                            this location - both enabled and disabled
        enabled_receivers : A list of enabled GPS receivers associated with
                            this location

    Methods:
        restore          : Overwrites instance attributes with saved settings
        add_receiver     : Add a new GPS receiver to this location
        delete_receiver  : Delete a GPS receiver from this location
        enable_receiver  : Enable a GPS receiver for this location
        disable_receiver : Disable a GPS receiver for this location
        * ignore_dates   : Ignore data from a GPS receiver for specified dates
        * use_dates      : Undoes the ignore_dates method
        save             : Save location settings (attribute values)
        export           : Export saved settings to an ecsv file

    Indexing:
        Instances can be indexed using the id code of an associated GPS
        receiver. This returns a Receiver type object. See `all_receivers` for
        a list of available indices. For example:

            Location()['KITT']
    """

    def __init__(self, name=None):
        self.name = name
        self._original_name = self.name
        self._config_data = _get_config_data(name)
        self.primary_receiver = self._config_data['primary']
        self._original_primary_receiver = self.primary_receiver

    def __repr__(self):
        rep = "<Location (name='{}', gps_receivers='{}')>"
        return rep.format(self.name, self.all_receivers)

    @staticmethod
    def _check_receiver_args(id, enabled):
        """Raise errors if attributes have incorrect types"""

        type_err = "Attribute '{}' must be of type {}"
        if type(id) is not str:
            raise TypeError(type_err.format('id', 'str'))

        elif len(id) != 4:
            raise ValueError('SuomiNet id codes should be 4 characters long.')

        if type(enabled) is not bool:
            raise TypeError(type_err.format('enabled', 'bool'))

    def __getitem__(self, key):

        if not isinstance(key, str):
            raise TypeError('Expected string index')

        if key not in self.all_receivers:
            err_msg = "No stored settings for GPS receiver '{}'".format(key)
            raise ValueError(err_msg)

        receiver_data = self._config_data['receivers'][key]
        receiver = Receiver()
        receiver.id = key
        receiver.enabled = receiver_data[0]
        receiver.ignore_timestamps = receiver_data[1]
        return receiver

    def _replace_years(self, yr_list):
        """Replaces the list of years in the location's config file"""

        path = CONFIG_PATH.format(self.name)
        with open(path, 'r+') as ofile:
            current_data = json.load(ofile)
            current_data['years'] = yr_list
            ofile.seek(0)
            json.dump(current_data, ofile, indent=2, sort_keys=True)
            ofile.truncate()

    @property
    def available_years(self):
        """A list of years for which SuomiNet data has been downloaded"""

        return self._config_data['years']

    def restore(self):
        """Overwrite any currently unsaved settings with saved values"""

        self._config_data = _get_config_data(self._original_name)
        self.name = self._original_name
        self.primary_receiver = self._original_primary_receiver

    def add_receiver(self, id, enabled=False):
        """Save the receiver instance to the package settings

        Args:
            id       (str): The SuomiNet id code of the receiver
            enabled (bool): Whether to use data from this receiver
        """

        # Todo : change this method to accept Receiver object

        self._check_receiver_args(id, enabled)

        if id in self._config_data['receivers']:
            err_msg = "Entry with id '{}' already exists for this location."
            raise ValueError(err_msg.format(id))

        else:
            self._config_data['receivers'][id] = [enabled, []]

    def delete_receiver(self, id):
        """Deletes a SuomiNet receiver from this location

        Only settings data is deleted. All PWV data downloaded from SuomiNet
        for the receiver will remain on disk.

        Args:
            id (str): The id code for a receiver stored in settings
        """

        if id in self._config_data['receivers']:
            del self._config_data['receivers'][id]

        else:
            warn("No entry found with id '{}'".format(id))

    def _raise_valid_id(self, id):
        """Raises ValueError if no settings are available for the given id"""

        if id not in self._config_data['receivers']:
            err_msg = "No receiver '{}' stored for location '{}'"
            raise ValueError(err_msg.format(id, self.name))

    def enable_receiver(self, id):
        """Set the status of a GPS receiver to enabled for this location

        Atmospheric models returned for a location only use data taken by
        receivers that are enabled. Changing the status of a receiver for one
        location does not effect other locations.

        Args:
            id (str): The 4 character id code of a GPS receiver
        """

        self._raise_valid_id(id)
        self._config_data['receivers'][id] = True

    def disable_receiver(self, id):
        """Set the status of a GPS receiver to disabled for this location

        Atmospheric models returned for a location only use data taken by
        receivers that are enabled. Changing the status of a receiver for one
        location does not effect other locations.

        Args:
            id (str): The 4 character id code of a GPS receiver
        """

        self._raise_valid_id(id)
        self._config_data['receivers'][id] = False

    @property
    def all_receivers(self):
        """A list of all GPS receivers associated with this location"""

        return list(self._config_data['receivers'].keys())

    @property
    def enabled_receivers(self):
        """A list of all enabled GPS receivers associated with this location"""

        enabled = []
        for receiver, settings in self._config_data['receivers'].items():
            if settings[0]:
                enabled.append(receiver)

        return enabled

    def ignore_dates(self, id, date_range):
        # Todo (include type checks)

        warn('`Location` class is under development. '
             'This method is not functional.')

    def use_dates(self, id, date_range):
        # Todo (include type checks)

        warn('`Location` class is under development. '
             'This method is not functional.')

    def save(self):
        """Save current settings for this locations to file"""

        path = CONFIG_PATH.format(self._original_name)
        with open(path, 'w') as ofile:
            json.dump(self._config_data, ofile, indent=2, sort_keys=True)
            ofile.truncate()

        old_dir = os.path.join(LOC_PATH, self._original_name)
        new_dir = os.path.join(LOC_PATH, self.name)
        shutil.move(old_dir, new_dir)
        self._original_name = self.name

    def export(self, out_dir, overwrite=False):
        """Write the current package settings to file

        Existing files will not be overwritten unless the `overwrite` argument
        is set to `True`

        Args:
            out_dir    (str): The desired output directory
            overwrite (bool): Whether to overwrite existing files
        """

        if not os.path.isdir(out_dir):
            raise ValueError('Output directory does not exist')

        atm_model_path = os.path.join(LOC_PATH, self.name, 'atm_model.csv')
        if not os.path.exists(atm_model_path):
            err_msg = 'No stored settings for location {}'
            raise ValueError(err_msg.format(self.name))

        atm_model = Table.read(atm_model_path)
        meta = _get_config_data(self.name)
        del meta['years']
        atm_model.meta = meta

        # Todo: Should the user specify a directory or file path?
        out_path = os.path.join(out_dir, '{}_settings.ecsv'.format(self.name))
        atm_model.write(out_path, format='ascii.ecsv', overwrite=overwrite)


class Settings:
    """Represents package settings for pwv_kpno

    Entries with an asterisk are underdevelopment and not functional

    Attributes:
        locations        : A list of locations with stored settings
        current_location : The default location used when providing
                           atmospheric models

    Methods:
        * add_location : Create a new location with a unique atmospheric model
        * read         : Read locations settings from file

    Indexing:
        Instances can be indexed using the name of a location with stored
        settings. This returns a Location type object. See `locations` for a
        list of available indices. For example:

            Settings()['kitt_peak']
    """

    def __iter__(self):
        location_objects = (self[site] for site in self.locations)
        self._iter_locations = iter(location_objects)
        return self._iter_locations

    def __next__(self):
        return next(self._iter_locations)

    def __getitem__(self, key):
        if not isinstance(key, str):
            raise TypeError('Expected string index')

        if key not in self.locations:
            err_msg = "No stored settings for location '{}'"
            raise ValueError(err_msg.format(key))

        config_data = _get_config_data(key)
        location = Location(key)
        location.primary_receiver = config_data['primary']
        location.gps_receivers = list(config_data['receivers'].keys())
        return location

    def __repr__(self):
        rep = "<pwv_kpno Settings>\n\n"
        rep += "Available Locations:\n"
        rep += "--------------------\n"
        for i, loc in enumerate(self.locations):
            rep += '  {}. {}\n'.format(i + 1, loc)

        return rep

    @property
    def locations(self):
        """A list of locations for which pwv_kpno has stored settings"""

        return next(os.walk(LOC_PATH))[1]

    @property
    def current_location(self):
        """The current location being modeled by pwv_kpno"""

        with open(os.path.join(FILE_DIR, 'CONFIG.txt'), 'r') as ofile:
            return self[ofile.readline()]

    @current_location.setter
    def current_location(self, location):
        """The current location being modeled by pwv_kpno"""

        if location not in self.locations:
            err_msg = 'No stored settings for location {}'
            raise ValueError(err_msg.format(location))

        with open(os.path.join(FILE_DIR, 'CONFIG.txt'), 'w') as ofile:
            ofile.seek(0)
            ofile.write(location)
            ofile.truncate()

    def add_location(self):
        """Create a new location with a unique atmospheric model"""
        # Todo (First implement ability to generate new atmospheric models)

        warn('`Settings` class is under development. '
             'This method is not functional.')

    def read(self, fpath):
        """Read locations settings from file"""
        # Todo (First implement add_location method)

        warn('`Settings` class is under development. '
             'This method is not functional.')
