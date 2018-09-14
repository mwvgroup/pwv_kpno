***********************
Correcting Observations
***********************

Spectrographic Observations
===========================

Correcting observed spectra for PWV effects is achieved in four steps:

#. Use **pwv_kpno** to determine the PWV transmission function corresponding to a given observation
#. Interpolate the transmission function to match the observed wavelengths
#. If desired, use a gaussian kernel to smooth the interpolated transmission function
#. Divide the observed flux by the modeled transmission

It is important to note that the atmospheric models used by **pwv_kpno** are
may be at a higher wavelength resolution than the observed spectra. This means
that the modeled transmission function must first be binned to a lower
resolution before interpolating to the observed wavelengths. Fortunately,
**pwv_kpno** makes this process easy.

For demonstration purposes, assume you wish to correct an observation that was
taken through an airmass of 1.5 on December 15, 2013 at 05:35:00 UTC.
Furthermore, assume that this observed spectra has a wavelength resolution of
16 :math:`\unicode{x212B}`. The binned transmission function corresponding to
this observation is given by:

.. code-block:: python
    :linenos:

    >>> import numpy as np
    >>> from pwv_kpno import pwv_atm
    >>>
    >>> # Meta-data about the observation to be corrected
    >>> spectral_resolution = 16
    >>> obsv_date = datetime(year=2013,
    >>>                      month=12,
    >>>                      day=15,
    >>>                      hour=5,
    >>>                      minute=35,
    >>>                      tzinfo=pytz.utc)
    >>>
    >>> # Determine the binned transmission function
    >>> bins = np.arange(3000, 12000, spectral_resolution)
    >>> transmission = pwv_atm.trans_for_date(obsv_date, 1.5, bins)

We then interpolate the binned transmission for the observed wavelengths and
use the ``scipy`` package to smooth the transmission function with a gaussian
kernel. Here we assume the wavelengths are stored in the array
``observed_wavelength_array``.

.. code-block:: python
    :linenos:

    >>> # Interpolate the transmission function to match observed wavelengths
    >>> interped_transmission = np.interp(observed_wavelength_array,
    >>>                                   transmission['wavelength'],
    >>>                                   transmission['transmission'])
    >>>
    >>> # Smooth the modeled transmission function
    >>> standard_deviation = 2
    >>> gaussian_transmission = gaussian_filter(interp_transmission,
    >>>                                         standard_deviation)

Finally, the corrected spectrum can then be found by dividing the observed flux
by the transmission on a wavelength by wavelength basis. Assuming the
uncorrected flux values are stored in an array called ``observed_flux_array``,
this is programmatically equivalent to:

.. code-block:: python
    :linenos:

    >>> corrected_spec = np.divide(observed_flux_array, gaussian_transmission)


Photometric Observations
========================

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