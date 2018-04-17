*********************
Modeling a Black Body
*********************

The `blackbody_with_atm` module provides functions for modeling the effects of
PWV absorption on a black body. This includes modeling the spectral energy
distribution, the magnitude in a given band, and the error in photometric zero
point. We suggest importing this module as `bb_atm`.


Generating an SED
=================


.. autofunction:: pwv_kpno.blackbody_with_atm.sed

Example:
--------

.. code-block:: python
   :linenos:

    >>> from pwv_kpno import blackbody as bb_atm
    >>>
    >>> bb_temp = 8000
    >>> wavelength = np.arange(7000, 10000, 100)
    >>> pwv = 15
    >>>
    >>> sed = bb_atm.sed(bb_temp, wavelength, pwv)

**Note:** If desired, the SED of a black body without atmospheric effects can
also be achieved by specifying a PWV level of zero.

Magnitude
=========

The `magnitude` function returns the magnitude of a black body in a given band.
Since **pwv_kpno only provides models for the atmospheric transmission between
7,000 and 10,000 angstroms, if the specified band extends outside this range
an error is raised.

**Note:** The magnitude of a blackbody without the effects of atmospheric
absorption can be found by specifying a PWV level of zero.

.. autofunction:: pwv_kpno.blackbody_with_atm.transmission_pwv

Example:
--------

In the *i* band from 7,000 to 8,500 Angstroms, the magnitude of a
black body is found by running

.. code-block:: python
   :linenos:

    >>> bb_temp = 8000
    >>> i_band = (7000, 8500)
    >>> pwv = 15
    >>>
    >>> bb_mag = bb_atm.magnitude(bb_temp, i_band, pwv)

Example:
--------

In the *i* band from 7,000 to 8,500 Angstroms, the magnitude of a
black body is found by running

.. code-block:: python
   :linenos:

    >>> bb_temp = 8000
    >>> i_band = (7000, 8500)
    >>>
    >>> bb_mag = bb_atm.magnitude(temp, i_band, 0)

Estimating Zero Point Error
===========================

.. autofunction:: pwv_kpno.blackbody_with_atm.zp_bias

Example:
--------

.. code-block:: python
   :linenos:

    >>> reference_star_temp = 4000
    >>> other_star_temps = 10000
    >>> bias = zp_bias(reference_star_temp, other_star_temps, i_band, pwv)
