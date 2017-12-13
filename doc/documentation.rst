*************
Documentation
*************

See below for documentation and examples on the individual methods included
with **pwv_kpno**. An example demonstrating how to use the package to correct
real world observations is under development.

.. toctree::
    :maxdepth: 4

    documentation

Retrieving Atmospheric Models
=============================

Users can retrieve the modeled atmospheric transmission for a given datetime
using the `transmission` function.

.. autofunction:: pwv_kpno.transmission

Example
-------

To return a model for the atmospheric transmission function for a specific
datetime, first create a datetime object. That object is then passed to the
transmission function along with an airmass value. For example, for an airmass
of 1.2, the transmission function at 2013-12-15 05:35:00 is given by::

    >>> from datetime import datetime
    >>> import pytz
    >>>
    >>> obsv_date = datetime(year=2013, month=12, day=15, hour=5, minute=35,
    >>>                      tzinfo=pytz.utc)
    >>>
    >>> trans = pwv_kpno.transmission(date=obsv_date, airmass=1.2)
    >>> print(trans)


      wavelength   transmission
      ------------- --------------
           7000.0 0.996573011501
      7001.00033344 0.993783855758
      7002.00066689 0.999867137883
                ... ...


Checking and Updating PWV Data
==============================

**pwv_kpno** relies on PWV measurements taken by the SuomiNet project. In order
to model the PWV transmission function for a given date, SuomiNet data for that
date must be available on the host machine. By default, **pwv_kpno** contains
all necessary SuomiNet data from 2010 through the end of 2016.

Checking the years for which SuomiNet data is locally available can be achieved
using the `available_data` function.

.. autofunction:: pwv_kpno.available_data

Example
-------

By default, `update_models` will download any data that is not available on the
local machine::

    >>> # Download all available data from 2017 onward
    >>> updated_years = pwv_kpno.update_models()
    >>> updated_years

      [2017]


If desired, **pwv_kpno** can be forced to (re)download SuomiNet data for a
specific year::

    >>> pwv_kpno.update_models(2010)

      [2010]

.. autofunction:: pwv_kpno.update_models

Accessing Local Data
====================

This is what it means to access the "local data"

.. autofunction:: pwv_kpno.measured_pwv
.. autofunction:: pwv_kpno.modeled_pwv