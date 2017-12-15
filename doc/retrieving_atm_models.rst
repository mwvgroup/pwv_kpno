*****************************
Retrieving Atmospheric Models
*****************************

**pwv_kpno** provides models for the atmospheric transmission due to H\
:sub:`2`\ O at Kitt Peak National Observatory. These models can be retrieved
by providing either a datetime and airmass value or a precipitable water vapor
concentration along line of sight.

Transmission from Datetime
==========================

Using measurements from the `SuomiNet project <http://www.suominet.ucar.edu>`_,
**pwv_kpno** is able to determine the PWV concentration along line of sight
for a provided datetime and airmass. To find the atmospheric transmission, use
the `transmission` method.

Note that this method requires SuomiNet data for the desired datetime to be
available on the local machine. **pwv_kpno** includes all necessary PWV data
for years 2010 through 2016. If you require additional data on your machine,
please see the `updating data <updating_data.html#updating-data>`_ section. For
more information on how **pwv_kpno** relates PWV concentration and airmass, see
the `Science Notes <science_notes.html>`_.

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
    >>> print(trans)


      wavelength   transmission
      ------------- --------------
             7000.0 0.996573011501
      7001.00033344 0.993783855758
      7002.00066689 0.999867137883
                ...            ...

Transmission from PWV
=====================

Instead of relying on SuomiNet measurements, users can also retrieve the
modeled transmission function by directly specifying a PWV concentration. This
can be done using the `transmission_pwv` method.

.. autofunction:: pwv_kpno.transmission_pwv

Example
-------


