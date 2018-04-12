*********************
Modeling a Black Body
*********************

The `blackbody_with_atm` module provides functions for modeling the effects of
PWV absorption on a black body. This includes modeling the spectral energy
distribution, the magnitude in a given band, and the error in photometric zero
point. We suggest importing this module as `bb_atm`.

Generating an SED
=================

If desired, the SED of a black body
    without atmospheric effects can also be achieved by specifying a PWV level of zero.

.. autofunction:: pwv_kpno.blackbody_with_atm.transmission

Example:
--------

    >>> from pwv_kpno import blackbody as bb_atm
    >>>
    >>> temp = 8000
    >>> wavelength = np.arange(7000, 10000, 100)
    >>> pwv = 15
    >>>
    >>> sed = bb_atm.sed(temp, wavelength, pwv)
    >>> print(sed)

      [67943236.6960908, 70958962.4114214, ...,
       30913697.9848318, 29947238.7968099]

Magnitude
=========

Using the \code{magnitude} function, users can also determine the magnitude of a black body in a given band. For
    example, in the $i$ band, which ranges from $7,000$ to $8,500 \rm{\AA}$, the magnitude of a black body is found by
    running

    As in the previous example, the magnitude of a blackbody without the effects of atmospheric absorption can be found
    by specifying a PWV level of zero. pwv\_kpno only provides models for the atmospheric transmission between $7,000$
    and $10,000$ angstroms. If the \code{magnitude} function as asked to determine the magnitude for a band that
    extends outside this range, and error is raised.

.. autofunction:: pwv_kpno.blackbody_with_atm.transmission_pwv

Example:
--------

    >>> i_band = (7000, 8500)
    >>> bb_mag = bb_atm.magnitude(temp, i_band, pwv)


Estimating Zero Point Error
===========================

.. autofunction:: pwv_kpno.blackbody_with_atm.zp_error

Example:
--------

    >>> reference_star_temp = 4000
    >>> other_star_temps = 10000
    >>> bias = zp_bias(reference_star_temp, other_star_temps, i_band, pwv)
