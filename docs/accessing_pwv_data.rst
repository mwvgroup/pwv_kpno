******************
Accessing PWV Data
******************

Todo: Add document description

Measured PWV Data
=================

To retrieve an astropy table of SuomiNet available on the local machine,
use the `measured_pwv` function. Results can be filtered independently by year,
month, day, and hour

.. autofunction:: pwv_kpno.measured_pwv

Example
-------

To retrieve all SuomiNet data available on the local machine as an astropy
table::

    >>> pwv_kpno.measured_pwv()


To retrieve SuomiNet data taken on November 14, 2016::

    >>> pwv_kpno.measured_pwv(year=2016, month=11, day=14)

                date        KITT P014 SA46 SA48 AZAM
                UTC          mm   mm   mm   mm   mm
        ------------------- ---- ---- ---- ---- ----
        2016-11-14 00:15:00  4.7  6.7 10.4   --  7.9
        2016-11-14 00:45:00  4.3  6.5 10.3   --  7.5
        2016-11-14 01:15:00  3.9  6.5 10.1   --  8.0
                        ...  ...  ...  ...  ...  ...

Note that if no SuomiNet data is available during the specified datetime, the
returned table will be empty.

Modeled PWV Data
================

This package uses SuomiNet data to create a model for the PWV level at Kitt
Peak. To retrieve this model as an astropy table, use the `measured_pwv`
function

.. autofunction:: pwv_kpno.modeled_pwv

Example
-------

To retrieve the entire PWV model covering from 2010 onward::

    >>> modeled_pwv = pwv_kpno.modeled_pwv()
    >>> print(modeled_pwv)

                date             pwv
                UTC               mm
        -------------------  -------------
        2010-06-25 00:15:00  5.37705575203
        2010-06-25 00:45:00  5.51619053262
        2010-06-25 01:15:00  5.56017738737
                        ...            ...


To retrieve the modeled PWV level for November 14, 2016::

    >>> modeled_pwv = pwv_kpno.modeled_pwv(year=2016, month=11, day=14)
    >>> print(modeled_pwv)

                date         PWV
                UTC           mm
        -------------------  ---
        2016-11-14 00:15:00  4.7
        2016-11-14 00:45:00  4.3
        2016-11-14 01:15:00  3.9
                        ...  ...

Note that the PWV model does not have a data point for every datetime. This
means that for some datetimes the returned table may be empty.