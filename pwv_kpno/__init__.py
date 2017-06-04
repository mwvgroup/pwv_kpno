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

"""
Package Description
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
package contains all necessary SuomiNet data from 2010 through the end of
2016. It is recomended to update the local SuomiNet data after installing
or updating the package, and periodically as necessary.

To download any SuomiNet data not included with this version of the pwv_kpno
package and update the locally stored PWV models, use the `update_models` 
function:
        
    >>> import pwv_kpno
    >>> pwv_kpno.update_models()
 
The `update_models` function can also be used to download SuomiNet data for
a specific year:

    >>> import pwv_kpno
    >>> pwv_kpno.update_models(year=2017)

Note that the update_models function requires the user to have permission
to write and modify files within the package directory.
         

Documentation
-------------
Help information and docstring is provided within the package's source code.
To view help information for a particular function, use the standard python
`help` function. 

    available_data()
        Return a set of years for which SuomiNet data has been downloaded

        Return a set of years for which SuomiNet data has been downloaded to the
        local machine. Note that this function includes years for which any amount
        of data has been downloaded. It does not indicate if additional data has
        been released by SuomiNet for a given year that is not locally available.

        Args:
            None

        Returns:
            years (set): A set of years with locally available SuomiNet data


    update_models(year=None):
        Download data from SuomiNet and update the locally stored PWV model

        Update the locally available SuomiNet data by downloading new data from the
        SuomiNet website. Use this data to create an updated model for the PWV
        level at Kitt Peak. If a year is provided, only update data for that year.
        If not, download all available data from 2017 onward that is not already
        on the local machine. Data for years from 2010 through 2016 is included
        with this package version by default.

        Args:
            year (int): A Year from 2010 onward

        Returns:
            updated_years (list): A list of years for which models where updated


    measured_pwv(year=None, month=None, day=None, hour=None):
        Return an astropy table of PWV measurements taken by SuomiNet

        Return an astropy table of precipitable water vapor (PWV) measurements
        taken by the SuomiNet project. The first column is named 'date' and
        contains the UTC datetime of each measurement. Successive columns are
        named using the SuomiNet IDs for different locations and contain PWV
        measurements for that location in millimeters. By default the returned
        table contains all locally available SuomiNet data. Results can be
        refined by year, month, day, and hour by using the keyword arguments.

        Args:
            year  (int): The year of the desired PWV data
            month (int): The month of the desired PWV data
            day   (int): The day of the desired PWV data
            hour  (int): The hour of the desired PWV data in 24-hour format

        Returns:
            pwv_data (astropy.table.Table): A table of measured PWV values in mm


    modeled_pwv(year=None, month=None, day=None, hour=None):
        Return an astropy table of the modeled PWV at Kitt Peak

        Return a model for the precipitable water vapor level at Kitt Peak as an
        astropy table. The first column of the table is named 'date' and contains
        the UTC datetime of each modeled value. The second column is named 'pwv',
        and contains PWV values in millimeters. By default this function returns
        modeled values from 2010 onward. Results can be restricted to a specific
        year, month, day, and hour by using the key word arguments.

        Args:
            year  (int): The year of the desired PWV data
            month (int): The month of the desired PWV data
            day   (int): The day of the desired PWV data
            hour  (int): The hour of the desired PWV data in 24-hour format

        Returns:
            pwv_data (astropy.table.Table): A table of modeled PWV values in mm


    transmission(date, airmass):
        Return a model for the atmospheric transmission function due to PWV

        For a given datetime and airmass, return a model for the atmospheric
        transmission function due to precipitable water vapor (PWV) at Kitt Peak.
        The modeled transmission is returned as an astropy table with the columns
        'wavelength' and 'transmission'. Wavelength values range from 7000 to
        10,000 angstroms.

        Args:
            date (datetime.datetime): The datetime of the desired model
            airmass          (float): The airmass of the desired model

        Returns:
            trans_func (astropy.table.Table): The modeled transmission function

Examples
-------- 

    1) transmission
    # example of how to use to get a transmission spectra  t
    
    2) available_data
    
    3) update_models
    
    4) To get an astropy table of the PWV measurments taken by SuomiNet for a
     given year, use the `measured_pwv` function. 
  
        >>> measured_data = pwv_kpno.measured_pwv()
        >>> print(measured_data)
                
                date         KITT  P014  SA46  SA48  AZAM
                UTC           mm    mm    mm    mm    mm 
        -------------------  ----  ----  ----  ----  ----
        2010-06-25 00:15:00    --    --  23.4  15.2    --
        2010-06-25 00:45:00    --    --  23.9  15.6    --        
                        ...   ...   ...   ...   ...   ...
        2017-05-30 18:15:00   8.7    --  13.7    --  12.8

     The `date` column contains the datetime of each measurment in UTC format.
     Successive columns contain the PWV values measured by specific GPS
     receivers, and are named using the SuomiNet ID for each reciever.
     Results can be refined to include only a specific year, month, day, and hour.
     
        >>> pwv_kpno.measured_pwv(year=2016, month=11, day=14)
        
                date        KITT P014 SA46 SA48 AZAM
                UTC          mm   mm   mm   mm   mm 
        ------------------- ---- ---- ---- ---- ----
        2016-11-14 00:15:00  4.7  6.7 10.4   --  7.9
        2016-11-14 00:45:00  4.3  6.5 10.3   --  7.5
        2016-11-14 01:15:00  3.9  6.5 10.1   --  8.0
                        ...  ...  ...  ...  ...  ...
     
       >>> measured_data['KITT'].units
  
"""

from end_user_functions import update_models
from end_user_functions import modeled_pwv
from end_user_functions import measured_pwv
from end_user_functions import transmission

__version__ = '1.0.0'
__author__ = 'Daniel Perrefort'
__email__ = 'djperrefort@gmail.com'
__copyright__ = 'Copyright 2017, Daniel Perrefort'
__license__ = 'GPL V3'
__status__ = 'Development'
