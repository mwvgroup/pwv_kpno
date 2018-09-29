****************
Package Overview
****************

What is pwv_kpno?
=================

**pwv_kpno** is a science focused Python package that provides access to
models for the atmospheric absorption due to H2O. The strength of H2O
absorption features have been observed to correlate strongly with measurements
of localized PWV column density. By measuring the delay of dual band GPS
signals traveling through the atmosphere, it is possible to determine the PWV
column density along line of sight. **pwv_kpno** leverages this principle to
provide atmospheric models for user definable sites as a function of date,
time, and airmass.

The SuomiNet project is a meteorological initiative that provides semi-hourly
PWV measurements for hundreds of GPS receivers world wide. The **pwv_kpno**
package uses published SuomiNet data in conjunction with MODTRAN models to
determine the modeled, time dependent atmospheric transmission.
By default this package provides access to the modeled transmission
function at Kitt Peak National Observatory. However, this package is designed
to be easily extensible to other locations within the SuomiNet Network.
Additionally, **pwv_kpno** provides access to atmospheric models as a function
of PWV, which is independent of geographical location. Atmospheric models
are provided from 3,000 to 12,000 Angstroms at a resolution of 0.05 Angstroms.

Data Handling
=============

We provide here a few key points on how **pwv_kpno** handles the parsing,
fitting, and error propagation of raw SuomiNet data. Questions not already
answered by the **pwv_kpno** science paper `Perrefort, Wood-Vasey et al. 2018
<https://arxiv.org/abs/1806.09701>`_ are welcomed, and can be submitted via
GitHub (see the "Need Help?" link above).

SuomiNet Rounding Error
-----------------------

Standard SuomiNet data files are published with PWV and PWV error values
recorded to a one decimal point precision. Unfortunately, the error in PWV can
sometimes be less than 0.05. As a result the SuomiNet data pipeline will round
these results to have an error of 0. To account for this loss of information,
**pwv_kpno** adds a conservative 0.025 error to all downloaded PWV
measurements.

The datetime format used by SuomiNet also suffers intrinsically from rounding
error. This only effects certain datetimes, and is automatically corrected.

Duplicate and Negative Data
---------------------------

In very rare instances, SuomiNet data files may contain two measurements for
a given datetime that are unequal. Since there is no way to determine from
the data files themselves which on is correct, **pwv_kpno** ignores both of
these entries. In the case where there are duplicate datetime entries with the
same measurements, these entries are kept.

In the published SuomiNet data there are also occasional instances when the
measured PWV column density is negative. In some (but not necessarily all)
cases this can be attributed to a malfunction of a particular GPS receiver.
measurements for any time when the reported PWV concentration is negative
are ignored.
