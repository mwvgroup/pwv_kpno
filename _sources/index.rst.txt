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

|

********
Overview
********

**pwv_kpno** is a Python package for modeling the atmospheric transmission
function at Kitt Peak National Observatory. It provides atmospheric models
in the optical and near-infrared (7,000 to 10,000 Angstroms) for years 2010
onward. Knowing the atmospheric transmission function is important when
correcting ground based astronomical observations for atmospheric effects.
Observed spectra are typically corrected using observations of a telluric
standard star. **pwv_kpno** provides an alternative method that does not require
dedicated observation time, and that can be run at the observer's convenience.

When working in the optical and near-infrared, the atmospheric transmission
function is highly dependent on the amount of precipitable water vapor (PWV)
in the atmosphere. **pwv_kpno** models the atmospheric transmission using PWV
measurements provided by the SuomiNet Project. SuomiNet measures PWV values
by relating the delay in GPS signals to PWV levels in the atmosphere. This
package uses measurements taken by GPS receivers located at Kitt Peak AZ,
Amado AZ, Sahuarita AZ, Tucson AZ, and Tohono O'odham Community College.

For more details on the correlation between GPS signals and PWV levels see
`Blake and Shaw, 2011 <https://arxiv.org/abs/1109.6703>`_. To learn more about
the SuomiNet project see their website `here <http://www.suominet.ucar.edu/overview.html>`_.
If you're interested in the package source code, it can be found on
`GitHub <https://github.com/mwvgroup/pwv_kpno>`_.

*****************
Table of Contents
*****************

.. toctree::
    :maxdepth: 2
    :numbered:

    install
    modeling_the_atmosphere
    updating_data
    accessing_pwv_data
    for_developers

..
    ***********
    How to Cite
    ***********

    The **pwv_kpno** is maintained by Daniel J. Perrefort. If you use **pwv_kpno**
    as part of your research, please cite it in the following way:

    Todo: Insert example
