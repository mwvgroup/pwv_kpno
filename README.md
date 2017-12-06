<h1 align="center">
  <img src="LOGO.png" height="140">
  <br>
</h1>

<h4 align="center">
Providing models of the atmospheric transmission function at
Kitt Peak National Observatory
</h4>

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
&nbsp;&nbsp;
[![release](https://img.shields.io/badge/version-0.10.0-blue.svg)]()
[![python](https://img.shields.io/badge/python-2.7,%203.6-blue.svg)]()
[![license](https://img.shields.io/badge/license-GPL%20v3.0-blue.svg)](https://www.gnu.org/licenses/gpl-3.0.en.html)
[![Code Climate](https://img.shields.io/codeclimate/github/mwvgroup/pwv_kpno.svg)](https://codeclimate.com/github/mwvgroup/pwv_kpno)

## Table of contents

- [1 Package Description](#1-package-description)
- [2 Installation](#2-installation)
  - [2.1 Install](#21-install)
  - [2.2 Setup](#22-setup)
- [3 Package Use](#3-package-use)
  - [3.1 Documentation](#31-documentation)
  - [3.2 Examples](#32-examples)
- [4 Future Development](#4-future-development)

## 1) Package Description

pwv_kpno is a Python package for modeling the atmospheric transmission
function at Kitt Peak National Observatory. It provides atmospheric models
in the optical and near-infrared (7000 to 11000 Angstroms) for years 2010
onward. Knowing the atmospheric transmission function is important when
correcting ground based astronomical observations for atmospheric effects.
Observed spectra are typically corrected using observations of a telluric
standard star. pwv_kpno provides an alternative method that does not require
dedicated observation time, and that can be run at the observer's convenience.

When working in the optical and near-infrared, the atmospheric transmission
function is highly dependent on the amount of precipitable water vapor (PWV)
in the atmosphere. pwv_kpno models the atmospheric transmission using PWV
measurements provided by the SuomiNet Project. SuomiNet measures PWV values
by relating the delay in GPS signals to PWV levels in the atmosphere. This
package uses measurements taken by GPS receivers located at Kitt Peak AZ,
Amado AZ, Sahuarita AZ, Tucson AZ, and Tohono O'odham Community College.
For more details on the correlation between GPS signals and PWV levels see
[Blake and Shaw, 2011](https://arxiv.org/abs/1109.6703). For more details on the SuomiNet project see
[http://www.suominet.ucar.edu/overview.html](http://www.suominet.ucar.edu/overview.html).

## 2) Installation

### 2.1 Install

This package can be installed using pip

    $ pip install pwv_kpno

Alternatively, you use the `setup.py` file

    $ python setup.py install --user

If you have issues installing the package with either method, ensure that the
following dependencies are installed in your Python environment: `'numpy',
'astropy', 'requests', 'pytz', 'scipy'`.

To run the test suite use

    $ python setup.py test

### 2.2 Setup

This package relies on PWV measurements taken by the SuomiNet project. In
order to model the PWV transmission function for a given date, SuomiNet data
for that date must be available on the host machine. By default, this package
contains all necessary SuomiNet data from 2010 through the end of 2016. It is
recommended to update the local SuomiNet data after installing or updating the
package, and periodically as necessary.

To download any SuomiNet data not included with this version of the pwv_kpno
package and update the locally stored PWV models, use the `update_models`
function:

    >>> import pwv_kpno
    >>> pwv_kpno.update_models()

The `update_models` function can also be used to download SuomiNet data for
a specific year:

    >>> pwv_kpno.update_models(year=2017)

Note that the update_models function requires the user to have permission
to write and modify files within the package directory.

## 3) Package Use

### 3.1 Documentation

The pwv_kpno package currently provides five functions: `available_data`
`update_models`, `measured_pwv`, `modeled_pwv`, and `transmission`.
Help information for each function can be accesed using the standard python
`help` function.

    available_data()
        Return a list of years for which SuomiNet data has been downloaded

        Return a list of years for which SuomiNet data has been downloaded to the
        local machine. Note that this list includes years for which any amount
        of data has been downloaded. It does not indicate if additional data has
        been released by SuomiNet for a given year that is not locally available.

        Args:
            None

        Returns:
            years (list): A list of years with locally available SuomiNet data


    update_models(year=None):
        Download data from SuomiNet and update the locally stored PWV model

        Update the locally available SuomiNet data by downloading new data from
        the SuomiNet website. Use this data to create an updated model for the PWV
        level at Kitt Peak. If a year is provided, only update data for that year.
        If not, download all available data from 2017 onward. Data for years from
        2010 through 2016 is included with this package version by default.

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
            data (astropy.table.Table): A table of measured PWV values in mm


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
            data (astropy.table.Table): A table of modeled PWV values in mm


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

### 3.2 Examples

#### Updating local SuomiNet data

Version 0.10.0 of this package is distributed with all the necessary SuomiNet
data from 2010 through 2016. To download any SuomiNet data published after
2016 use the `update_models` function:

    >>> # Download all available data from 2017 onward
    >>> updated_years = pwv_kpno.update_models()
    >>> updated_years

    [2017]

The `update_models` function will return a list of years for which data was
downloaded. Data can also be used to update data for a specific year:

    >>> pwv_kpno.update_models(2010)

    [2010]

#### Retrieving local SuomiNet data

To retrieve an astropy table of SuomiNet available on the local machine,
use the `measured_pwv` function:

    >>> measured_data = pwv_kpno.measured_pwv()
    >>> print(measured_data)

                date         KITT  P014  SA46  SA48  AZAM
                UTC           mm    mm    mm    mm    mm
        -------------------  ----  ----  ----  ----  ----
        2010-06-25 00:15:00    --    --  23.4  15.2    --
        2010-06-25 00:45:00    --    --  23.9  15.6    --
        2010-06-25 01:15:00    --    --  22.6  17.1    --
                        ...   ...   ...   ...   ...   ...

Results can also be refined by year, month, day, and hour. For example, data
taken on November 14, 2016 can be retrieved as follows:

    >>> pwv_kpno.measured_pwv(year=2016, month=11, day=14)

                date        KITT P014 SA46 SA48 AZAM
                UTC          mm   mm   mm   mm   mm
        ------------------- ---- ---- ---- ---- ----
        2016-11-14 00:15:00  4.7  6.7 10.4   --  7.9
        2016-11-14 00:45:00  4.3  6.5 10.3   --  7.5
        2016-11-14 01:15:00  3.9  6.5 10.1   --  8.0
                        ...  ...  ...  ...  ...  ...

Note that if no SuomiNet data is available during the specified datetime, the
returned table will be empty

    >>> pwv_data = pwv_kpno.measured_pwv(year=2016, month=11, day=11, hour=1)
    >>> len(pwv_data)

        0

#### Retrieving the PWV model

This package uses SuomiNet data to create a model for the PWV level at Kitt
Peak. To retrieve this model as an astropy table, use the `measured_pwv`
function:

    >>> modeled_pwv = pwv_kpno.modeled_pwv()
    >>> print(modeled_pwv)

                date             pwv
                UTC               mm
        -------------------  -------------
        2010-06-25 00:15:00  5.37705575203
        2010-06-25 00:45:00  5.51619053262
        2010-06-25 01:15:00  5.56017738737
                        ...  ...

Results can also be refined by year, month, day, and hour. For example,
model values for November 14, 2016 can be retrieved as follows:

    >>> modeled_pwv = pwv_kpno.modeled_pwv(year=2016, month=11, day=14)
    >>> print(modeled_pwv)

                date         PWV
                UTC           mm
        -------------------  ---
        2016-11-14 00:15:00  4.7
        2016-11-14 00:45:00  4.3
        2016-11-14 01:15:00  3.9
                        ...  ...

Note that the PWV model does not have a data point for every datetime. This
means that for some datetimes the returned table will be empty.

    >>> pwv_data = pwv_kpno.measured_pwv(year=2016, month=11, day=11, hour=1)
    >>> len(pwv_data)

        0

#### Generating an atmospheric transmission function

To return a model for the atmospheric transmission function for a specific
datetime, first create a datetime object. That object is then passed to the
`transmission` function along with an airmass value. For example, for an
airmass of 1.2, the transmission function at 2013-12-15 05:35:00 is given by:

    >>> from datetime import datetime
    >>> import pytz
    >>>
    >>> obsv_date = datetime(year=2013, month=12, day=15, hour=5, minute=35,
    >>>                      tzinfo=pytz.utc)
    >>>
    >>> trans = pwv_kpno.transmission(date=obsv_date, airmass=1.2)
    >>> print(trans)


        wavelength   transmission
        ------------- --------------
             7000.0 0.996573011501
        7001.00033344 0.993783855758
        7002.00066689 0.999867137883
              ...        ...

## 4) Future Development

For those interested in modifying or updating this package, a collection of
informal notes and instructions is maintained in [DEVNOTES.md](DEVNOTES.md).
