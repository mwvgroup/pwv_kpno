***********************
Modeling the Atmosphere
***********************
The ``pwv_atm`` module provides models for the atmospheric transmission due to
precipitable water vapor. These models can be retrieved by providing either a
datetime and airmass value or a PWV column density along the line of sight.

Transmission for Datetime
=========================

Modeling the atmospheric transmission function for a given datetime requires
SuomiNet data to be available on the local machine. See the
:ref:`accessing_data:Updating Data` section for more details.

To determine the atmospheric transmission for a given datetime, use the
``trans_for_date`` function.

.. autofunction:: pwv_kpno.pwv_atm.trans_for_date

For example, given an airmass of 1.2, the transmission function at 2013-12-15
05:35:00 UTC is given by:

.. code-block:: python
    :linenos:

    >>> from datetime import datetime
    >>> from pwv_kpno import pwv_atm
    >>> import pytz
    >>>
    >>> obsv_date = datetime(year=2013,
    >>>                      month=12,
    >>>                      day=15,
    >>>                      hour=5,
    >>>                      minute=35,
    >>>                      tzinfo=pytz.utc)
    >>>
    >>> pwv_atm.trans_for_date(date=obsv_date, airmass=1.2)

      wavelength  transmission  transmission_err
       Angstrom
      ---------- -------------- ----------------
         3000.00 0.999999991637 1.3506621821e-08
         3000.05 0.999999991637 1.3507332141e-08
         3000.10 0.999999991637 1.3507963636e-08
             ...            ...              ...


Transmission for PWV
====================

Instead of relying on SuomiNet measurements, users can also retrieve the
modeled transmission function by directly specifying a PWV column density. This
can be done using the ``trans_for_pwv`` method.

.. autofunction:: pwv_kpno.pwv_atm.trans_for_pwv

For a 13.5 mm PWV column density along the line of sight, the transmission function
is given by:

.. code-block:: python
    :linenos:

    >>> from pwv_kpno import pwv_atm
    >>> pwv_atm.trans_for_pwv(13.5)

      wavelength  transmission
       Angstrom
      ---------- --------------
         3000.00 0.999999922781
         3000.05 0.999999922777
         3000.10 0.999999922774
             ...            ...

Note that the ``trans_for_pwv`` method will only return the error in the modeled
transmission if the ``pwv_err`` argument is specified:

.. code-block:: python
    :linenos:

    >>> from pwv_kpno import pwv_atm
    >>> pwv_atm.trans_for_pwv(13.5, 1.5)

      wavelength  transmission  transmission_err
       Angstrom
      ---------- -------------- ----------------
         3000.00 0.999999922781 1.7159738408e-08
         3000.05 0.999999922777 1.7160641019e-08
         3000.10 0.999999922774 1.7161443266e-08
             ...            ...              ...

Binning the Transmission
========================

Both the ``trans_for_date`` and the ``trans_for_pwv`` functions provide support
for binning the returned transmission function via the ``bins`` argument. The
returned transmission in each bin is calculated as:

.. math::
   T = \frac{1}{\lambda_1 - \lambda_0} \int_{\lambda_0}^{\lambda_1} T(\lambda) \, d\lambda

If the ``bins`` argument is an integer, it defines the number of equal-width bins
to use. If ``bins`` is a sequence, it defines the bin edges, including the
rightmost edge, allowing for non-uniform bin widths. Wavelengths in the
returned transmission function mark the leftmost edge of each bin. For
example:

.. code-block:: python
    :linenos:

    >>> import numpy as np
    >>> from pwv_kpno import pwv_atm

    >>> bins = np.arange(3000, 12000, 10)  # Bins with 1 Angstrom resolution
    >>> pwv_atm.trans_for_pwv(13.5, bins=bins)

      wavelength  transmission
       Angstrom
      ---------- --------------
          3000.0 0.999999922381
          3010.0 0.999999921544
          3020.0 0.999999920685
             ...            ...
