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

Updating Data
=============

Version 0.10.0 of this package is distributed with all the necessary SuomiNet
data from 2010 through 2016. To download any SuomiNet data published after
2016 use the `update_models` function:

.. autofunction:: pwv_kpno.update_models

Example
-------

The `update_models` function will return a list of years for which data was
downloaded::

    >>> # Download all available data from 2017 onward
    >>> updated_years = pwv_kpno.update_models()
    >>> updated_years

    [2017]

Data can also be used to update data for a specific year::

    >>> pwv_kpno.update_models(2010)

    [2010]
