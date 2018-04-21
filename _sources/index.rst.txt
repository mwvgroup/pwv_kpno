.. figure::  _static/LOGO.png
   :align:   center

.. image:: https://img.shields.io/badge/version-0.10.1-blue.svg
    :target: https://pypi.python.org/pypi/pwv-kpno/

.. image:: https://img.shields.io/badge/python-2.7,%203.6,%203.7-blue.svg
    :target: #

.. image:: https://img.shields.io/badge/license-GPL%20v3.0-blue.svg
    :target: https://www.gnu.org/licenses/gpl-3.0.en.html

.. image:: https://travis-ci.org/mwvgroup/pwv_kpno.svg?branch=master
    :target: https://travis-ci.org/mwvgroup/pwv_kpno

.. toctree::
    :hidden:
    :numbered:

    install
    accessing_data
    atmospheric_modeling
    blackbody_modeling
    correcting_observations
    for_developers

|
|

********
Overview
********

**pwv_kpno** is a Python package for modeling the atmospheric absorption due to
H\ :sub:`2`\ O at Kitt Peak National Observatory. It provides atmospheric models
in the near-infrared (from 7,000 to 10,000 Angstroms) for years 2010 onward.
Understanding atmospheric absorption is important when calibrating ground
based astronomical observations. Traditionally, determining the detailed
atmospheric transmission function at a given date and time required performing
dedicated spectrographic observations. **pwv_kpno** provides an alternative
method that does not require dedicated observation time, and that can be
performed at the user's convenience.

Atmospheric absorption in the near-infrared is highly dependent on the column
density of precipitable water vapor (PWV). By measuring the delay of GPS signals
through the atmosphere, the `SuomiNet project
<http://www.suominet.ucar.edu/overview.html>`_ provides accurate PWV measurements
for multiple, international locations. The **pwv_kpno** package uses published
SuomiNet data in conjunction with MODTRAN models to determine the modeled
atmospheric transmission function at Kitt Peak in close to real time.
The package also provides automated retrieval and processing of SuomiNet data,
allowing photometry to typically be corrected within an hour of observation.

***********
How to Cite
***********

If you use **pwv_kpno** as part of any published work or research, we ask that
you cite Perrefort, Wood-Vasey et al. (`Arxiv <#>`_, `BibTeX <#>`_).
If there is not an appropriate place to cite the source paper, please use the
following standard acknowledgement:

    *This research made use of the pwv_kpno python package, an open source project that provides models for the atmospheric absorption due to precipitable water vapor in the near-infrared (Perrefort, Wood-Vasey et al. 2018)*

If the publisher allows, you can also include a footnote with a link pointing
to the documentation page
`https://mwvgroup.github.io/pwv_kpno/ <https://mwvgroup.github.io/pwv_kpno/>`_.

****************
Acknowledgements
****************

This work is based in part on observations at Kitt Peak National Observatory,
National Optical Astronomy Observatory (NOAO Prop. IDs: 2011B-0482 and
2012B-0500; PI: Wood-Vasey), which is operated by the Association of
Universities for Research in Astronomy (AURA) under a cooperative agreement
with the National Science Foundation.

This project uses data published by the SuomiNet project. We thank Teresa
Vanhove and the SuomiNet team for their assistance in answering questions over
the course of project development.

********************
Additional Resources
********************

- The package source code is publicly available on `GitHub <https://github.com/mwvgroup/pwv_kpno>`_.

- To learn more about the SuomiNet project, see their `website <http://www.suominet.ucar.edu/overview.html>`_.

- For an additional example on the correlation between GPS signals and atmospheric modeling, see `Blake and Shaw, 2011 <https://arxiv.org/abs/1109.6703>`_.
