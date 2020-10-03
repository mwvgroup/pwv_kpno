******************
Blackbody Modeling
******************

When calibrating photometric images, astronomers traditionally rely on bright
stars of a known spectral type with very few absorption features. Early A-type
stars are commonly used for this purpose due to their few, weak metal lines and
reasonable approximation as a black body at about 10,000 K. For this reason,
it is useful to understand the impact of atmospheric absorption on the spectral
energy distribution (SED) of a black body.

Absorption Features
===================

The SED of a blackbody at 8,000 K (black) is shown across the i-band (left)
and z-band (right) ranges. Shown in grey, the modeled atmospheric absorption
for a PWV column density of 15 mm is applied to the SED. This is compared to
the black body SED scaled using the integrated absorption in each band in red.

.. rst-class:: validation_figure
.. image::  /../../_static/images/blackbody.png
   :target: ../../_static/images/blackbody.png
   :align:   center

Zero Point Bias
===============

Correcting photometric observations using tabulated values of a standard star
introduces residual error in the magnitudes of other stars with different
spectral types. The residual error in $z$ band photometric zero point due to
absorption by precipitable water vapor is shown for three black bodies at
$3,000$ (M type), $6,000$ (G type), and $10,000$ K (A type). Results are shown
as a function of the color of the reference star used to calculate the zero
point. Error values are shown for a PWV column density of 5 (left) and 30 mm
(right).

.. rst-class:: validation_figure
.. image::  /../../_static/images/zero_point_bias.png
   :target: ../../_static/images/zero_point_bias.png
   :align:   center
