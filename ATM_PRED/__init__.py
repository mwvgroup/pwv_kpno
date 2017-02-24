#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

#    This file is part of the ATM_PRED module.
#
#    The ATM_PRED module is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    The ATM_PRED module is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Foobar.  If not, see <http://www.gnu.org/licenses/>.

from os import listdir as _listdir
from warnings import warn as _warn
from datetime import datetime as _datetime

from get_pwv_data import update_data
from get_pwv_data import pwv_data
from get_pwv_data import nearest_value
from datetime_to_spectra import date_to_spectra

__version__ = '1.0.0'
__license__ = 'GPL V3'
__status__ = 'Development'
 
# Check if there is any missing data from SuomiNet
SUOMI_DIR = './suomi_data'

available_data_years = set()
files = [f for f in _listdir(SUOMI_DIR)]

for file in files:
    if file.endswith('.plot'):
        available_data_years.add(int(file[-9:-5]))

missing_data = set(range(2010, _datetime.now().year)) - available_data_years

if missing_data:
    _warn('No downloaded SuomiNet data for years ' + str(missing_data) +
          '. Run update_date to update the local data from SuomiNet.')


# -- Developer notes --
# create_atm_model.py:
#     Find assumed PWV value
#
# create_pwv_model.py
#     Get Jess' Code
#     Add docstring / author info
#
# datetime_to_spectra.py
#    Connect with jess' code
#
# pwv_data.py
#    remove excess info from PWV table
#        for kittpeak data it will flatline at a certain value
#    create and save PWV models
#
# Todo (distribution):
#    Approval for classifiers and keywords / finish setup.py
#    Update ReadMe

# know what releigh scattering is
