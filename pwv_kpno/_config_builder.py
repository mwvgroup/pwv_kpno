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
from warnings import warn

import numpy as np

from ._atm_model import create_pwv_atm_model
from ._package_settings import Settings

__authors__ = ['Daniel Perrefort']
__copyright__ = 'Copyright 2017, Daniel Perrefort'

__license__ = 'GPL V3'
__email__ = 'djperrefort@pitt.edu'
__status__ = 'Development'

# List of params that data cuts can be applied for
CUT_PARAMS = ('PWV', 'PWVerr', 'ZenithDelay', 'SrfcPress', 'SrfcTemp', 'SrfcRH')


# Todo: Add test coverage
class ConfigBuilder:
    """The ConfigBuilder class is used to build config files for a custom site

    Default wavelengths and cross sections are provided by MODTRAN estimates
    and range from 3,000 to 12,000 Angstroms in 0.05 Angstrom increments.

    Attributes:
        data_cuts         (dict): Specifies cuts for SuomiNet data
        site_name          (str): Desired name of the custom site
        primary_rec        (str): SuomiNet ID code for the primary GPS receiver
        sup_recs          (list): List of id codes for supplemental receivers
        wavelengths    (ndarray): Array of wavelengths in Angstroms (optional)
        cross_sections (ndarray): Array of PWV cross sections in cm^2 (optional)

    Methods:
        save_to_dir : Create a custom config file <site_name>.ecsv
    """

    def __init__(self, **kwargs):
        self.data_cuts = dict()
        self.site_name = None  # type: str
        self.primary_rec = None  # type: str
        self.sup_rec = []

        settings = Settings()
        settings.set_site('kitt_peak')
        atm_cross_sections = np.genfromtxt(settings._h2o_cs_path).transpose()
        self.wavelengths = atm_cross_sections[0]
        self.cross_sections = atm_cross_sections[1]

        for key, value in kwargs.items():
            setattr(self, key, value)

    def _raise_unset_attributes(self):
        """Ensure user has assigned values to required attributes"""

        err_msg = 'Must specify attribute {} before saving.'
        attrs = ['site_name', 'primary_rec', 'wavelengths', 'cross_sections']
        for value in attrs:
            if getattr(self, value) is None:
                raise ValueError(err_msg.format(value))

    def _warn_data_cuts(self):
        """Raise warnings if data cuts are not the correct format

        Data cuts should be of the form:
            {cut param: [[lower bound, upper bound], ...], ...}
        """

        for dictionary in self.data_cuts.values():
            for key, value in dictionary.items():
                if key not in CUT_PARAMS:
                    warn(
                        'Provided data cut parameter {} does not correspond'
                        ' to any parameter used by pwv_kpno'.format(key)
                    )

                value = np.array(value)
                if not len(value.shape) == 2:
                    warn(
                        'Cut boundaries for parameter {}'
                        ' are not a two dimensional array'.format(key)
                    )

    def _warn_site_name(self):
        """Raise warnings if site_name is not the correct format

        Site names should be lowercase strings.
        """

        if not self.site_name.islower():
            warn(
                'pwv_kpno uses lowercase site names. The site name {} will be'
                ' saved as {}.'.format(self.site_name, self.site_name.lower())
            )

    def _warn_id_codes(self):
        """Raise warnings if SuomiNet ID codes are not the correct format

        SuomiNet ID codes should be four characters long and uppercase.
        """

        all_id_codes = self.sup_rec.copy()
        all_id_codes.append(self.primary_rec)
        for id_code in all_id_codes:
            if len(id_code) != 4:
                warn('ID is not of expected length 4: {}'.format(id_code))

            if not id_code.isupper():
                warn(
                    'SuomiNet ID codes should be uppercase. ID code {} will'
                    ' be saved as {}.'.format(id_code, id_code.upper())
                )

    def _create_config_dict(self):
        """Create a dictionary with config data for this site

        Returns:
            A dictionary storing site settings
        """

        config_data = dict()
        self._warn_data_cuts()
        config_data['data_cuts'] = self.data_cuts

        self._warn_site_name()
        config_data['site_name'] = self.site_name.lower()

        self._warn_id_codes()
        config_data['primary_rec'] = self.primary_rec.upper()
        config_data['sup_rec'] = [id_code.upper() for id_code in self.sup_rec]
        return config_data

    def save_to_dir(self, out_dir, overwrite=False):
        # type: (str) -> None
        """Create a custom config file <out_dir>/<self.site_name>.ecsv

        Args:
            out_dir    (str): The desired output directory
            overwrite (bool): Whether to overwrite an existing file
        """

        self._raise_unset_attributes()
        model = create_pwv_atm_model(mod_lambda=np.array(self.wavelengths),
                                     mod_cs=np.array(self.cross_sections),
                                     out_lambda=np.array(self.wavelengths))

        model.meta = self._create_config_dict()
        out_path = os.path.join(out_dir, self.site_name + '.ecsv')
        model.write(out_path, overwrite=overwrite)

    def __repr__(self):
        rep = '<ConfigBuilder site_name={}, primary_rec={}>'
        return rep.format(self.site_name, self.primary_rec)
