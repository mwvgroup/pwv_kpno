***********************
Modeling the Atmosphere
***********************

**pwv_kpno** provides models for the atmospheric transmission due to H\
:sub:`2`\ O at Kitt Peak National Observatory. These models can be retrieved
by providing either a datetime and airmass value or a precipitable water vapor
concentration along line of sight.

Transmission from Datetime
==========================

Using measurements from the `SuomiNet <http://www.suominet.ucar.edu>`_ project,
**pwv_kpno** is able to determine the PWV concentration along line of sight
for a provided datetime and airmass. Note that this requires SuomiNet data for
the desired datetime to be available on the local machine. By default,
**pwv_kpno** includes all necessary PWV data for years 2010 through 2016. To
find the atmospheric transmission, use the `transmission` method.

If you require additional data on your machine, please see the `updating data
<updating_data.html#updating-data>`_ section.

.. For more information on how **pwv_kpno** relates PWV concentration and airmass,
.. see the `Science Notes <science_notes.html>`_.

.. autofunction:: pwv_kpno.transmission

Example
-------

For an airmass of 1.2, the transmission function at 2013-12-15 05:35:00 is
given by::

    >>> from datetime import datetime
    >>> import pytz
    >>>
    >>> obsv_date = datetime(year=2013,
    >>>                      month=12,
    >>>                      day=15,
    >>>                      hour=5,
    >>>                      minute=35,
    >>>                      tzinfo=pytz.utc)
    >>>
    >>> trans = pwv_kpno.transmission(date=obsv_date, airmass=1.2)
    >>> trans

      wavelength   transmission
       Angstrom         %
      ------------- --------------
             7000.0 0.994565196207
      7001.00033344  0.99014340451
      7002.00066689 0.999789258963
                ...            ...

Transmission from PWV
=====================

Instead of relying on SuomiNet measurements, users can also retrieve the
modeled transmission function by directly specifying a PWV concentration. This
can be done using the `transmission_pwv` method.

.. autofunction:: pwv_kpno.transmission_pwv

Example
-------
.. code-block:: python

    >>> pwv_kpno.transmission_pwv(13.5)

      wavelength   transmission
       Angstrom         %
      ------------- --------------
             7000.0 0.927538932462
      7001.00033344 0.872185668270
      7002.00066689 0.997095800639
