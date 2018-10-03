****************
Package Overview
****************

What is pwv_kpno?
=================

**pwv_kpno** is a science focused Python package that provides access to
models for the atmospheric absorption due to H\ :sub:`2`\ O. The strength of
H\ :sub:`2`\ O absorption features are strongly correlated with measurements
of localized PWV column density. By measuring the delay of dual-band GPS signals
traveling through the atmosphere, it is possible to determine the PWV column
density along line of sight. **pwv_kpno** leverages this principle to provide
atmospheric models for user definable sites as a function of date, time, and airmass.

How it Works
============

The SuomiNet project is a meteorological initiative that provides semi-hourly
PWV measurements for hundreds of GPS receivers worldwide. The **pwv_kpno**
package uses published SuomiNet data in conjunction with MODTRAN models to
determine the modeled, time-dependent atmospheric transmission.
By default, the package provides access to the modeled transmission
function at Kitt Peak National Observatory. However, the package is designed
to be easily extensible to other locations within the SuomiNet Network.
Additionally, **pwv_kpno** provides access to atmospheric models as a function
of PWV, which is independent of geographical location. Default atmospheric models
are provided from 3,000 to 12,000 Angstroms at a resolution of 0.05 Angstroms.
