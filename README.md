<h1 align="center">
  <img src="LOGO.png" height="140">
  <br>
</h1>

<h4 align="center">
Providing models of the atmospheric transmission function at
Kitt Peak National Observatory
</h4>

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
[![release](https://img.shields.io/badge/version-1.0.0-blue.svg)]()
[![python](https://img.shields.io/badge/python-2.7,%203.5,%203.6,%203.7-blue.svg)]()
[![license](https://img.shields.io/badge/license-GPL%20v3.0-blue.svg)](https://www.gnu.org/licenses/gpl-3.0.en.html)
[![Build Status](https://travis-ci.org/mwvgroup/pwv_kpno.svg?branch=master)](https://travis-ci.org/mwvgroup/pwv_kpno)
[![Coverage Status](https://coveralls.io/repos/github/mwvgroup/pwv_kpno/badge.svg?branch=master)](https://coveralls.io/github/mwvgroup/pwv_kpno?branch=master)
[![arxiv](https://img.shields.io/badge/astro--ph.IM-arXiv%3A1806.09701-B31B1B.svg)](https://arxiv.org/abs/1806.09701)

For package documentation and installation instructions, please see
[https://mwvgroup.github.io/pwv_kpno/](https://mwvgroup.github.io/pwv_kpno/)

## Overview

**pwv_kpno** is a Python package for modeling the atmospheric absorption due
to H<sub>2</sub>O. It provides atmospheric models from 3,000 to 12,000 
Angstoms at a resolution of 0.05 Angstroms.

Atmospheric absorption in the near-infrared is highly dependent on the column
density of precipitable water vapor (PWV). By measuring the delay of GPS
signals through the atmosphere, the [SuomiNet project](https://www.suominet.ucar.edu)
provides accurate PWV measurements for multiple, international locations. The
**pwv_kpno** package  uses published SuomiNet data in conjunction with MODTRAN
models to determine  the modeled atmospheric transmission function as a function
of date and time.

By default the package provides access to the time dependent transmission
function at Kitt Peak National Observatory. However, this package is designed
to be easily extensible to other locations around within the SuomiNet Network.
Additionally, **pwv_kpno** provides access to atmospheric models as a function of
PWV, which is independent of a geographical location.

## Contributing and Attribution

**pwv_kpno** is open source software released under the GNU General Public
License. Issues, pull requests, and feedback are welcome. Additionally, pull
requests introducing custom configuration files that extend **pwv_kpno** to new
locations are also welcome.

If you use **pwv_kpno** as part of any published work or research, we ask that
you please use the following standard acknowledgement:

&nbsp;&nbsp;&nbsp;&nbsp;*This research made use of the pwv_kpno python package,*<br>
&nbsp;&nbsp;&nbsp;&nbsp;*an open source project that provides models for the*<br>
&nbsp;&nbsp;&nbsp;&nbsp;*atmospheric absorption due to precipitable water vapor*<br>
&nbsp;&nbsp;&nbsp;&nbsp;*in the near-infrared (Perrefort, Wood-Vasey et al. 2018)*<br>

If the publisher allows, you can also include a footnote with a link pointing
to the documentation page:
[https://mwvgroup.github.io/pwv_kpno/](https://mwvgroup.github.io/pwv_kpno/)

# Acknowledgements

This work is based in part on observations taken at Kitt Peak National
Observatory, National Optical Astronomy Observatory (NOAO Prop. IDs: 2011B-0482
and 2012B-0500; PI: Wood-Vasey), which is operated by the Association of
Universities for Research in Astronomy (AURA) under a cooperative agreement
with the National Science Foundation.

This work was supported in part by the US Department of Energy Office of Science 
under DE-SC0007914.

# Additional Resources

- An up time monitor for the SuomiNet website can be found
  [here](https://stats.uptimerobot.com/gn1xqsJvj)

- For more information on the Kitt Peak National Observatory, see
  [www.noao.edu/kpno/](https://www.noao.edu/kpno/)

- To learn more about the SuomiNet project, see
  [www.suominet.ucar.edu/overview.html](http://www.suominet.ucar.edu/overview.html)

- For an additional example on the correlation between GPS signals and
  atmospheric modeling, see
  [Blake and Shaw, 2011](https://arxiv.org/abs/1109.6703)
