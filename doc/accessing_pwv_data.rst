******************
Accessing PWV Data
******************

This is what it means to access the "local data"

Measured PWV Data
=================

To retrieve an astropy table of SuomiNet available on the local machine,
use the `measured_pwv` function. Results can be filtered independently by year,
month, day, and hour

.. autofunction:: pwv_kpno.measured_pwv

Example
-------

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
returned table will be empty::

    >>> pwv_data = pwv_kpno.measured_pwv(year=2016, month=11, day=11, hour=1)
    >>> len(pwv_data)

        0

Modeled PWV Data
================

This package uses SuomiNet data to create a model for the PWV level at Kitt
Peak. To retrieve this model as an astropy table, use the `measured_pwv`
function

.. autofunction:: pwv_kpno.modeled_pwv

Example
-------

f::

    >>> modeled_pwv = pwv_kpno.modeled_pwv()
    >>> print(modeled_pwv)

                date             pwv
                UTC               mm
        -------------------  -------------
        2010-06-25 00:15:00  5.37705575203
        2010-06-25 00:45:00  5.51619053262
        2010-06-25 01:15:00  5.56017738737
                        ...            ...

Results can also be refined by year, month, day, and hour. For example,
model values for November 14, 2016 can be retrieved as follows::

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
means that for some datetimes the returned table will be empty::

    >>> pwv_data = pwv_kpno.measured_pwv(year=2016, month=11, day=11, hour=1)
    >>> len(pwv_data)

        0

