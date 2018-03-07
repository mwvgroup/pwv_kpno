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
[![release](https://img.shields.io/badge/version-0.10.2-blue.svg)]()
[![python](https://img.shields.io/badge/python-2.7,%203.6-blue.svg)]()
[![license](https://img.shields.io/badge/license-GPL%20v3.0-blue.svg)](https://www.gnu.org/licenses/gpl-3.0.en.html)
[![Build Status](https://travis-ci.org/mwvgroup/pwv_kpno.svg?branch=master)](https://travis-ci.org/mwvgroup/pwv_kpno)

## 1) Package Description

**pwv_kpno** is a Python package for modeling the atmospheric transmission
function at Kitt Peak National Observatory. It provides atmospheric models
in the optical and near-infrared (7000 to 11000 Angstroms) for years 2010
onward. Knowing the atmospheric transmission function is important when
correcting ground based astronomical observations for atmospheric effects.
Observed spectra are typically corrected using observations of a telluric
standard star. **pwv_kpno** provides an alternative method that does not
require dedicated observation time, and that can be run at the observer's
convenience.

When working in the optical and near-infrared, the atmospheric transmission
function is highly dependent on the amount of precipitable water vapor (PWV)
in the atmosphere. **pwv_kpno** models the atmospheric transmission using PWV
measurements provided by the SuomiNet Project. SuomiNet measures PWV values
by relating the delay in GPS signals to PWV levels in the atmosphere. This
package uses measurements taken by GPS receivers located at Kitt Peak AZ,
Amado AZ, Sahuarita AZ, Tucson AZ, and Tohono O'odham Community College.

For more details on the correlation between GPS signals and PWV levels see
[Blake and Shaw, 2011](https://arxiv.org/abs/1109.6703). To learn more about
the SuomiNet project, see their website [here](http://www.suominet.ucar.edu/overview.html).

## 2) Documentation

Documentation for **pwv_kpno**, including installation and setup instructions,
can be found online [here](https://mwvgroup.github.io/pwv_kpno/).
