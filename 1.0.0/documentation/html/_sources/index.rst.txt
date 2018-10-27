.. |version| image:: https://img.shields.io/badge/version-1.0.0-blue.svg
    :target: https://pypi.python.org/pypi/pwv-kpno/

.. |python| image:: https://img.shields.io/badge/python-2.7,%203.5+-blue.svg
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
.. figure::  _static/LOGO.png
    :align:   center

.. rst-class:: badges

   +-------------------------------------------------------+
   | |version| |python| |license| |travis| |cover| |arxiv| |
   +-------------------------------------------------------+

.. toctree::
    :hidden:
    :numbered:

    install
    sites_and_settings
    accessing_data
    atmospheric_modeling
    blackbody_modeling

|

What is pwv_kpno?
=================

**pwv_kpno** is a scientific Python package that provides models for the
atmospheric transmission due to precipitable water vapor (PWV) at user
specified sites. By measuring the delay of dual-band GPS signals traveling
through the atmosphere, it is possible to determine the PWV column density
along the line of sight. **pwv_kpno** leverages this principle to provide
atmospheric models for user definable sites as a function of date,
time, and airmass. Using the package, ground-based photometric observations
taken between 3,000 and 12,000 Å can be easily corrected for atmospheric
effects due to PWV.

How it Works
============

The SuomiNet project is a meteorological initiative that provides semi-hourly
PWV measurements for hundreds of GPS receivers worldwide. The **pwv_kpno**
package uses published SuomiNet data in conjunction with MODTRAN models to
determine the modeled, time-dependent atmospheric transmission.
By default, the package provides access to the modeled transmission
function at Kitt Peak National Observatory. However, the package is designed
to be easily extensible to other locations within the SuomiNet Network.
Additionally, **pwv_kpno** provides access to atmospheric models as a function
of PWV, which is independent of geographical location.

|

.. rst-class:: home_table

+---------------------------------------------------------------------------------+----------------------------------------------------------------------------------+--------------------------------------------------------------------------------------+
| Contributing and Attribution                                                    | Acknowledgements                                                                 | Additional Resources                                                                 |
+=================================================================================+==================================================================================+======================================================================================+
| *pwv_kpno* is open source software released under the GNU General Public        |  This work is based in part on observations taken at Kitt Peak National          | 1. The official **pwv_kpno** paper is available on                                   |
| License. Issues raised on `GitHub <https://github.com/mwvgroup/pwv_kpno>`_ and  |  Observatory, National Optical Astronomy Observatory (NOAO Prop. IDs: 2011B-0482 | `Arxiv.org <https://arxiv.org/abs/1806.09701>`_.                                     |
| pull requests from contributors are welcome. Additionally, pull requests        |  and 2012B-0500; PI: Wood-Vasey), which is operated by the Association of        +--------------------------------------------------------------------------------------+
| introducing default configuration files for new sites are also welcome.         |  Universities for Research in Astronomy (AURA) under a cooperative agreement     | 2. An up time monitor for the SuomiNet web server can be found                       |
|                                                                                 |  with the National Science Foundation.                                           | `here <https://stats.uptimerobot.com/gn1xqsJvj/780552028>`_.                         |
|                                                                                 |                                                                                  +--------------------------------------------------------------------------------------+
| If you use **pwv_kpno** as part of any published work or research, we ask that  |  This work was supported in part by the US Department of Energy Office of        | 3. To learn more about the SuomiNet project, see                                     |
| you please cite                                                                 |  Science under DE-SC0007914.                                                     | `suominet.ucar.edu <http://www.suominet.ucar.edu/overview.html>`_.                   |
| `Perrefort, Wood-Vasey et al. 2018 <https://arxiv.org/abs/1806.09701>`_         |                                                                                  +--------------------------------------------------------------------------------------+
| If the publisher allows, you can also include a footnote with a link pointing   |                                                                                  | 4. For an additional example on the correlation between GPS signals and              |
| to this documentation page.                                                     |                                                                                  | atmospheric modeling, see `Blake and Shaw, 2011 <https://arxiv.org/abs/1109.6703>`_. |
|                                                                                 |                                                                                  |                                                                                      |
|                                                                                 |                                                                                  |                                                                                      |
|                                                                                 |                                                                                  |                                                                                      |
|                                                                                 |                                                                                  |                                                                                      |
+---------------------------------------------------------------------------------+----------------------------------------------------------------------------------+--------------------------------------------------------------------------------------+
