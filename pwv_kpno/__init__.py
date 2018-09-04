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

"""pwv_kpno provides models for the atmospheric transmission function due to
precipitable water vapor (PWV). Models cover wavelengths from 7,000 to 11,000
Angstroms at a resolution of 0.05 Angstroms. Using PWV measurements published
by the SuomiNet project (https://www.suominet.ucar.edu), this package is
capable of returning the modeled PWV transmission for a given date, time, and
airmass at customizable geographic locations. By default, this functionality
is set to model Kitt Peak National Observatory.

For more information on using this package, documentation is available online
at https://mwvgroup.github.io/pwv_kpno/ or through the standard python help
function.

An incomplete guide to getting started:

    To model the effects of PWV absorption on a black body, see the
    documentation for the `blackbody_with_atm` module:

      >>> from pwv_kpno import blackbody_with_atm as bb_atm


    To model the atmospheric transmission function, either for a known PWV
    concentration or for a datetime at a particular location, see the `pw_atm`
    module:

      >>> from pwv_kpno import pwv_atm


    To configure this package to model a custom geographical site, see the
    `ConfigBuilder` class:

      >>> from pwv_kpno import ConfigBuilder
"""

from . import pwv_atm
from . import blackbody_with_atm
from ._config_builder import ConfigBuilder
from ._package_settings import settings

__authors__ = ['Daniel Perrefort']
__copyright__ = 'Copyright 2017, Daniel Perrefort'
__credits__ = ['Michael Wood-Vasey', 'Azalee Bostroem',
               'Jessica Kroboth', 'Alexander Afanasyev']

__license__ = 'GPL V3'
__version__ = '0.12.1'
__email__ = 'djperrefort@pitt.edu'
__status__ = 'Development'

settings.set_site('kitt_peak')
