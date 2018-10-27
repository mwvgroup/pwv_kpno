*************************
Custom Sites and Settings
*************************

The **pwv_kpno** package provides access to models for the atmospheric
transmission due to PWV at any site within the
`SuomiNet <http://www.suominet.ucar.edu>`_  GPS network. However, the package
is configured by default to return models for Kitt Peak National Observatory.
This page provides instructions on how to add and retrieve models for
additional sites.

Available Sites and Settings
============================

A list of sites that are available with a particular install of **pwv_kpno**
can be retrieved by running

.. code-block:: python
    :linenos:

    >>> from pwv_kpno.package_settings import settings
    >>> print(settings.available_sites)

        ['kitt_peak']

The returned list will contain the default location ``'kitt_peak'`` in
addition to any custom locations that have been installed on your current
machine. The package can be configured to model a particular location by
running

.. code-block:: python
    :linenos:

    >>> settings.set_site('cerro_tololo')

After setting pwv_kpno to a model a specific site, the package will return
atmospheric models and PWV data exclusively for that site. It is important to
note that this setting is not persistent. When pwv_kpno is first imported into
a new environment the package will always default to using the standard model
for Kitt Peak, and the above command will have to be rerun.

A complete summary of package settings for the current site being
modeled can be accessed by printing the ``settings`` object. For example,
the settings for Kitt Peak are as follows:

.. code-block:: python
    :linenos:

    >>> print(settings)
      
                           pwv_kpno Current Site Information
      ============================================================================
      Site Name:            kitt_peak 
      Primary Receiver:     KITT
      Secondary Receivers:
          AZAM
          P014
          SA46
          SA48
      
      Years Downloaded from SuomiNet:
          2010
          2011
          2012
          2013
          2014
          2015
          2016
          2017
      
                                       Data Cuts
      ============================================================================
      Receiver    Value       Type          Lower_Bound          Upper_Bound  unit
      ----------------------------------------------------------------------------
      AZAM    SrfcPress  inclusive                  880                  925  mbar
      KITT    SrfcPress  inclusive                  775                 1000  mbar
      KITT         date  exclusive  2016-01-01 00:00:00  2016-04-01 00:00:00   UTC
      P014    SrfcPress  inclusive                  870                 1000  mbar
      SA46    SrfcPress  inclusive                  900                 1000  mbar
      SA48    SrfcPress  inclusive                  910                 1000  mbar

Alternatively, individual settings can be accessed individually using
attributes. Of these settings,

.. code-block:: python
    :linenos:

    >>> # The unique name for the current site being modeled
    >>> print(settings.site_name)

        kitt_peak

    >>> # A list of all SuomiNet GPS receivers that pwv_kpno is using
    >>> # data from for the current site
    >>> print(settings.receivers)

        ['AZAM', 'KITT', 'P014', 'SA46', 'SA48']

    >>> # The ID code for the primary GPS receiver which
    >>> # directly measures PWV for the current site
    >>> print(settings.primary_rec)

        'KITT'

    >>> # The ID codes for GPS receivers near the primary receiver.
    >>> # These are used to supplement measurements from the primary receiver
    >>> print(settings.supplement_rec)

        ['AZAM', 'P014', 'SA46', 'SA48']

    >>> # Cuts applied to data downloaded from SuomiNet
    >>> print(settings.data_cuts)

        {
        'AZAM': {'SrfcPress': [[880, 925]]},
        'KITT': {'SrfcPress': [[775, 1000]], 'date': [[1451606400.0, 1459468800.0]]},
        'P014': {'SrfcPress': [[870, 1000]]},
        'SA46': {'SrfcPress': [[900, 1000]]},
        'SA48': {'SrfcPress': [[910, 1000]]}
         }

Defining a Custom Location
==========================

Each site modeled by **pwv_kpno** is defined by a unique configuration file.
The ``ConfigBuilder`` class allows users to create customized configuration
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
of other, nearby receivers that can be used to supplement data taken by
``primary_rec``. Unlike the default model for KPNO, there are no additional
receivers near the CTIO and so ``sup_rec`` in this example is left as an
empty list (the default value).

Custom Transmission Models
==========================

By default, **pwv_kpno** models use MODTRAN estimates for the wavelength dependent
cross section of H\ :sub:`2`\ O. from 3,000 to 12,000 Angstroms. The optional
``wavelengths`` and ``cross_sections`` arguments allow a user to customize
these cross sections in units of Angstroms and cm\ :sup:`2` respectively.

