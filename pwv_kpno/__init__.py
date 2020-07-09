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
precipitable water vapor (PWV). Using PWV measurements published
by the SuomiNet project (https://www.suominet.ucar.edu), this package is
capable of returning the modeled PWV transmission for a given date and time
at customizable geographic locations. By default, this functionality
is set to model Kitt Peak National Observatory. Default models cover
wavelengths from 3,000 to 12,000 Angstroms at a resolution of 0.05 Angstroms.

For more information on using this package, documentation is available online
at https://mwvgroup.github.io/pwv_kpno/ or through the standard python help
function.
"""

__authors__ = ['MWV Research Group']
__copyright__ = 'Copyright 2017, MWV Research Group'
__credits__ = [
    'Daniel Perrefort'
    'W. M. Wood-Vasey',
    'K. Azalee Bostroem',
    'Jessica Kroboth',
    'Tom Matheson',
]

__license__ = 'GPL V3'
__version__ = '2.0.0'
__email__ = 'djperrefort@pitt.edu'
__status__ = 'Release'
