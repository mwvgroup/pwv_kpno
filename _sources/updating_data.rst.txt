******************
Accessing PWV Data
******************

**pwv_kpno** relies on PWV measurements taken by the `SuomiNet project
<http://www.suominet.ucar.edu>`_. In order to model the PWV transmission
function for a given date, SuomiNet data for that date must be available on
your local machine. By default, each release of **pwv_kpno** contains all
necessary SuomiNet data from 2010 through the end of the previous year.

For convenience, functions are provided to check what data is available on the
local machine, and to download any newly published data. Users can also access
the local data as an `astropy` table.

Checking Available Data
=======================

Checking the years for which SuomiNet data is locally available can be achieved
using the `available_data` function. By default, version 0.10.0 of **pwv_kpno**
is distributed with all the necessary SuomiNet data from 2010 through 2017.

.. autofunction:: pwv_kpno.pwv_trans.available_data

Example:
--------

.. code-block:: python

    >>> pwv_kpno.available_data()

      [2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017]

Updating Data
=============

To download SuomiNet data to your local machine, use the `update_models`
function. By default only data that is not available on the local machine will
be downloaded.

.. autofunction:: pwv_kpno.pwv_trans.update_models

Example:
--------

By default, `update_models` will download any data that is not available on the
local machine. Version 0.11.0 already includes all data from years 2010 through
2017::

    >>> updated_years = pwv_kpno.update_models()
    >>> updated_years

      [2017, 2018]


If desired, **pwv_kpno** can be forced to (re)download SuomiNet data for a
specific year::

    >>> pwv_kpno.update_models(2010)

      [2010]

|

Measured PWV Data
=================

To retrieve an astropy table of SuomiNet data available on the local machine,
use the `measured_pwv` function. Results can be filtered independently by year,
month, day, and hour

.. autofunction:: pwv_kpno.pwv_trans.measured_pwv

Example:
--------

To retrieve all SuomiNet data available on the local machine as an `astropy`
table::

    >>> pwv_kpno.measured_pwv()

                 date             KITT    P014    SA46    SA48    AZAM
                 UTC               mm      mm      mm      mm      mm
      ------------------------- ------- ------- ------- ------- -------
      2010-01-01 00:15:00+00:00      --     3.6     4.2     4.7      --
      2010-01-01 00:45:00+00:00      --     3.7     4.0     4.7      --
      2010-01-01 01:14:00+00:00      --     3.7     3.4     3.6      --
                            ...     ...     ...     ...     ...     ...

Example:
--------

To retrieve SuomiNet data taken on November 14, 2016, specify the datetime as
keyword arguments. Note in the below example that there is no data available
from the SA48 receiver for this date::

    >>> pwv_kpno.measured_pwv(year=2016, month=11, day=14)

                 date             KITT    P014    SA46    SA48    AZAM
                 UTC               mm      mm      mm      mm      mm
      ------------------------- ------- ------- ------- ------- -------
      2016-11-14 00:15:00+00:00     4.7     6.9     9.8      --     8.4
      2016-11-14 00:45:00+00:00     4.3     6.7     9.9      --     8.0
      2016-11-14 01:14:00+00:00     3.9     6.7     9.7      --     8.0
                            ...     ...     ...     ...     ...     ...

If no SuomiNet data is available at all during the specified datetime, then the
returned table will be empty.

Modeled PWV Data
================

Using SuomiNet data, **pwv_kpno** creates a model for the PWV level at Kitt
Peak. This model is used exclusively when modeling the atmospheric absorption,
and is updated to reflect new measurements every tie the `update_models`
function is run. To retrieve this model as an astropy table, use the
`modeled_pwv` function

.. autofunction:: pwv_kpno.pwv_trans.modeled_pwv

Example:
--------

To retrieve the entire PWV model covering from 2010 onward::

    >>> pwv_kpno.modeled_pwv()

                 date                pwv
                 UTC                  mm
                object             float64
      ------------------------- --------------
      2010-01-01 00:15:00+00:00 0.898602350838
      2010-01-01 00:45:00+00:00 0.886046065367
      2010-01-01 01:14:00+00:00  0.62058536959
                            ...            ...


Example:
--------

To retrieve the modeled PWV level for November 14, 2016::

    >>> pwv_kpno.modeled_pwv(year=2016, month=11, day=14)

                   date                pwv
                   UTC                  mm
                  object             float64
        ------------------------- -------------
        2016-11-14 00:15:00+00:00 2.94364012734
        2016-11-14 00:45:00+00:00 2.85828459218
        2016-11-14 01:14:00+00:00           3.9
                              ...           ...
