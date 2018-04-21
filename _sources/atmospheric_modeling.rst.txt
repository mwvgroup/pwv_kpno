***********************
Modeling the Atmosphere
***********************

**pwv_kpno** provides models for the atmospheric transmission due to H\
:sub:`2`\ O at Kitt Peak National Observatory. These models can be retrieved
by providing either a datetime and airmass value or a precipitable water vapor
concentration along line of sight.

Atmospheric modeling is available as part of the ``pwv_kpno.pwv_atm`` module.

Transmission from Datetime
==========================

Using measurements from the `SuomiNet <http://www.suominet.ucar.edu>`_ project,
**pwv_kpno** is able to determine the PWV concentration along line of sight
for a provided datetime and airmass. Note that this requires SuomiNet data for
the desired datetime to be available on the local machine (See `updating data
<updating_data.html>`_ for more details).

To find the atmospheric transmission, use the ``trans_from_date`` method.

.. autofunction:: pwv_kpno.pwv_atm.trans_from_date

Example:
--------

For an airmass of 1.2, the transmission function at 2013-12-15 05:35:00 is
given by::

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
    >>> pwv_trans.trans_from_date(date=obsv_date, airmass=1.2)

      wavelength   transmission
       Angstrom         %
      ------------- --------------
             7000.0 0.995667371031
      7001.00033344 0.992141802334
      7002.00066689 0.999832009999
                ...            ...

Transmission from PWV
=====================

Instead of relying on SuomiNet measurements, users can also retrieve the
modeled transmission function by directly specifying a PWV concentration. This
can be done using the ``transmission_pwv`` method.

.. autofunction:: pwv_kpno.pwv_atm.trans_from_pwv

Example:
--------
.. code-block:: python

    >>> pwv_trans.transmission_pwv(13.5)

      wavelength   transmission
       Angstrom         %
      ------------- --------------
             7000.0 0.927538932462
      7001.00033344  0.87218566827
      7002.00066689 0.997095800639
