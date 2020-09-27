**************************************
Correcting Spectrographic Observations
**************************************

.. Although **pwv_kpno** is primarily designed for correcting photometric
observations, it can also be used to correct spectra. However, it is
strongly recommended to read the
`Validation section <../../validation/html/transmission_function.html#comparison-to-observations>`_
first.

Correcting observed spectra for PWV effects is generally achieved in four steps:

#. Use **pwv_kpno** to determine the PWV transmission function corresponding to a given observation
#. Interpolate the transmission function to match the observed wavelengths
#. If desired, use a Gaussian kernel to smooth the interpolated transmission function
#. Divide the observed flux by the modeled transmission

It is important to note that the atmospheric models used by **pwv_kpno** are
may be at a higher wavelength resolution than the observed spectra. This means
that the modeled transmission function must first be binned to a lower
resolution before interpolating to the observed wavelengths. Fortunately,
**pwv_kpno** makes this process easy.

For demonstration purposes, assume you wish to correct an observation that was
taken through an airmass of 1.5 on December 15, 2013, at 05:35:00 UTC.
The binned transmission function corresponding to this observation is given by:

.. code-block:: python
    :linenos:

    >>> import numpy as np
    >>> from pwv_kpno import pwv_atm
    >>>
    >>> # Meta-data about the observation to be corrected
    >>> bin_resolution = 16
    >>> obsv_date = datetime(year=2013,
    >>>                      month=12,
    >>>                      day=15,
    >>>                      hour=5,
    >>>                      minute=35,
    >>>                      tzinfo=pytz.utc)
    >>>
    >>> # Determine the binned transmission function
    >>> bins = np.arange(3000, 12000, bin_resolution)
    >>> transmission = pwv_atm.trans_for_date(obsv_date, 1.5, bins)

We then interpolate the binned transmission for the observed wavelengths and
use the ``scipy`` package to smooth the transmission function with a Gaussian
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
