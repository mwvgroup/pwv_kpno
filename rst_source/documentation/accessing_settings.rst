**************************
Accessing Package Settings
**************************

By default *pwv_kpno* provides models for the PWV transmission function at
Kitt Peak National Observatory. However, *pwv_kpno* also provides atmospheric
modeling for user customized sites.

Available Sites and Settings
============================

Support for modeling multiple geographical sites is handled by the
``package_settings`` module, and allows modeling at any location with a
SuomiNet connected GPS receiver. A list of sites that are available with a
particular install of *pwv_kpno* can be retrieved by running

.. code-block:: python
    :linenos:

    >>> from pwv_kpno.package_settings import settings
    >>> print(settings.available_sites)

        ['kitt_peak']

The returned list will contain the default location (``'kitt_peak'``) in
addition to any custom locations that have been installed on your current
machine. A complete summary of package settings for the current site being
modeled can be accessed by printing the ``settings`` object. For example, the
settings for Kitt Peak are as follows

.. code-block:: python
    :linenos:

    >>> settings.set_site('kitt_peak')
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

        Available Data:
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
        Reveiver    Value       Type          Lower_Bound          Upper_Bound  unit
        ----------------------------------------------------------------------------
        AZAM    SrfcPress  inclusive                  880                  925  mbar
        KITT    SrfcPress  inclusive                  775                 1000  mbar
        KITT         date  exclusive  2016-01-01 00:00:00  2016-04-01 00:00:00   UTC
        P014    SrfcPress  inclusive                  850                 1000  mbar
        SA46    SrfcPress  inclusive                  900                 1000  mbar
        SA48    SrfcPress  inclusive                  910                 1000  mbar

Alternatively, individual settings can be accessed, but not modified, using
attributes.

.. code-block:: python
    :linenos:

    >>> print(settings.site_name)

        kitt_peak

    >>> print(settings.receivers)

        ['AZAM', 'KITT', 'P014', 'SA46', 'SA48']

    >>> print(settings.primary_rec)

        'KITT'

    >>> print(settings.supplement_rec)

        ['AZAM', 'P014', 'SA46', 'SA48']