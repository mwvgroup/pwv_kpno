#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

#    This file is part of the pwv_kpno package.
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

"""
Package description
-------------------
This package models the transmission function due to perciptible water vapor
(PWV) at Kitt Peak for years 2010 and later. Models are created using PWV
measurments provided by the SuomiNet Project. SuomiNet measures PWV values
by relating the delay in GPS signals to PWV levels in the atmosphere. This
package uses measurments taken by GPS recievers located at Kitt Peak AZ,
Amado AZ, Sahuarita AZ, Tucson AZ, and Tohono O'odham Community College.

For more details on the correlation betwean GPS signals and PWV levels see
Blake and Shaw, 2011. For more details on the SuomiNet project see
http://www.suominet.ucar.edu/overview.html .

Package Setup
-------------
This package relies on PWV measurments taken by the SuomiNet project. In
order to model the PWV transmission function for a given date, SuomiNet
data for that date must be available on the host machine. By default this
package contains SuomiNet data from 2010 through the end of 2016. It is
recomended to update the local SuomiNet data after installing / updating
the package, and periodically as necessary.

To download new SuomiNet data and update the locally stored PWV models,
use the `update_models` function:
        
    >>> import pwv_kpno
    >>> pwv_kpno.update_models()
            
Note that the update_models function requires the user to have permission
to write and modify files within the package directory.

Documentation
-------------
Help information and docstring is provided within the package's source code.
To view help information for a particular function, use the standard python
`help` function. This package consists of four primary functions. Usage
examples for these functions are provided below.

  Examples:

    1) update_models
    
    2) transmission
    # example of how to use to get a transmission spectra 
    
    3) To get an astropy table of the PWV measurments taken by SuomiNet for a
     given year, use the `measured_pwv` function. 
  
        >>> measured_data = pwv_kpno.measured_pwv(year=2013)
        >>> measured_data

        date   KITT    SA48
        int32 float64 float64
        ----- ------- -------
                    
                    
         ...    ...     ...

     The returned table will have one column for the datetime of each measuerment,
     and an additional column for each reciever with locally available data.
     The `date` column contains the datetime of each measurment in ""
     format. Successive columns contain the PWV values measured by a specific
     receiver. These columns are named using the SuomiNet ID for each reciever.
     All PWV values are returned in units of millimeters
     
       >>> measured_data['KITT'].units
       
       

  4) To get an astropy table of the modeled PWV at Kitt Peak used to determine
     the transmission, use the `modeled_pwv`.
     
       pwv_kpno.modeled_pwv(year)
       

  

    
"""

from create_pwv_models import update_models
from end_user_functions import modeled_pwv
from end_user_functions import measured_pwv
from end_user_functions import transmission

__version__ = '1.0.0'
__license__ = 'GPL V3'
__status__ = 'Development'

# -- Developer notes --

# print GPNU notice on cmd line start
# Get command line code running
# email Dick Joyce about pressure flatline

# compatibility with python 2
# atm model has wavlengths at unequal increments
# make sure models for atmosphere are actually correct

# create readme ("transmission function due to PWV" )
# finish setup.py




# dev notes - atm model can model more effects
# dev notes - Make sure config.txt and local data are present - there are no checks
# dev notes - reset config file, overwrite suomi data, and change DIST_YEAR variable in create_pwv_models.py



#next steps:
# Get transmission binned for certain wavelengths

# spectral energy distribution? convenience function to estimate error you would make
#    in calibration of image tricky - relative to stars used to calibrate in that field
#    assuming i calibrated with a star of this color, using some library, what error
#    did i make for something in z that i didn't take account for pwv absorption (if all stars 
#    have exact same sed, doesn't matter; stars are actually a range of colors, should have some
#    differential effect in delta magnitude in z band which is function of color of star) use
#    blackbody seds, after this is developed, can look at stellar seds (6500 redward is when you care about pwv)    
