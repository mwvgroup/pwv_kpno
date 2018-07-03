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

"""The ConfigBuilder class is provided to create custom config files used in
the pwv_kpno package.
"""

import os

import numpy as np

from ._atm_model import create_pwv_atm_model

__authors__ = ['Daniel Perrefort']
__copyright__ = 'Copyright 2017, Daniel Perrefort'

__license__ = 'GPL V3'
__email__ = 'djperrefort@pitt.edu'
__status__ = 'Development'

# Todo: Add value checks for args

class ConfigBuilder:
    """This class is used to build custom config files for the pwv_kpno package

    Attributes:
        data_cuts         (dict): Specifies data ranges to ignore
        loc_name           (str): Desired name of the custom location
        primary_rec        (str): SuomiNet ID code for the primary GPS receiver
        sup_recs          (list): List of SuomiNet id codes for supplemental receivers
        wavelengths    (ndarray): Array of wavelengths in Angstoms
        cross_sections (ndarray): Array of MODTRAN cross sections per wavelength in cm^2

    Methods:
        save : Create a custom config file <loc_name>.ecsv in a given directory
    """

    def __init__(self, **kwargs):
        self.data_cuts = dict()
        self.date_cuts = dict()
        self.loc_name = None  # type: str
        self.primary_rec = None  # type: str
        self.sup_rec = []
        self.wavelengths = None  # type: np.ndarray
        self.cross_sections = None  # type: np.ndarray

        for key, value in kwargs.items():
            setattr(self, key, value)

    def _check_attributes(self):
        """Ensure user has assigned values to required attributes"""

        err_msg = 'Must specify attribute {} before saving.'
        attrs = ['loc_name', 'primary_rec', 'wavelengths', 'cross_sections']
        for value in attrs:
            if getattr(self, value) is None:
                raise ValueError(err_msg.format(value))

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
        config_data['sup_rec'] = [id_code.upper() for id_code in self.sup_rec]
        return config_data

    def save(self, out_dir):
        # type: (str) -> None
        """Create a custom config file <out_dir>/<self.loc_name>.ecsv

        Args:
            out_dir (str): The desired output directory
        """

        self._check_attributes()
        model = create_pwv_atm_model(mod_lambda=np.array(self.wavelengths),
                                     mod_cs=np.array(self.cross_sections),
                                     out_lambda=np.array(self.wavelengths))

        model.meta = self._create_config_dict()
        out_path = os.path.join(out_dir, self.loc_name + '.ecsv')
        model.write(out_path)

    def __repr__(self):
        rep = '<ConfigBuilder loc_name={}, primary_rec={}>'
        return rep.format(self.loc_name, self.primary_rec)
