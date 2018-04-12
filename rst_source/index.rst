.. figure::  _static/LOGO.png
   :align:   center

.. image:: https://img.shields.io/badge/version-0.10.1-blue.svg
    :target: https://pypi.python.org/pypi/pwv-kpno/

.. image:: https://img.shields.io/badge/python-2.7,%203.6-blue.svg
    :target: #

.. image:: https://img.shields.io/badge/license-GPL%20v3.0-blue.svg
    :target: https://www.gnu.org/licenses/gpl-3.0.en.html

.. image:: https://travis-ci.org/mwvgroup/pwv_kpno.svg?branch=master
    :target: https://travis-ci.org/mwvgroup/pwv_kpno

.. toctree::
    :hidden:
    :numbered:

    install
    updating_data
    atmospheric_modeling
    blackbody_modeling
    correcting_observations
    for_developers

|
|

********
Overview
********

**pwv_kpno** is a Python package for modeling the atmospheric transmission
function at Kitt Peak National Observatory. It provides atmospheric models
in the near-infrared (7,000 to 10,000 Angstroms) for years 2010 onward.
Characterizing the atmospheric absorption is important when calibrating ground
based astronomical observations. Traditionally, determining the detailed
atmospheric transmission function required dedicated spectrographic
observations. **pwv_kpno** provides an alternative method that does not require
dedicated observation time, and that can be run at the observer's convenience.

When working in the optical and near-infrared, the atmospheric transmission
function is highly dependent on the amount of precipitable water vapor (PWV)
in the atmosphere. **pwv_kpno** models the atmospheric transmission using PWV
measurements provided by the SuomiNet Project. SuomiNet measures PWV values
by relating the delay in GPS signals to PWV levels in the atmosphere. This
package uses measurements taken by GPS receivers located at Kitt Peak AZ,
Amado AZ, Sahuarita AZ, Tucson AZ, and Tohono O'odham Community College.To seeHere

***********
How to Cite
***********

If you use **pwv_kpno** as part of any published work or research, we ask that
you cite Perrefort, Wood-Vasey et al. (`Arxiv <#>`_, `BibTeX <#>`_).
If there is not an appropriate place to cite the source paper, please use the
following standard acknowledgement:

    *This research made use of the pwv_kpno python package, an open source project that provides models for the atmospheric transmission and related effects (Perrefort, Wood-Vasey et al. 2018)*

If the publisher allows, you can also include a link pointing to the
documentation page https://mwvgroup.github.io/pwv_kpno/ .

********************
Additional Resources
********************

- The package source code is publicly available on `GitHub <https://github.com/mwvgroup/pwv_kpno>`_.

- To learn more about the SuomiNet project, see their `website <http://www.suominet.ucar.edu/overview.html>`_.

- For an additional example on the correlation between GPS signals and atmospheric modeling, see `Blake and Shaw, 2011 <https://arxiv.org/abs/1109.6703>`_.
