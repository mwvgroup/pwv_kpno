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
from datetime import datetime

from astropy.table import Table

__authors__ = ['Daniel Perrefort']
__copyright__ = 'Copyright 2017, Daniel Perrefort'

__license__ = 'GPL V3'
__email__ = 'djperrefort@pitt.edu'
__status__ = 'Development'

# Sites included with release that cannot be overwritten by the user
PROTECTED_NAMES = ['kitt_peak']


class ModelingConfigError(Exception):
    pass


def site_property(f):
    @property
    def wrapper(self, *args, **kwargs):
        if self._site_name is None:
            err_msg = 'No site has been specified for pwv_kpno model.'
            raise ModelingConfigError(err_msg)

        return f(self, *args, **kwargs)

    return wrapper


class Settings:
    """Represents pwv_kpno settings for a particular geographical site

    Represents settings for Kitt Peak by default

    Attributes:
        site_name       : The current site being modeled
        available_sites : A list of built in sites that pwv_kpno can model
        receivers       : A list of SuomiNet receivers used by this site
        primary_rec     : The SuomiNet id code for the primary GPS receiver
        supplement_rec  : Same as receivers but without the primary receiver

    Methods:
        set_site      : Configure pwv_kpno to model a given site
        export_config : Save the current site's configuration data to file
    """

    _site_name = None  # The name of the current site
    _config_data = None  # Data from the site's config file

    def __init__(self):
        _file_dir = os.path.dirname(os.path.realpath(__file__))
        self._suomi_dir = os.path.join(_file_dir, 'suomi_data')
        self._loc_dir_unf = os.path.join(_file_dir, 'site_data/{}')
        self._config_path_unf = os.path.join(self._loc_dir_unf, 'config.json')

        atm_dir = os.path.join(_file_dir, 'default_atmosphere/')
        self._h2o_cs_path = os.path.join(atm_dir, 'h2ocs.txt')
        # self._o2_cs_path = os.path.join(atm_dir, 'o2cs.txt')
        # self._o3_cs_path = os.path.join(atm_dir, 'o3cs.txt')

    @property
    def site_name(self):
        # type: () -> str
        return self._site_name

    @site_property
    def primary_rec(self):
        # type: () -> str
        return self._config_data['primary_rec']

    @site_property
    def _loc_dir(self):
        return self._loc_dir_unf.format(self.site_name)

    @property
    def _atm_model_path(self):
        return os.path.join(self._loc_dir, 'atm_model.csv')

    @site_property
    def _config_path(self):
        return self._config_path_unf.format(self.site_name)

    @property
    def _pwv_model_path(self):
        return os.path.join(self._loc_dir, 'modeled_pwv.csv')

    @property
    def _pwv_measred_path(self):
        return os.path.join(self._loc_dir, 'measured_pwv.csv')

    @property
    def available_sites(self):
        # type: () -> list[str]
        """A list of sites for which pwv_kpno has stored settings"""

        return next(os.walk(self._loc_dir_unf.format('')))[1]

    def set_site(self, loc):
        # type: (str) -> None
        """Configure pwv_kpno to model the default_atmosphere at a given site

        See the available_sites attribute for a list of available site names

        Args:
            loc (str): The name of a site to model
        """

        if loc in self.available_sites:
            config_path = self._config_path_unf.format(loc)

        else:
            err_msg = 'No stored settings for site {}'
            raise ValueError(err_msg.format(loc))

        with open(config_path, 'r') as ofile:
            self._config_data = json.load(ofile)

        self._site_name = self._config_data['site_name']

    @site_property
    def _available_years(self):
        """A list of years for which SuomiNet data has been downloaded"""

        return sorted(self._config_data['years'])

    def _replace_years(self, yr_list):
        # Replaces the list of years in the site's config file

        # Note: self._config_path calls @site_property decorator
        with open(self._config_path, 'r+') as ofile:
            current_data = json.load(ofile)
            current_data['years'] = list(set(yr_list))
            ofile.seek(0)
            json.dump(current_data, ofile, indent=4, sort_keys=True)
            ofile.truncate()

    @site_property
    def receivers(self):
        # type: () -> list[str]
        """A list of all GPS receivers associated with the current site"""

        # list used instead of .copy for python 2.7 compatibility
        rec_list = list(self._config_data['sup_rec'])
        rec_list.append(self._config_data['primary_rec'])
        return sorted(rec_list)

    @site_property
    def supplement_rec(self):
        # type () -> list[str]
        """A list of all supplementary GPS receivers for the current site"""

        return sorted(self._config_data['sup_rec'])

    @site_property
    def data_cuts(self):
        # type () -> dict
        """Returns restrictions on what SuomiNet measurements to include"""

        return self._config_data['data_cuts']

    def export_config(self, out_dir):
        # type: (str) -> None
        """Save the current site's config file to <out_dir>/<site_name>.ecsv

        Args:
            out_dir (str): The desired output directory
        """

        os.mkdir(out_dir)
        atm_model = Table.read(self._atm_model_path)
        atm_model.meta = self._config_data

        out_path = os.path.join(out_dir, self.site_name + '.ecsv')
        atm_model.write(out_path)

    def import_site(self, path, force_name=None, overwrite=False):
        # type: (str, bool) -> None
        """Load a custom configuration file and save it to the package

        Existing sites are only overwritten if overwrite is set to True.
        The imported site can be assigned an alternative name using the
        forced_name argument.

        Args:
            path       (str): The path of the desired config file
            force_name (str): Optional site name to overwrite config file
            overwrite (bool): Whether to overwrite an existing site
        """

        config_data = Table.read(path)
        if force_name:
            config_data.meta['site_name'] = str(force_name)

        loc_name = config_data.meta['site_name']
        if loc_name in PROTECTED_NAMES:
            err_msg = 'Cannot overwrite protected site name {}'
            raise ValueError(err_msg.format(loc_name))

        out_dir = self._loc_dir_unf.format(loc_name)
        if os.path.exists(out_dir) and not overwrite:
            err_msg = 'Site already exists {}'
            raise ValueError(err_msg.format(loc_name))

        temp_dir = out_dir + '_temp'
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

        os.mkdir(temp_dir)
        config_path = os.path.join(temp_dir, 'config.json')
        with open(config_path, 'w') as ofile:
            config_data.meta['years'] = []
            json.dump(config_data.meta, ofile, indent=4, sort_keys=True)

        atm_model_path = os.path.join(temp_dir, 'atm_model.json')
        config_data.write(atm_model_path, format='ascii.csv')

        if os.path.exists(out_dir):
            shutil.rmtree(out_dir)

        shutil.move(temp_dir, out_dir)

    def __repr__(self):
        rep = '<pwv_kpno.Settings, Current Site Name: {}>'
        return rep.format(self.site_name)

    def __str__(self):
        """Print metadata for the current site being modeled"""

        status_table = (
            "                     pwv_kpno Current Site Information\n"
            "============================================================================\n"
            "Site Name:            {} \n"
            "Primary Receiver:     {}\n"
            "Secondary Receivers:\n"
            "    {}\n\n"
            "Available Data:\n"
            "    {}\n\n"
            "                                 Data Cuts\n"
            "============================================================================\n"
            "Reveiver    Value       Type          Lower_Bound          Upper_Bound  unit\n"
            "----------------------------------------------------------------------------"
        )

        if self.supplement_rec:
            receivers = '\n    '.join(self.supplement_rec)

        else:
            receivers = '    NONE'

        if self._available_years:
            years = '\n    '.join(str(x) for x in self._available_years)

        else:
            years = '    NONE'

        status = status_table.format(
            self.site_name,
            self.primary_rec,
            receivers,
            years
        )

        units = {
            'date': 'UTC',
            'PWV': 'mm',
            'PWVerr': 'mm',
            'ZenithDelay': 'mm',
            'SrfcPress': 'mbar',
            'SrfcTemp': 'C',
            'SrfcRH': '%'
        }

        # Todo: This will be simplified once the config file format
        #  is modified in version 1.0.0
        for site, cuts in self.data_cuts.items():
            for value, bounds in cuts.items():
                for start, end in bounds:
                    if value == 'date':
                        cut_type = 'exclusive'
                        start = datetime.utcfromtimestamp(start)
                        end = datetime.utcfromtimestamp(end)

                    else:
                        cut_type = 'inclusive'

                    status += (
                            '\n' +
                            site +
                            value.rjust(13) +
                            cut_type.rjust(11) +
                            str(start).rjust(21) +
                            str(end).rjust(21) +
                            units[value].rjust(6)
                    )

        return status


# This instance should be used package wide to access site settings
settings = Settings()
