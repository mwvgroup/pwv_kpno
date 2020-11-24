Installation
============

The **pwv_kpno** package is open source and can be installed using
any of the options listed below.

Install Using PIP (Recommended)
-------------------------------

Using the `pip package manager <https://pip.pypa.io/en/stable/>`_ is the
recommended method for installing **pwv_kpno**. To install with pip, run:

.. code-block:: bash

    pip install pwv_kpno

Install from Source
-------------------

The package source code is available on GitHub_ and can be downloaded from
the GitHub webpage or using the ``git`` command line client:

.. _GitHub: https://github.com/mwvgroup/pwv_kpno.git

.. code-block:: bash

   git clone https://github.com/mwvgroup/pwv_kpno.git

Once the source code has been downloaded, it can be installed in your
current working environment by running the included setup file:

.. code-block:: bash

   python pwv_kpno/setup.py install --user

As in the previous method, any missing dependencies in your Python environment
should be installed automatically. If you have any issues installing the
package, install each dependency listed in the included
``requirements.txt`` file and try again.

Package Setup
-------------

By default, any data downloaded by **pwv_kpno** is stored in the
installation directory. This avoids potential permission errors and cross-talk
between installations in different environments. However, when working with
multiple environments (such as when using conda) you may wish to have
installations share ownership of the downloaded data. In this case, the
``SUOMINET_DIR`` variable can be set in your working environment to configure
where data should be written by the **pwv_kpno** package.

To enable this feature, define the following in your ``.bashrc`` or
``.bash_profile`` file:

.. code-block:: bash

   export SUOMINET_DIR="/my/data/directory"

Running Tests
-------------

You can run the **pwv_kpno** test suite against the installed
package using the ``setup.py`` file included with the source code:

.. code-block::

   pip install --install-option test

or using the ``setup.py`` file:

.. code-block::

   python setup.py test
