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
[Blake and Shaw, 2011](https://arxiv.org/abs/1109.6703). For more details on
the SuomiNet project see
[http://www.suominet.ucar.edu/overview.html](http://www.suominet.ucar.edu/overview.html).

## 2) Installation

### 2.1 Install

This package can be installed using the pip package manager

    pip install pwv_kpno

Alternatively, you use the `setup.py` file

    python setup.py install --user

Both installation methods should automatically install any missing necessary
dependencies. However, if you have issues installing the package, ensure\
that these dependencies are present in your enviornment by installing them manually.
To do so with pip run: 
 
 
    pip install numpy
    pip install astropy
    pip install requests
    pip install pytz
    pip install scipy

If desired, the test suite can be run using the command:

    python setup.py test

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

