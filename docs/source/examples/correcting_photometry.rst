Correcting Photometric Observations
===================================

For an atmospheric transmission :math:`T(\lambda)`, the photometric correction
for an object with an intrinsic spectral energy distribution :math:`S(\lambda)`
is given by

.. math::
   C = \frac{\int S(\lambda) \cdot T(\lambda) \, d\lambda}
             {\int S(\lambda) \, d\lambda}

where the integration bounds are defined by the wavelength range of the
photometric bandpass. In practice, an SED of the desired object may not be
available. In such a case spectral templates should be used instead.

For demonstration purposes, we consider an observation of a black body.
To simulate a black body SED we use the ``astropy`` package:

.. code-block:: python
   :linenos:

   import numpy as np
   from astropy.modeling import models
   from astropy import units as u

   bb = models.BlackBody(temperature=5000*u.K)

   wavelengths = np.arange(3_000, 12_000)
   flux_without_atm = bb(wavelengths * u.AA)

Note that product in the numerator :math:`S(\lambda) \cdot T(\lambda)`
represents the SED under the influence of atmospheric effects.
For demonstration purposes, we assume the photometric observation was taken
through 5 mm of PWV.
The transmission function of the atmosphere can be found as:


.. code-block:: python
   :linenos:

   from pwv_kpno.defaults import v1_transmission

   atm_transmission = v1_transmission(5, wavelengths)

Finally, the integral above can be evaluated using your favorite integration
technique. For simplicity, we here use a trapezoidal integration. Evaluating
the integral requires you specify a set of integration bounds. As an example,
we consider a photometric observation taken in the *i* band, which ranges
(approximately) from 7,000 to 8,500 :math:`\unicode{x212B}`.

.. code-block:: python
   :linenos:

   i_band = (7000, 8500)
   numerator = np.trapz(flux_without_atm * atm_transmission, i_band, dx=1)
   denominator = np.trapz(flux_without_atm, i_band, dx=1)

   photo_corr = np.divide(numerator, denominator)
