.. |version| image:: https://img.shields.io/badge/version-1.0.0-blue.svg
   :target: https://pypi.python.org/pypi/pwv-kpno/

.. |python| image:: https://img.shields.io/badge/python-3.5+-blue.svg
   :target: #

.. |license| image:: https://img.shields.io/badge/license-GPL%20v3.0-blue.svg
   :target: https://www.gnu.org/licenses/gpl-3.0.en.html

.. |travis| image:: https://travis-ci.org/mwvgroup/pwv_kpno.svg?branch=master
   :target: https://travis-ci.org/mwvgroup/pwv_kpno

.. |cover| image:: https://coveralls.io/repos/github/mwvgroup/pwv_kpno/badge.svg?branch=master
   :target: https://coveralls.io/github/mwvgroup/pwv_kpno?branch=master

.. |arxiv| image:: https://img.shields.io/badge/astro--ph.IM-arXiv%3A1806.09701-B31B1B.svg
   :target: https://arxiv.org/abs/1806.09701

.. rst-class:: logo
.. figure::  ../static/images/LOGO.png
   :align:   center

.. rst-class:: badges

   +-------------------------------------------------------+
   | |version| |python| |license| |travis| |cover| |arxiv| |
   +-------------------------------------------------------+

.. toctree::
   :hidden:
   :titlesonly:
   :caption: Examples:

   examples/modeling.rst
   examples/downloading_pwv_data.rst
   examples/data_cuts.rst
   examples/correcting_photometry.rst

.. toctree::
   :hidden:
   :titlesonly:
   :caption: API Documentation:

   api/pwv_kpno
   api/defaults
   api/downloads
   api/file_parsing
   api/gps_pwv
   api/transmission
   api/types

.. toctree::
   :hidden:
   :titlesonly:
   :caption: Science Validation:

   validation/overview
   validation/data_handling
   validation/pwv_modeling
   validation/data_cuts
   validation/blackbody
   validation/transmission_function

|

What is *pwv_kpno*?
===================

**pwv_kpno** is an open-source Python package for modeling the transmission of
light through Earth's atmosphere due to atmospheric water vapor. Using GPS
measurements of the atmosphere, the package provides transmission models
for user definable sites as a function of date, time, and airmass. Customizable
transmission models are also available independent of location (i.e., using
user defined parameters instead of GPS based measurements) and span a wavelength
coverage of 3,000 to 12,000 Angstroms.

.. doctest:: python

   >>> import numpy as np
   >>> import pwv_kpno
   >>> from pwv_kpno.defaults import v1_transmission

   >>> # Define wavelength values in units of angstroms
   >>> wavelengths = np.arange(3000, 12000)
   >>> transmission = v1_transmission(pwv=5, wave=wavelengths)
   >>> fig = pwv_kpno.plot_transmission(wavelengths, transmission)
   >>> fig.show()


How it Works
------------

**pwv_kpno** is based on public data taken by the SuomiNet project:
a meteorological initiative that provides semi-hourly precipitable water vapor
(PWV) measurements for hundreds of GPS receivers worldwide. The **pwv_kpno**
package uses published SuomiNet data in conjunction with MODTRAN / LIBRADTRAN
models to modeled the time-dependent atmospheric transmission.

Contributing and Attribution
----------------------------

The **pwv_kpno** package is open source software released under the GNU General
Public License. Issues raised on `GitHub <https://github.com/mwvgroup/pwv_kpno>`_
and pull requests from contributors are welcome.
If you use **pwv_kpno** as part of any published work or research, we ask that
you please cite `Perrefort, Wood-Vasey et al. 2018 <https://arxiv.org/abs/1806.09701>`_.
If the publisher allows, you are encouraged to also include a footnote with a
link pointing at this documentation page.

|

.. rst-class:: home_table

+----------------------------------------------------------------------------------+--------------------------------------------------------------------------------------+
| Acknowledgements                                                                 | Additional Resources                                                                 |
+==================================================================================+======================================================================================+
|  This work is based in part on observations taken at Kitt Peak National          | 1. The official **pwv_kpno** paper is available on                                   |
|  Observatory, National Optical Astronomy Observatory (NOAO Prop. IDs: 2011B-0482 | `Arxiv.org <https://arxiv.org/abs/1806.09701>`_.                                     |
|  and 2012B-0500; PI: Wood-Vasey), which is operated by the Association of        +--------------------------------------------------------------------------------------+
|  Universities for Research in Astronomy (AURA) under a cooperative agreement     | 2. An up time monitor for the SuomiNet web server can be found                       |
|  with the National Science Foundation.                                           | `here <https://stats.uptimerobot.com/gn1xqsJvj/780552028>`_.                         |
|                                                                                  +--------------------------------------------------------------------------------------+
|  This work was supported in part by the US Department of Energy Office of        | 3. To learn more about the SuomiNet project, see                                     |
|  Science under DE-SC0007914.                                                     | `suominet.ucar.edu <http://www.suominet.ucar.edu/overview.html>`_.                   |
|                                                                                  +--------------------------------------------------------------------------------------+
|                                                                                  | 4. For an additional example on the correlation between GPS signals and              |
|                                                                                  | atmospheric modeling, see `Blake and Shaw, 2011 <https://arxiv.org/abs/1109.6703>`_. |
|                                                                                  |                                                                                      |
|                                                                                  |                                                                                      |
|                                                                                  |                                                                                      |
|                                                                                  |                                                                                      |
+----------------------------------------------------------------------------------+--------------------------------------------------------------------------------------+
