Transmission Modeling
=====================



Evaluating a Transmission Model
-------------------------------

Transmission models in **pwv_kpno** are callable objects that evaluate the
atmospheric PWV transmission function for a given set of wavelengths and
PWV concentrations. Although it is possible to define a customized model
(see below), we here use a prebuilt model for convenience.

By default, transmission models are returned for a given PWV concentration at
the highest available resolution

.. code-block:: python
   :linenos:

   from pwv_kpno.defaults import v1_transmission

   pwv = 5
   transmission = v1_transmission(pwv)
   print(transmission)

   > wave
   > 3000.00     1.000000
   > 3000.05     1.000000
   > 3000.10     1.000000
   > 3000.15     1.000000
   > 3000.20     1.000000
   >               ...
   > 11999.80    0.995957
   > 11999.85    0.995927
   > 11999.90    0.995875
   > 11999.95    0.995805
   > 12000.00    0.995718
   > Name: 5.0 mm, Length: 180001, dtype: float64

Notice when evaluating transmission models for a single PWV concentration, the
returned value is a pandas ``Series`` object. An array of PWV values can also
be passed to the model, in which case the return will be a pandas ``DataFrame``:

.. code-block:: python
   :linenos:

   vector_pwv = [5, 10]
   transmission = v1_transmission(vector_pwv)
   print(transmission)

   >             5.0 mm   10.0 mm
   > wave
   > 3000.00   1.000000  1.000000
   > 3000.05   1.000000  1.000000
   > 3000.10   1.000000  1.000000
   > 3000.15   1.000000  1.000000
   > 3000.20   1.000000  1.000000
   > ...            ...       ...
   > 11999.80  0.995957  0.991931
   > 11999.85  0.995927  0.991871
   > 11999.90  0.995875  0.991767
   > 11999.95  0.995805  0.991627
   > 12000.00  0.995718  0.991453

The transmission model can also be evaluated for a given set of wavelengths
by specifying the ``wave`` argument (in units of Angstroms). The returned
values are determined by linearly interpolating from the underlying transmission
values.

.. code-block:: python
   :linenos:

   pwv = 5
   wavelengths = range(3_000, 12_000)
   transmission = trans_model(pwv, wave=wavelengths)
   print(transmission)

   > 3000     1.000000
   > 3001     1.000000
   > 3002     1.000000
   > 3003     1.000000
   > 3004     1.000000
   >            ...
   > 11995    0.996006
   > 11996    0.994342
   > 11997    0.934950
   > 11998    0.987888
   > 11999    0.995811
   > Name: 5.0 mm, Length: 9000, dtype: float64


Reducing Model Resolution
-------------------------

You may have to bin the resolution of the modeled transmission function to
match an existing data set (e.g., the SED of a spectroscopically observed
object). This can be accomplished by specifying the resolution argument.
Here is an example that visualizes the effect of the ``res`` argument:

.. code-block:: python
   :linenos:

   from matplotlib import pyplot as plt

   full_res = v1_transmission(pwv, wavelengths)
   lower_res = v1_transmission(pwv, wavelengths, res=10)

   plt.plot(full_res.index, full_res, label='Default resolution')
   plt.plot(full_res.index, lower_res, label='res = 10')
   plt.xlabel('Wavlengths (Angstrom)')
   plt.ylabel('Transmission')
   plt.legend()
   plt.show()

.. rst-class:: validation_figure
.. image::  /../../_static/images/res_arg_demo.png
   :target: ../../_static/images/res_arg_demo.png
   :align:   center

Defining a Transmission Model
-----------------------------

The **pwv_kpno** package provides predefined transmission models as part of the
``defaults`` module. However, customized transmission models can also be defined
using one of the below options. Each available option represents a
different approach to how the atmospheric transmission is calculated for a
given PWV concentration.

Interpolation Models (Recommended)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The ``TransmissionModel`` class determines the PWV transmission function by
linearly interpolating through pre-tabulated transmission values sampled from
a uniform grid of PWV concentrations and wavelengths. Here we demonstrate a
mock transmission model with transmission values that are uniform with
wavelength, but decrease linearly with PWV

.. code-block:: python
   :linenos:

   import numpy as np
   from pwv_kpno.transmission import TransmissionModel

   pwv_grid_points = [0, 2, 4]
   wave_grid_points = range(6_000, 8_000, 100)  # Expected in Angstroms
   sim_trans = [
      np.ones_like(wave_grid_points),
      np.full_like(wave_grid_points, .5),
      np.zeros_like(wave_grid_points)
   ]

   trans_model = TransmissionModel(pwv_grid_points, wave_grid_points, sim_trans)

Cross Section Models
^^^^^^^^^^^^^^^^^^^^

The ``CrossSectionTransmission`` class determines the PWV transmission function
by evaluating the Beer-Lambert law for a set of per-wavelength molecular
cross-sections. Cross section values must be specified in units of
:math:`cm^2`. Wavlength values must be specified in units of Angstroms.

.. code-block:: python
   :linenos:

   from pwv_kpno.transmission import CrossSectionTransmission

   wavelengths = [3000.00, 3000.05, ..., 11999.95, 12000.00]
   cross_sections = [1.711160e-30, 1.711250e-30, ..., 2.515410e-25, 2.567750e-25]
   trans_model = CrossSectionTransmission(wavelengths, cross_sections)
