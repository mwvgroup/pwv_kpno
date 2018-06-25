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
[![release](https://img.shields.io/badge/version-0.11.6-blue.svg)]()
[![python](https://img.shields.io/badge/python-2.7,%203.6-blue.svg)]()
[![license](https://img.shields.io/badge/license-GPL%20v3.0-blue.svg)](https://www.gnu.org/licenses/gpl-3.0.en.html)
[![Build Status](https://travis-ci.org/mwvgroup/pwv_kpno.svg?branch=master)](https://travis-ci.org/mwvgroup/pwv_kpno)

For package documentation and installation instructions, please see
[https://mwvgroup.github.io/pwv_kpno/](https://mwvgroup.github.io/pwv_kpno/)

## Overview

**pwv_kpno** is a Python package for modeling the atmospheric absorption due
to H<sub>2</sub>O at Kitt Peak National Observatory. It provides atmospheric
models from 3000 to 12,000 Angstroms for years 2010 onward. Understanding atmospheric
effects is important when calibrating ground based astronomical observations.
Traditionally, determining the detailed atmospheric transmission function at a
given date and time required performing dedicated spectrographic observations.
**pwv_kpno** provides an alternative that can be performed at the user's
convenience.

Atmospheric absorption in the near-infrared is highly dependent on the column
density of precipitable water vapor (PWV). By measuring the delay of GPS
signals through the atmosphere, the [SuomiNet](http://www.suominet.ucar.edu)
project provides accurate PWV measurements for multiple, international
locations. The **pwv_kpno** package uses published SuomiNet data in conjunction
with MODTRAN models to determine the modeled atmospheric transmission function
at Kitt Peak in close to real time. The package also provides automated
retrieval and processing of SuomiNet data, allowing photometry to typically be
corrected within an hour of observation.

**pwv_kpno** is open source software released under the GNU General Public
License. Issues, pull requests, and feedback are welcome.

## How to Cite

If you use **pwv_kpno** as part of any published work or research, we ask that
you please use the following standard acknowledgement:

&nbsp;&nbsp;&nbsp;&nbsp;*This research made use of the pwv_kpno python package,*<br>
&nbsp;&nbsp;&nbsp;&nbsp;*an open source project that provides models for the*<br>
&nbsp;&nbsp;&nbsp;&nbsp;*atmospheric absorption due to precipitable water vapor*<br>
&nbsp;&nbsp;&nbsp;&nbsp;*in the near-infrared (Perrefort, Wood-Vasey et al. 2018)*<br>

If the publisher allows, you can also include a footnote with a link pointing
to the documentation page
[https://mwvgroup.github.io/pwv_kpno/](https://mwvgroup.github.io/pwv_kpno/)

# Acknowledgements

This work is based in part on observations taken at Kitt Peak National
Observatory, National Optical Astronomy Observatory (NOAO Prop. IDs: 2011B-0482
and 2012B-0500; PI: Wood-Vasey), which is operated by the Association of
Universities for Research in Astronomy (AURA) under a cooperative agreement
with the National Science Foundation.

# Additional Resources

- An up time monitor for the SuomiNet website can be found
  [here](https://stats.uptimerobot.com/gn1xqsJvj)

- For more information on the Kitt Peak National Observatory, see
  [www.noao.edu/kpno/](www.noao.edu/kpno/)

- To learn more about the SuomiNet project, see
  [www.suominet.ucar.edu/overview.html](www.suominet.ucar.edu/overview.html)

- For an additional example on the correlation between GPS signals and
  atmospheric modeling, see
  [Blake and Shaw, 2011](https://arxiv.org/abs/1109.6703)
