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

This package uses SuomiNet data to create a model for the PWV level at Kitt
Peak. To retrieve this model as an astropy table, use the `measured_pwv`
function

.. autofunction:: pwv_kpno.modeled_pwv

Example
-------

To retrieve the entire PWV model covering from 2010 onward::

    >>> pwv_kpno.modeled_pwv()

                 date                pwv
                 UTC                  mm
                object             float64
      ------------------------- --------------
      2010-01-01 00:15:00+00:00  1.06488584353
      2010-01-01 00:45:00+00:00  1.05127933812
      2010-01-01 01:14:00+00:00 0.782751028328
                            ...            ...


To retrieve the modeled PWV level for November 14, 2016::

    >>> pwv_kpno.modeled_pwv(year=2016, month=11, day=14)

                date         PWV
                UTC           mm
        -------------------  ---
        2016-11-14 00:15:00  4.7
        2016-11-14 00:45:00  4.3
        2016-11-14 01:15:00  3.9
                        ...  ...
