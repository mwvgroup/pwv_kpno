#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

#    This file is part of the pwv_kpno software package.
#
#    The pwv_kpno package is free software: you can redistribute it and/or
#    modify it under the terms of the GNU General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    The pwv_kpno package is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General
#    Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with pwv_kpno.  If not, see <http://www.gnu.org/licenses/>.

"""``pwv_kpno`` provides models for the atmospheric transmission function due
to precipitable water vapor (PWV). Using PWV measurements published by the
SuomiNet project (https://www.suominet.ucar.edu), the package provides access
to the modeled PWV concentration and/or atmospheric transmission for a given
date and time at customizable geographic locations. The atmospheric
transmission can also be determined manually for a given set of atmospheric
parameters.

Package Modules
---------------

+---------------------+---------------------------------------------------------+
| Module              | Description                                             |
+=====================+=========================================================+
| :ref:`defaults`     | Prebuilt receiver objects and transmission models.      |
+---------------------+---------------------------------------------------------+
| :ref:`downloads`    | Handles the downloading of data from SuomiNet servers.  |
+---------------------+---------------------------------------------------------+
| :ref:`file_parsing` | Parses files written in the the SuomiNet file format.   |
+---------------------+---------------------------------------------------------+
| :ref:`gps_pwv`      | PWV modeling and data access for given GPS locations.   |
+---------------------+---------------------------------------------------------+
| :ref:`transmission` | Models the PWV atmospheric transmission function.       |
+---------------------+---------------------------------------------------------+
| :ref:`types`        | Custom object types for PEP 484 support.                |
+---------------------+---------------------------------------------------------+
"""

from .gps_pwv import PWVModel

__authors__ = ['MWV Research Group']
__copyright__ = 'Copyright 2017, MWV Research Group'
__credits__ = [
    'Daniel Perrefort'
    'W. M. Wood-Vasey',
    'K. Azalee Bostroem',
    'Jessica Kroboth',
    'Tom Matheson',
]

__license__ = 'GPL V3'
__version__ = '2.0.0.dev6'
__email__ = 'djperrefort@pitt.edu'
__status__ = 'Release'


def plot_transmission(wavelengths, transmission):
    """Plot atmospheric transmission values as a function of wavelength

    Args:
        wavelengths: Array of wavelength values in units of Angstroms
        transmission: Array of dimensionless transmission values
    """

    import numpy as np
    from matplotlib import pyplot as plt

    fig, axis = plt.subplots()
    axis.fill_between(wavelengths, transmission, np.ones_like(transmission))

    axis.set_xlim(min(wavelengths), max(wavelengths))
    axis.set_ylim(0, 1)

    axis.set_xlabel(r'Wavelengths [$\AA$]')
    axis.set_ylabel(r'Atmospheric Transmission')
    return fig
