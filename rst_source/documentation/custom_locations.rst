*********************
Modeling Custom Sites
*********************

Defining a New Location
=======================

Each site modeled by *pwv_kpno* is defined by a unique configuration file.
Using the ``ConfigBuilder`` class, users can create customized configuration
files for any SuomiNet site. As a simple example, we create a new configuration
file for the Cerro Tololo Inter-American Observatory near La Serena, Chile.

.. code-block:: python
    :linenos:

    >>> from pwv_kpno.package_settings import ConfigBuilder
    >>>
    >>> new_config = ConfigBuilder(
    >>>     site_name='cerro_tololo',
    >>>     primary_rec='CTIO',
    >>>     sup_rec=[]
    >>> )
    >>>
    >>> new_config.save_to_ecsv('./cerro_tololo.ecsv')

Here ``site_name`` specifies a unique identifier for the site being
modeled, ``primary_rec`` is the SuomiNet ID code for the GPS receiver
located at the modeled site, and ``sup_rec`` is a list of SuomiNet ID codes
for supplementary, off site receivers. Unlike the default model for KPNO, there
are no additional receivers near the CTIO and so ``sup_rec`` in this example
is left empty.

Custom Transmission Models
==========================

By default *pwv_kpno* models use MODTRAN estimates for the wavelength dependent
cross section of H\ :sub:`2`\ O. from 3,000 to 12,000 Angstroms. The optional
``wavelengths`` and ``cross_sections`` arguments allow a user to customize
these cross sections in units of Angstroms and cm^2 respectively.

.. code-block:: python
    :linenos:

    >>> from pwv_kpno.package_settings import ConfigBuilder
    >>>
    >>> new_config = ConfigBuilder(
    >>>     site_name='cerro_tololo', primary_rec='CTIO',
    >>>     sup_rec=[],
    >>>     wavelength=custom_wavelengths, # Array of wavelengths in Angstroms
    >>>     cross_section=custom_cross_sections # Array of cross sections in cm^2
    >>> )
    >>>
    >>> new_config.save_to_ecsv('./cerro_tololo.ecsv')

Specifying Data Cuts
====================

If desired, users can specify custom data cuts on SuomiNet data used by the
package. Data cuts are defined using a 2d dictionary of boundary values.
The first key specifies which receiver the data cuts apply to. The second key
specifies what values to cut. Following SuomiNet's naming convention, values
that can be cut include the following:

 Value                Key              Expected Units   Data Cut Type
===================  ===============  ===============  ===============
Date of Measurement  ``"Date"``       UTC timestamp    Exclude data
Water Vapor          ``"PWV"``        mm               Include data
Water Vapor Error    ``"PWVerr"``     mm               Include data
Surface Pressure     ``"SrfcPress"``  mbar             Include data
Surface Temperature  ``"SrfcTemp"``   Kelvin           Include data
Relative Humidity    ``"SrfcRH"``     %                Include data

For example, if weather station at CTIO began to malfunction between
January 1st, 2050 and February 1st, 2050, we could ignore these measurements
by specifying:

.. code-block:: python
    :linenos:

    >>> data_cuts = {'CTIO':
            {'Date': [[, ],]}
        }

    >>> new_config = ConfigBuilder(
            site_name='cerro_tololo',
            primary_rec='CTIO',
            data_cuts = data_cuts)


Importing a New Location
========================

Once a configuration file has been created, it can be permanently added to the
*pwv_kpno* package by running

.. code-block:: python
    :linenos:

    >>> from pwv_kpno.package_settings import settings
    >>> settings.import_site('./cerro_tololo.ecsv')

This command only needs to be run once, after which *pwv_kpno* will retain
the new model on disk, even in between package updates. The package can then be
configured to use the new model by running

.. code-block:: python
    :linenos:

    >>> settings.set_site('cerro_tololo')

After setting **pwv_kpno** to a new location, the package will exclusively use
the new model until the current Python environment is terminated. It is
important to note that this setting is not persistent. When **pwv_kpno** is
first imported into a new environment the package will always default to using
the standard model for Kitt Peak, and the above command will have to be rerun.

Exporting Current Settings
==========================

The configuration file for the currently modeled location can be exported in
ecsv format by running:

.. code-block:: python
    :linenos:

    >>> settings.export_site('./kitt_two_receivers.ecsv')
