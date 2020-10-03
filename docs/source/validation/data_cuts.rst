*********
Data Cuts
*********

KPNO Pressure Cuts
==================

The barometric sensor at Kitt Peak was malfunctioning in 2016 from January
through March, so we ignore any SuomiNet data published for Kitt Peak during
this time period. The sensor has since been repaired, but occasionally records
a non-physical drop in pressure. We disregard these measurements by ignoring
any meteorological measurements taken for Kitt Peak with a pressure below 775
mbar. Here we demonstrate this cut against the distribution of pressure
measurements taken at Kitt Peak from March 2015 through the end of 2017.

.. rst-class:: validation_figure
.. figure::  /../../_static/images/pressure_cut.png
   :target: ../../_static/images/pressure_cut.png
   :align:   center

General Data Cuts
=================

Unlike temperature or PWV column density, we expect the atmospheric pressure
at a given location to fluctuate within a fairly narrow range. This makes
pressure measurements a natural indicator for outlier and non-physical data
points. Demonstrated below, we ignore PWV measurements that lie outside a
site-specific pressure range. Note that measurements for Kitt Peak have an
additional cut for periods when the barometric sensor was malfunctioning.
Dropped data points are shown in orange.


+--------------+------------------+--------------------+--------------------+
| Site Name    | Receiver ID Code | Lower Pressure Cut | Upper Pressure Cut |
+==============+==================+====================+====================+
| Kitt Peak Az | KITT             | 775 mbar           | 1000 mbar          |
+--------------+------------------+--------------------+--------------------+
| Amado Az     | AZAM             | 880 mbar           | 925 mbar           |
+--------------+------------------+--------------------+--------------------+
| Sahuarita AZ | P014             | 870 mbar           | 1000 mbar          |
+--------------+------------------+--------------------+--------------------+
| Tuscon Az    | SA46             | 900 mbar           | 1000 mbar          |
+--------------+------------------+--------------------+--------------------+
| Sells Az     | SA48             | 910 mbar           | 1000 mbar          |
+--------------+------------------+--------------------+--------------------+

.. rst-class:: validation_figure
.. image::  /../../_static/images/data_cuts.png
   :target: ../../_static/images/data_cuts.png
   :align:   center
