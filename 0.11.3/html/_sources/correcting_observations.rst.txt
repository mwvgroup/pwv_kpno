***********************
Correcting Observations
***********************
.. This will be uncommented once the jupyter notebook tutorial is completed

    .. only:: builder_html

        **Note:** The following tutorial is available for download as a
        `Jupyter Notebook <_static/pwv_kpno_demo.ipynb>`_

Examples are provided on how to correct astronomical observations for
atmospheric effects. For demonstration purposes, the following examples
exclusively consider correcting observations of a black body.

Spectrographic Observations
===========================

In order to correct spectrographic observations for atmospheric effects,
observed spectra are divided by the atmospheric transmission function. As
an example, consider the spectral energy distribution (SED) of a black body
under the effects of atmospheric absorption. For a temperature of 8,000 K, and
a PWV level of 15 mm, this can be found as:

.. code-block:: python
    :linenos:

    >>> from pwv_kpno import blackbody_with_atm as bb_atm
    >>> import numpy as np
    >>>
    >>> temp = 8000
    >>> wavelengths = np.arange(7000, 1000, 100)
    >>> pwv = 15
    >>>
    >>> sed = bb_atm.sed(temp, wavelengths, pwv)
    >>> print(sed)

      [67943236.6960908, 70958962.4114214, ...,
       30913697.9848318, 29947238.7968099]

Since we know the PWV level used to generate this spectra, we can determine the
corresponding transmission function using the ``trans_for_pwv`` function
(although in a real world setting the ``trans_for_date`` function may be more
appropriate).

.. code-block:: python
    :linenos:

    >>> from pwv_kpno import pwv_atm
    >>>
    >>> modeled_trans = pwv_atm.trans_for_pwv(15)
    >>> print(modeled_trans)

              wavelength        transmission
               Angstrom
          ------------------ ------------------
                      7000.0 0.9198165020431311
           7001.000333444482 0.8590254136327501
           7002.000666888963 0.9967736288238565
                         ...                ...

In order to divide these two results, the SED at and the transmission function
must be known for the same wavelength values. Since the SED is a well
behaved function, we interpolate the SED to match the wavelength sampling of
the transmission function. In general the transmission function not a smooth
function, which can cause problems when interpolating.

Using the ``numpy`` package, we interpolate as follows:

.. code-block:: python
    :linenos:

    >>> sampled_sed = np.interp(modeled_trans["wavelength"],
    >>>                         wavelengths,
    >>>                         sed)

The corrected spectrum can then be found by dividing the observed flux
by the transmission on a wavelength by wavelength basis.

.. code-block:: python
    :linenos:

    >>> corrected_spec = np.divide(sampled_sed, modeled_trans["transmission"])


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

Note that product in the numerator :math:`S(\lambda) \cdot T(\lambda)`
represents the SED under the influence of atmospheric effects. For a
photometric observation taken in the *i* band (7,000 to 8,500
:math:`\unicode{x212B}`), the integration arguments can be found as:

.. code-block:: python
    :linenos:

    >>> from pwv_kpno import blackbody_with_atm as bb_atm
    >>> import numpy as np
    >>>
    >>> pwv = 15
    >>> temp = 8000
    >>>
    >>> i_band = (7000, 8500)
    >>> sample_rate = 100
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

