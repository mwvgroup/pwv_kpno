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
#    along with pwv_kpno.  If not, see <http://www.gnu.org/licenses/>.

"""pwv_kpno provides models for the atmospheric transmission function at Kitt
Peak National Observatory due to atmospheric water vapor. Models cover
wavelengths in the optical and near-infrared (7000 to 11000 Angstroms) for
years 2010 onward.

To retrieve the atmospheric model for a datetime and airmass, see the function
`transmission`. To retrieve the atmospheric model for a precipitable water
vapor concentration, see the function `transmission_pwv`. Documentation can be
accessed on the package homepage (url tbd) or by using the standard python help
function.

For more details on the correlation between GPS signals and PWV levels see
Blake and Shaw, 2011 (https://arxiv.org/abs/1109.6703). For more details on the
SuomiNet project see http://www.suominet.ucar.edu/overview.html.
"""

from .calc_transmission import transmission
from .calc_transmission import transmission_pwv
from .end_user_utilities import available_data
from .end_user_utilities import update_models
from .end_user_utilities import modeled_pwv
from .end_user_utilities import measured_pwv

__author__ = 'Daniel Perrefort'
__copyright__ = 'Copyright 2017, Daniel Perrefort'
__credits__ = ['Azalee Bostroem', 'Jessica Kroboth',
               'Michael Wood-Vasey', 'Alexander Afanasyev']

__license__ = 'GPL V3'
__version__ = '0.10.0'
__email__ = 'djperrefort@gmail.com'
__status__ = 'Development'
