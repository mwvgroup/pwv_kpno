********
Examples
********

Updating local SuomiNet data
============================

Version 0.10.0 of this package is distributed with all the necessary SuomiNet
data from 2010 through 2016. To download any SuomiNet data published after 2016
use the update_models function::

    >>> # Download all available data from 2017 onward
    >>> updated_years = pwv_kpno.update_models()
    >>> updated_years

      [2017]

The update_models function will return a list of years for which data was
downloaded. Data can also be used to update data for a specific year::

    >>> pwv_kpno.update_models(2010)

      [2010]

Retrieving local SuomiNet data
==============================

To retrieve an astropy table of SuomiNet available on the local machine, use
the measured_pwv function::

    >>> measured_data = pwv_kpno.measured_pwv()
    >>> print(measured_data)

              date         KITT  P014  SA46  SA48  AZAM
              UTC           mm    mm    mm    mm    mm
      -------------------  ----  ----  ----  ----  ----
      2010-06-25 00:15:00    --    --  23.4  15.2    --
      2010-06-25 00:45:00    --    --  23.9  15.6    --
      2010-06-25 01:15:00    --    --  22.6  17.1    --
                      ...   ...   ...   ...   ...   ...

Results can also be refined by year, month, day, and hour. For example, data
taken on November 14, 2016 can be retrieved as follows::

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

Retrieving the PWV model
========================

This package uses SuomiNet data to create a model for the PWV level at Kitt
Peak. To retrieve this model as an astropy table, use the measured_pwv
function::

    >>> modeled_pwv = pwv_kpno.modeled_pwv()
    >>> print(modeled_pwv)

              date             pwv
              UTC               mm
      -------------------  -------------
      2010-06-25 00:15:00  5.37705575203
      2010-06-25 00:45:00  5.51619053262
      2010-06-25 01:15:00  5.56017738737
                      ...  ...

Results can also be refined by year, month, day, and hour. For example, model
values for November 14, 2016 can be retrieved as follows:

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

Generating an atmospheric transmission function
===============================================

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
