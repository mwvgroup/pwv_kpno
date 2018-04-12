***********************
Correcting Observations
***********************

Spectrographic Observations
===========================

In order to correct spectral observations for atmospheric effects, observed
spectra are devided by the atmospheric transmission function. For demonstration
purposes, we consider the spectral energy distribution (SED) of a black body
under the effects of atmospheric absorption. For a temperature of 8,000 K, and
 a PWV level of 15 mm, this can be found as::

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

Since we know the PWV level used to generate this spectra, we can determine the
corresponding transmission function using the `transmission_pwv` function::

    >>> from pwv_kpno import pwv_trans
    >>> modeled_trans = pwv_trans.transmission_pwv(15)

In order to find the atmospheric transmission at each of the wavelength values
used to generate the black body, we use the `numpy` package to interpolate.

    >>> import numpy as np
    >>> trans_at_wavelength = np.interp(obs_wavelengths,
    >>>     modeled_trans["wavelength"],
    >>>     modeled_trans["transmission"])

Finally, the corrected spectrum can be found by dividing the observed flux
by the transmission `trans_at_wavelength` on a wavelength by wavelength basis.

    >>> corrected_spec = observed_spec.copy()
    >>> corrected_spec = np.divide(observed_spec["flux"], trans_at_wavelength)


Photometric Observations
========================
