*******************
Accessing Site Data
*******************

In order to model the PWV absorption for a given date and time, GPS
measurements for that date must be available on your local machine. Accessing
and downloading new GPS data is handled by the ``pwv_atm`` module.

Checking For Available Data
===========================

To check what years of data have been downloaded from the SuomiNet server, use the
``downloaded_years`` function.

.. autofunction:: pwv_kpno.pwv_atm.downloaded_years

By default, each release of **pwv_kpno** contains all necessary SuomiNet data
from 2010 through the end of the previous year.

.. code-block:: python
    :linenos:

    >>> from pwv_kpno import pwv_atm
    >>> pwv_atm.downloaded_years()

      [2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017]

Updating Data
=============

To download new data to your local machine, use the ``update_models``
function. This function will download new data from the SuomiNet web server,
and use that data to update the modeled precipitable water vapor for the
current site being modeled.

.. autofunction:: pwv_kpno.pwv_atm.update_models

To ensure that the PWV data for **pwv_kpno** is up to date run:

.. code-block:: python
    :linenos:

    >>> from pwv_kpno import pwv_atm
    >>>
    >>> # Download any new / missing data
    >>> pwv_atm.update_models()

      [2017, 2018]

    >>> # Re-download a specific year
    >>> pwv_atm.update_models(2010)

      [2010]

.. note:: If **pwv_kpno** has been set to model a custom site and no data has
    already been downloaded from SuomiNet, this function will default to download any
    available data from 2010 onward.


Measured PWV Data
=================

Any locally available PWV data for the current site being modeled can be
accessed using the ``measured_pwv`` function.

.. autofunction:: pwv_kpno.pwv_atm.measured_pwv


To retrieve all SuomiNet data available on the local machine:

.. code-block:: python
    :linenos:

    >>> from pwv_kpno import pwv_atm
    >>> pwv_atm.measured_pwv()

               date       KITT KITT_err P014 P014_err SA46 SA46_err SA48 ...
               UTC         mm     mm     mm     mm     mm     mm     mm  ...
      ------------------- ---- -------- ---- -------- ---- -------- ---- ...
      2010-01-01 00:15:00   --       --  3.6    0.125  4.2    0.125  4.7 ...
      2010-01-01 00:45:00   --       --  3.7    0.125  4.0    0.125  4.7 ...
      2010-01-01 01:15:00   --       --  3.7    0.025  3.4    0.125  3.6 ...
                   ...     ...      ...  ...      ...  ...      ...  ... ...

To retrieve SuomiNet data taken on a specific date or time:

.. code-block:: python
    :linenos:

    >>> pwv_atm.measured_pwv(year=2016, month=11, day=14)

               date       KITT KITT_err P014 P014_err SA46 SA46_err SA48 ...
               UTC         mm     mm     mm     mm     mm     mm     mm  ...
      ------------------- ---- -------- ---- -------- ---- -------- ---- ...
      2016-11-14 00:15:00  4.7    1.025  6.9    0.525  9.8    0.725   -- ...
      2016-11-14 00:45:00  4.3    1.025  6.7    0.425  9.9    0.525   -- ...
      2016-11-14 01:15:00  3.9    0.925  6.7    0.425  9.7    0.525   -- ...
                   ...     ...      ...  ...      ...  ...      ...  ... ...

.. Note:: If no SuomiNet data is available at all during the specified
    datetime, then the returned table will be empty.

Modeled PWV Data
================

To retrieve the modeled PWV level for the site's primary GPS receiver, use the
``modeled_pwv`` function.

.. autofunction:: pwv_kpno.pwv_atm.modeled_pwv

To retrieve the entire PWV model for all available dates:

.. code-block:: python

    >>> from pwv_kpno import pwv_atm
    >>> pwv_atm.modeled_pwv()

               date       pwv   pwv_err
               UTC         mm      mm
      ------------------- ----- -------
      2010-01-01 00:15:00 1.55    1.227
      2010-01-01 00:45:00 1.532   1.225
      2010-01-01 01:15:00 1.178   1.175
                      ...   ...     ...

To retrieve the modeled PWV level for a specific date or time:

.. code-block:: python

    >>> pwv_atm.modeled_pwv(year=2016, month=11, day=14)

               date       pwv pwv_err
               UTC         mm    mm
      ------------------- --- -------
      2016-11-14 00:15:00 4.7   1.025
      2016-11-14 00:45:00 4.3   1.025
      2016-11-14 01:15:00 3.9   0.925
                      ... ...    ...

PWV For a Given Date
====================

For convenience, users can interpolate from the modeled PWV concentration at
Kitt Peak using the ``pwv_date`` function.

.. autofunction:: pwv_kpno.pwv_atm.pwv_date

To retrieve the modeled PWV level for November 14, 2016 at 11:06 AM:

.. code-block:: python
    :linenos:

    >>> from datetime import datetime
    >>> from pwv_kpno import pwv_atm
    >>> import pytz
    >>>
    >>> date = datetime(2016, 11, 14, 11, 6, tzinfo=pytz.utc)
    >>> pwv, pwv_err = pwv_atm.pwv_date(date)

Additional Meteorological Data
==============================

The full set of downloaded SuomiNet measurements for a particular GPS receiver
can be found using the ``get_all_receiver_data`` function. The returned table
includes the PWV measurements for a given receiver, plus measurements of the
GPS zenith delay, surface pressure, surface temperature, and relative humidity.

.. autofunction:: pwv_kpno.pwv_atm.get_all_receiver_data

