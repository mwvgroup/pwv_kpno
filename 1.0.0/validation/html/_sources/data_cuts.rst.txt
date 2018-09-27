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
mbar. Here we demonstrate the distribution of pressure measurements taken at
Kitt Peak from March 2015 through the end of 2017.

.. rst-class:: validation_figure
.. figure::  _static/pressure_cut.pdf
    :align:   center

General Data Cuts
=================

We expect the surface pressure for a given location to lie within a fairly
narrow range. To eliminate outlier data points, we ignore PWV measurements
that lie outside a site specific pressure range.

.. rst-class:: validation_figure
.. figure::  _static/data_cuts.png
    :align:   center

