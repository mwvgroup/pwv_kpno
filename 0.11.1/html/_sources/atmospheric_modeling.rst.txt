***********************
Modeling the Atmosphere
***********************

**pwv_kpno** provides models for the atmospheric transmission due to H\
:sub:`2`\ O at Kitt Peak National Observatory. These models can be retrieved
by providing either a datetime and airmass value or a PWV column density along
line of sight. Atmospheric modeling is available as part of the
``pwv_kpno.pwv_atm`` module.

Transmission for Datetime
=========================

Modeling the atmospheric transmission function for a given datetime requires
SuomiNet data to be available on the local machine. See the
:ref:`accessing_data:Updating Data` section for more details.

To find the atmospheric transmission for a given datetime, use the
``trans_for_date`` method.

.. autofunction:: pwv_kpno.pwv_atm.trans_for_date

Examples:
---------

For an airmass of 1.2, the transmission function at 2013-12-15 05:35:00 is
given by:

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

        wavelength   transmission
         Angstrom
      ------------- --------------
             7000.0 0.994835616916
      7001.00033344 0.990633715253
      7002.00066689 0.999799748012
                ...            ...

Transmission for PWV
====================

Instead of relying on SuomiNet measurements, users can also retrieve the
modeled transmission function by directly specifying a PWV column density. This
can be done using the ``trans_for_pwv`` method.

.. autofunction:: pwv_kpno.pwv_atm.trans_for_pwv

Examples:
---------

For a 13.5 mm PWV column density along line of sight, the transmission function
is given by:

.. code-block:: python
    :linenos:

    >>> from pwv_kpno import pwv_atm
    >>> pwv_atm.trans_for_pwv(13.5)

        wavelength   transmission
         Angstrom
      ------------- --------------
             7000.0 0.927538932462
      7001.00033344 0.872185668270
      7002.00066689 0.997095800639

