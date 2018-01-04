*****************
Updating PWV Data
*****************

**pwv_kpno** relies on PWV measurements taken by the SuomiNet project. In order
to model the PWV transmission function for a given date, SuomiNet data for that
date must be available on your local machine. By default, **pwv_kpno** contains
all necessary SuomiNet data from 2010 through the end of 2016.

Checking Available Data
=======================

Checking the years for which SuomiNet data is locally available can be achieved
using the `available_data` function. By default, version 0.10.0 of **pwv_kpno**
is distributed with all the necessary SuomiNet data from 2010 through 2016.

.. autofunction:: pwv_kpno.available_data

Example
-------

.. code-block:: python

    >>> pwv_kpno.available_data()

      [2010, 2011, 2012, 2013, 2014, 2015, 2016]

Updating Data
=============

To download SuomiNet data to your local machine, use the `update_models`
function. By default only data that is not available on the local machine will
be downloaded.

.. autofunction:: pwv_kpno.update_models

Example
-------

By default, `update_models` will download any data that is not available on the
local machine. Version 0.10.0 already includes all data from years 2010 through
2016::

    >>> updated_years = pwv_kpno.update_models()
    >>> updated_years

      [2017]


If desired, **pwv_kpno** can be forced to (re)download SuomiNet data for a
specific year::

    >>> pwv_kpno.update_models(2010)

      [2010]
