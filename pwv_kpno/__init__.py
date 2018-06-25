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
#    along with pwv_kpno.  If not, see <http://www.gnu.org/licenses/>.

"""pwv_kpno provides models for the atmospheric transmission function at Kitt
Peak National Observatory due to precipitable water vapor. Models cover
wavelengths from 7000 to 11000 Angstroms for years 2010 onward. Documentation
is available online at https://mwvgroup.github.io/pwv_kpno/ or through the
standard python help function.
"""

from . import pwv_atm
from . import blackbody_with_atm
from ._settings import settings as _settings

__authors__ = ['Daniel Perrefort']
__copyright__ = 'Copyright 2017, Daniel Perrefort'
__credits__ = ['Michael Wood-Vasey', 'Azalee Bostroem',
               'Jessica Kroboth', 'Alexander Afanasyev']

__license__ = 'GPL V3'
__version__ = '0.11.6'
__email__ = 'djperrefort@pitt.edu'
__status__ = 'Development'

# Sets up package to model Kitt Peak
_settings.set_location('kitt_peak')
