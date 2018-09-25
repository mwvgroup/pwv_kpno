***********************************
Correcting Photometric Observations
***********************************

For an atmospheric transmission :math:`T(\lambda)`, the photometric correction
for an object with an intrinsic spectral energy distribution :math:`S(\lambda)`
is given by

.. math::
   C = \frac{\int S(\lambda) \cdot T(\lambda) \, d\lambda}
             {\int S(\lambda) \, d\lambda}

where the integration bounds are defined by the wavelength range of the
photometric bandpass. In practice an SED of the desired object may not be
available. In such a case spectral templates should be used instead.

For demonstration purposes, we consider an observation of a black body. Note
that product in the numerator :math:`S(\lambda) \cdot T(\lambda)` represents
the SED under the influence of atmospheric effects. For a photometric
observation taken in the *i* band (7,000 to 8,500 :math:`\unicode{x212B}`),
the integration arguments can be found as:

.. code-block:: python
    :linenos:

    >>> from pwv_kpno import blackbody_with_atm as bb_atm
    >>> import numpy as np
    >>>
    >>> pwv = 15
    >>> temp = 8000
    >>>
    >>> i_band = (7000, 8500)
    >>> sample_rate = 1
    >>> wavelengths = np.arange(i_band[0], i_band[1], sample_rate)
    >>>
    >>> sed_with_atm = bb_atm.sed(temp, wavelengths, pwv)  # S(lambda) T(lambda)
    >>> intrinsic_sed = bb_atm.sed(temp, wavelengths, 0)  # S(lambda)

Trapezoidal integration of array like objects in Python can be performed using
the ``Numpy`` package. Using results from the spectrographic example we have:

.. code-block:: python
    :linenos:

    >>> numerator = np.trapz(sed_with_atm, i_band, sample_rate)
    >>> denominator = np.trapz(intrinsic_sed, i_band, sample_rate)
    >>>
    >>> photo_corr = np.divide(numerator, denominator)