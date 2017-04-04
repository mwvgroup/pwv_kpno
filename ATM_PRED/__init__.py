#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

#    This file is part of the atm_pred module.
#
#    The atm_pred module is free software: you can redistribute it and/or
#    modify it under the terms of the GNU General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    The atm_pred module is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with atm_pred.  If not, see <http://www.gnu.org/licenses/>.

"""The atm_pred module models the atmospheric transmission spectrum due to
perciptible water vapor (PWV) above kitt peak for year 2010 and later. Models
are created using PWV measurment provided by the SuomiNet Project
(see http://www.suominet.ucar.edu/overview.html)."""

from os import listdir as _listdir
from warnings import warn as _warn
from datetime import datetime as _datetime

from create_pwv_model import update_models
from datetime_to_spectra import pwv_data
from datetime_to_spectra import nearest_value
from datetime_to_spectra import date_to_spectra

__version__ = '1.0.0'
__license__ = 'GPL V3'
__status__ = 'Development'

# -- Developer notes --
# create_atm_model.py:
#     Find assumed PWV value
#
#
# Todo (distribution):
#    Approval for classifiers and keywords / finish setup.py
#    What authors to credit where
#    Update ReadMe
#       Make note that user needs permission to update files within the package
#           when updating pwv data
#       Comment on releigh scattering
