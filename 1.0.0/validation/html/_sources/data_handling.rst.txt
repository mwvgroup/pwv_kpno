*************
Data Handling
*************

Here we discuss how **pwv_kpno** handles the parsing, fitting, and error
propagation of raw SuomiNet data. While this is not technically part of the
validation process, the design decisions outlined here have a direct effect
on carious values and errors reported by the package.

SuomiNet Rounding Error
=======================

Standard SuomiNet data files are published with PWV and PWV error values
recorded to a one decimal point precision. Unfortunately, the error in PWV can
sometimes be less than 0.05. As a result, the SuomiNet data pipeline will round
these some measurements to have an error of 0.0. To account for this loss of
information, **pwv_kpno** adds a conservative 0.025 error to all downloaded PWV
measurements.

The datetime format used by SuomiNet also suffers intrinsically from rounding
error. This only effects certain datetimes, and is automatically corrected.

Duplicate and Negative Data
===========================

In very rare instances, SuomiNet data files may contain two measurements for
a given location and datetime that are unequal. Since there is no way to
determine from the data files which value is correct, **pwv_kpno** ignores
both entries. In the case where there are duplicate datetime entries with the
same measurements, these entries are kept.

In the published SuomiNet data there are occasional instances when the
measured PWV column density is unmasked and negative. In some (but not
necessarily all) cases this can be attributed to a malfunction of a particular
GPS receiver. Measurements for any time when the reported PWV concentration is
negative are ignored.

Hourly and Daily Publications
=============================

For GPS sites located within the continental United States, SuomiNet
measurements are published hourly and then reprocessed and published again
daily. Hourly data releases are provided for convenience, but may not be
as accurate as the daily releases. As such **pwv_kpno** uses measurements from
the daily data releases whenever possible, and suppliments these measurements
with the hourly releases when daily data is not available.

Supplemental Receivers
======================
