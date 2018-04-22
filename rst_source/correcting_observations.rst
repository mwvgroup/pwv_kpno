***********************
Correcting Observations
***********************

Examples are provided on how to correct astronomical observations for
atmospheric effects. For demonstration purposes, the following examples
exclusively consider correcting observations of a black body.

Spectrographic Observations
===========================

In order to correct specrographic observations for atmospheric effects,
observed spectra are divided by the atmospheric transmission function. As
an example, consider the spectral energy distribution (SED) of a black body
under the effects of atmospheric absorption. For a temperature of 8,000 K, and
a PWV level of 15 mm, this can be found as::

    >>> from pwv_kpno import blackbody_with_atm as bb_atm
    >>> import numpy as np
    >>>
    >>> temp = 8000
    >>> wavelength = np.arange(7000, 10000, 100)
    >>> pwv = 15
    >>>
    >>> sed = bb_atm.sed(temp, wavelength, pwv)
    >>> print(sed)

      [67943236.6960908, 70958962.4114214, ...,
       30913697.9848318, 29947238.7968099]

Since we know the PWV level used to generate this spectra, we can determine the
corresponding transmission function using the ``trans_for_pwv`` function::

    >>> from pwv_kpno import pwv_atm
    >>>
    >>> modeled_trans = pwv_atm.trans_for_pwv(15)
    >>> print(modeled_trans)

              wavelength        transmission
               Angstrom              %
          ------------------ ------------------
                      7000.0 0.9198165020431311
           7001.000333444482 0.8590254136327501
           7002.000666888963 0.9967736288238565
                         ...                ...

In order to divide these two results, the SED at and the transmission function
must both be known for the same wavelength values. Since the SED is a well
behaved function, we interpolate the SED to match the wavelength sampling of
the transmission function. In general the transmission function not a smooth
function,which can yield innacuracies when interpolating.

Using the ``numpy`` package, we interpolate as follows:

    >>> sampled_sed = np.interp(modeled_trans["wavelength"],
    >>>                         obs_wavelengths,
    >>>                         sed)

The corrected spectrum can then be found by dividing the observed flux
by the transmission on a wavelength by wavelength basis.

    >>> corrected_spec = np.divide(sampled_sed, modeled_trans["transmission"])


Photometric Observations
========================