.. code-block:: python
    :linenos:

    >>> from pwv_kpno.package_settings import ConfigBuilder
    >>>
    >>> new_config = ConfigBuilder(
    >>>     site_name='cerro_tololo',
    >>>     primary_rec='CTIO',
    >>>     sup_rec=[],
    >>>     wavelength=custom_wavelengths, # Array of wavelengths in Angstroms
    >>>     cross_section=custom_cross_sections # Array of cross sections in cm^2
    >>> )
    >>>
    >>> new_config.save_to_ecsv('./cerro_tololo.ecsv')

Specifying Data Cuts
====================

If desired, users can specify custom data cuts on SuomiNet data used by the
package. Data cuts are defined using a 2-dimensional dictionary of boundary
values. The first key specifies which receiver the data cuts apply to. The
second key specifies what values to cut. Following SuomiNet's naming
convention, values that can be cut include the following:

+---------------------+------------------+------------------+----------------+
| Value               |  Key             |  Expected Units  | Data Cut Type  |
+=====================+==================+==================+================+
| Date of Measurement | ``"Date"``       | UTC timestamp    | Exclude data   |
+---------------------+------------------+------------------+----------------+
| Water Vapor         | ``"PWV"``        | mm               | Include data   |
+---------------------+------------------+------------------+----------------+
| Water Vapor Error   | ``"PWVerr"``     | mm               | Include data   |
+---------------------+------------------+------------------+----------------+
| Surface Pressure    | ``"SrfcPress"``  | mbar             | Include data   |
+---------------------+------------------+------------------+----------------+
| Surface Temperature | ``"SrfcTemp"``   | Centigrade       | Include data   |
+---------------------+------------------+------------------+----------------+
| Relative Humidity   | ``"SrfcRH"``     | %                | Include data   |
+---------------------+------------------+------------------+----------------+

For example, if the weather station at Cerro Tololo began to malfunction between
two dates we could ignore these measurements by specifying:

.. code-block:: python
    :linenos:

    >>> data_cuts = {'CTIO':
    >>>     {'Date': [[timestamp_start, timestamp_start],]}
    >>> }

    >>> new_config = ConfigBuilder(
    >>>     site_name='cerro_tololo',
    >>>     primary_rec='CTIO',
    >>>     data_cuts=data_cuts
    >>> )

Data cuts can also be modified for the current site being modeled via the
``settings`` object

.. code-block:: python
    :linenos:

    >>> from pwv_kpno.package_settings import settings
    >>> settings.data_cuts['CTIO']['Date'].append([timestamp_start, timestamp_start])

Note that in order for these changes to take full effect, the PWV model for the
primary site must be updated. This must be performed even if you are modeling a
custom site without any supplemental receivers:

.. code-block:: python
    :linenos:

    >>> from pwv_kpno import pwv_atm
    >>>
    >>> years_to_download = pwv_atm.downloaded_years()
    >>> pwv_atm.update_models(years_to_download)

.. note:: A fully worked out example on how to choose and visualize your chosen
  data cuts is available in the `Examples section<../../examples/html/data_cuts.html>`_.


.. warning:: Any modifications to the data cuts for a given site are persistent
  and cannot be automatically undone. To undo any changes to
  ``settings.data_cuts`` you will need to manually modify the attribute to
  its previous state.

Importing a New Location
========================

Once a configuration file has been created, it can be permanently added to the
locally installed **pwv_kpno** package by running

.. code-block:: python
    :linenos:

    >>> from pwv_kpno.package_settings import settings
    >>> settings.import_site_config('./cerro_tololo.ecsv')

This command only needs to be run once, after which **pwv_kpno** will retain
the new model on disk. The package can then be configured to use the new model
by running

.. code-block:: python
    :linenos:

    >>> settings.set_site('cerro_tololo')
    >>> print(settings.site_name)

After setting **pwv_kpno** to a new location, the package will exclusively use
the new model until the current Python environment is terminated.

.. note:: This setting is not persistent. When **pwv_kpno** is
    first imported into a new environment the package will always default to using
    the standard model for Kitt Peak and the above command will have to be rerun.

Exporting Current Settings
==========================

The configuration file for the currently modeled location can be exported in
ecsv format by running:

.. code-block:: python
    :linenos:

    >>> settings.export_site_config('./cerro_tololo.ecsv')

It is recommended to keep a backup of any custom configuration files added
to your **pwv_kpno** install. This is especially important because
reinstalling or updating the package will delete your custom sites.
