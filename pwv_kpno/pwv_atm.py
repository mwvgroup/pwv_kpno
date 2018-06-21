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

"""This module provides access PWV measurements for Kitt Peak and the modeled
PWV transmission function.

For full documentation on a function use the builtin Python `help` function
or see https://mwvgroup.github.io/pwv_kpno/.

An Incomplete Guide to Getting Started:

    To check what years data is locally available for:

      >>> from pwv_kpno import pwv_atm
      >>> pwv_atm.available_data()


    To update the locally available data with any new measurements:

      >>> pwv_atm.update_models()


    To determine the PWV concentration at Kitt Peak for a datetime:

      >>> from datetime import datetime
      >>> import pytz
      >>>
      >>> obsv_date = datetime(year=2013,
      >>>                      month=12,
      >>>                      day=15,
      >>>                      hour=5,
      >>>                      minute=35,
      >>>                      tzinfo=pytz.utc)
      >>>
      >>> pwv = pwv_atm.pwv_date(obsv_date)


    To retrieve the atmospheric model for a line of sight PWV concentration:

      >>> pwv_atm.trans_for_pwv(pwv)


    To retrieve the atmospheric model for a datetime:

      >>> pwv_atm.trans_for_date(date=obsv_date, airmass=1.2)


    To access the PWV measurements as an astropy table:

      >>> # All locally available PWV measurements
      >>> pwv_atm.measured_pwv()
      >>>
      >>> # All PWV measurements taken on November 14, 2016
      >>> pwv_atm.measured_pwv(year=2016, month=11, day=14)


    To access the modeled PWV level at Kitt Peak as an astropy table:

      >>> # The entire model from 2010 to present
      >>> pwv_atm.modeled_pwv()
      >>>
      >>> # The modeled PWV level only for November 14, 2016
      >>> pwv_atm.modeled_pwv(year=2016, month=11, day=14)
"""

from ._serve_pwv_data import available_data
from ._serve_pwv_data import pwv_date
from ._serve_pwv_data import measured_pwv
from ._serve_pwv_data import modeled_pwv
from ._update_pwv_model import update_models
from ._transmission import trans_for_date
from ._transmission import trans_for_pwv

__authors__ = ['Daniel Perrefort']
__copyright__ = 'Copyright 2017, Daniel Perrefort'

__license__ = 'GPL V3'
__email__ = 'djperrefort@pitt.edu'
__status__ = 'Development'
