*********************
Modeling a Black Body
*********************

The ``blackbody_with_atm`` module provides functions for modeling the effects
of PWV absorption on a black body. We suggest importing this module as
``bb_atm``.

Generating an SED
=================

For a given array of wavelengths in Angstroms, the ``sed`` function returns
the corresponding spectral energy distribution of a black body as seen through
the atmosphere.

.. autofunction:: pwv_kpno.blackbody_with_atm.sed

Example:
--------

.. code-block:: python
    :linenos:

    >>> import numpy as np
    >>> from pwv_kpno import blackbody_with_atm as bb_atm
    >>>
    >>> bb_temp = 8000
    >>> wavelengths = np.arange(7000, 10000, 100)
    >>> pwv = 15
    >>>
    >>> sed = bb_atm.sed(bb_temp, wavelengths, pwv)

**Note:** If desired, the SED of a black body without atmospheric effects can
also be achieved by specifying a PWV level of zero.

Magnitude
=========

The ``magnitude`` function returns the absolute magnitude of a black body in a
given band as seen under the effects of PWV absorption. Since **pwv_kpno** only
provides models for the atmospheric transmission between 7,000 and 10,000
Angstroms, if the specified band extends outside this range an error is raised.


.. autofunction:: pwv_kpno.blackbody_with_atm.magnitude

Examples:
---------

In the *i* band from 7,000 to 8,500 Angstroms, the magnitude of a
black body is found by running

.. code-block:: python
    :linenos:

    >>> from pwv_kpno import blackbody_with_atm as bb_atm
    >>>
    >>> bb_temp = 8000
    >>> i_band = (7000, 8500)
    >>> pwv = 15
    >>>
    >>> bb_mag = bb_atm.magnitude(bb_temp, i_band, pwv)


**Note:** If desired, the absolute magnitude of a black body without
atmospheric effects can also be achieved by specifying a PWV level of zero.

Estimating Zero Point Error
===========================

Correcting photometric observations using tabulated values of a standard star
introduces residual error in the magnitudes of other stars with different
spectral types. The error in photometric zero point introduced by not
considering absorption by precipitable water vapor can be found using the
``zp_bias`` function.

.. autofunction:: pwv_kpno.blackbody_with_atm.zp_bias

Examples:
---------

.. code-block:: python
    :linenos:

    >>> from pwv_kpno import blackbody_with_atm as bb_atm
    >>>
    >>> reference_star_temp = 4000
    >>> other_star_temp = 10000
    >>> bias = bb_atm.zp_bias(reference_star_temp, other_star_temp, i_band, pwv)
