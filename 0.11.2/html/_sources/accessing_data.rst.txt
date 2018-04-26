******************
Accessing PWV Data
******************

In order to model the PWV absorption for a given date and time, SuomiNet data
for that date must be available on your local machine. By default, each release
of **pwv_kpno** contains all necessary SuomiNet data from 2010 through the end
of the previous year. For convenience, functions are provided to check what
data is available on the local machine, and to download any newly published
data. Users can also access the local data as an ``astropy`` table.

Access to PWV data is available as part of the ``pwv_kpno.pwv_atm`` module.

Checking For Available Data
===========================

To check what years of SuomiNet data are locally available, use the
``available_data`` function. By default, version 0.10.0 of **pwv_kpno** is
distributed with all the necessary SuomiNet data from 2010 through 2017.

.. autofunction:: pwv_kpno.pwv_atm.available_data

Examples:
---------

To check the years for which SuomiNet data is locally available, run the
following:

.. code-block:: python
    :linenos:

    >>> from pwv_kpno import pwv_atm
    >>> pwv_atm.available_data()

      [2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017]

Updating Data
=============

To download SuomiNet data to your local machine, use the ``update_models``
function. By default, this function will download all published data for any
years not currently present on the local machine. In addition, it will also
download data for the most recent year for which data is locally available.
This method ensures there are no years with incomplete measurements in the
locally available data.

.. autofunction:: pwv_kpno.pwv_atm.update_models

Examples:
---------

To ensure that the PWV data for **pwv_kpno** is up to date run:

.. code-block:: python
    :linenos:

    >>> from pwv_kpno import pwv_atm
    >>> pwv_atm.update_models()

      [2017, 2018]

If desired, **pwv_kpno** can be forced to (re)download SuomiNet data for a
specific year:

.. code-block:: python
    :linenos:

    >>> pwv_atm.update_models(2010)

      [2010]


Measured PWV Data
=================

The ``measured_pwv`` function returns an astropy table containing any SuomiNet
data available on the local machine. Results can be filtered independently by
year, month, day, and hour

.. autofunction:: pwv_kpno.pwv_atm.measured_pwv

Examples:
---------

To retrieve all SuomiNet data available on the local machine as an ``astropy``
table:

.. code-block:: python
    :linenos:

    >>> from pwv_kpno import pwv_atm
    >>> pwv_atm.measured_pwv()

                 date             KITT    P014    SA46    SA48    AZAM
                 UTC               mm      mm      mm      mm      mm
      ------------------------- ------- ------- ------- ------- -------
      2010-01-01 00:15:00+00:00      --     3.6     4.2     4.7      --
      2010-01-01 00:45:00+00:00      --     3.7     4.0     4.7      --
      2010-01-01 01:14:00+00:00      --     3.7     3.4     3.6      --
                            ...     ...     ...     ...     ...     ...

To retrieve SuomiNet data taken on November 14, 2016, specify the datetime as
keyword arguments. Note in the below example that there is no data available
from the SA48 receiver for this date:

.. code-block:: python
    :linenos:

    >>> pwv_atm.measured_pwv(year=2016, month=11, day=14)

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
and is updated to reflect new measurements every time the ``update_models``
function is run. To retrieve this model as an astropy table, use the
``modeled_pwv`` function

.. autofunction:: pwv_kpno.pwv_atm.modeled_pwv

Examples:
---------

To retrieve the entire PWV model from 2010 onward:

.. code-block:: python
    :linenos:

    >>> from pwv_kpno import pwv_atm
    >>> pwv_atm.modeled_pwv()

                 date                pwv
                 UTC                  mm
                object             float64
      ------------------------- --------------
      2010-01-01 00:15:00+00:00 1.021057909034
      2010-01-01 00:45:00+00:00 1.007850543589
      2010-01-01 01:14:00+00:00 0.746607564877
                            ...            ...

To retrieve the modeled PWV level over the course of November 14th, 2016:

.. code-block:: python
    :linenos:

    >>> pwv_atm.modeled_pwv(year=2016, month=11, day=14)

                   date             pwv
                   UTC               mm
                  object          float64
        ------------------------- -------
        2016-11-14 00:15:00+00:00     4.7
        2016-11-14 00:45:00+00:00     4.3
        2016-11-14 01:15:00+00:00     3.9
                              ...     ...

PWV For a Given Date
====================

In order to determine the PWV column density for a given datetime, users should
interpolate from the modeled PWV table outlined above. For convenience, this
can be done automatically using the ``pwv_date`` function.

.. autofunction:: pwv_kpno.pwv_atm.pwv_date

Examples:
---------

To retrieve the modeled PWV level for November 14, 2016 at 11:00 AM:

.. code-block:: python
    :linenos:

   >>> from datetime import datetime
   >>> from pwv_kpno import pwv_atm
   >>> import pytz
   >>>
   >>> date = datetime(2016, 11, 14, 11, 00, tzinfo=pytz.utc)
   >>> pwv = pwv_atm.pwv_date(date)

