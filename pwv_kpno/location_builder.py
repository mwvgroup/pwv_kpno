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


"""This code allows users to create a configuration file for a custom location.
"""

import os

from ._atm_model import create_pwv_atm_model

__authors__ = ['Daniel Perrefort']
__copyright__ = 'Copyright 2017, Daniel Perrefort'

__license__ = 'GPL V3'
__email__ = 'djperrefort@pitt.edu'
__status__ = 'Development'


class LocationBuilder:
    # Todo: Add value checks and documentation when publicly released

    def __init__(self, **kwargs):

        # Set default values
        self.data_cuts = dict()
        self.date_cuts = dict()
        self.loc_name = None
        self.primary_rec = None
        self.sup_rec = []
        self.wavelengths = None
        self.cross_sections = None

        for key, value in kwargs.items():
            setattr(self, key, value)

    def _create_config_dict(self):
        """Create a dictionary with config data for this location

        Returns:
            A dictionary storing location settings
        """

        config_data = dict()
        config_data['data_cuts'] = self.data_cuts
        config_data['date_cuts'] = self.date_cuts
        config_data['loc_name'] = self.loc_name.lower()
        config_data['primary_rec'] = self.primary_rec.upper()
        config_data['sup_rec'] = self.sup_rec
        return config_data

    def save(self, out_dir):
        """Save location data to a <out_dir>/<location_name>.ecsv

        Args:
            out_dir (str): The desired output directory
        """

        model = create_pwv_atm_model(mod_lambda=self.wavelengths,
                                     mod_cs=self.cross_sections,
                                     out_lambda=self.wavelengths)

        model.meta = self._create_config_dict()
        out_path = os.path.join(out_dir, self.loc_name + '.ecsv')
        model.write(out_path)

    def __repr__(self):
        rep = '<pwv_kpno.LocationBuilder>'
        return rep.format(self.loc_name)
