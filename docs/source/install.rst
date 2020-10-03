Installation
============

To install the **pwv_kpno** API, please choose one of the options below.

Install Using PIP (Recommended)
-------------------------------

Using the `pip package manager <https://pip.pypa.io/en/stable/>`_ is the
recommended method for installing **pwv_kpno**. To install with pip, run:

.. code-block:: bash

    pip install pwv_kpno

The pip package manager will automatically install any missing dependencies
in your Python environment. If you have any issues installing the package,
try installing the dependency manually and then reinstall **pwv_kpno**.
Dependencies can be installed manually with pip by running:

.. code-block:: bash

    pip install -r requirements.txt

Install from Source
-------------------

The package source code can be downloaded from GitHub_.

.. _GitHub: https://github.com/mwvgroup/pwv_kpno.git

.. code-block:: bash

   git clone https://github.com/mwvgroup/pwv_kpno.git

The package can then be installed by running the included setup file:

.. code-block:: bash

   python pwv_kpno/setup.py install --user

As in the previous method, any missing dependencies in your Python environment
should be installed automatically. If you have any issues installing the
package, install each dependency from requirements.txt and then try again.

Package Setup
-------------

By default, data downloaded by the **pwv_kpno** package is downloaded to the
installation directory. While this avoids most potential permission erros,
it also means that each installation of the package will download and manage
duplicate data. If you are working with multiple environments, the
``SUOMINET_DIR`` variable can be set in the working environment to configure
where data should be downloaded by the **pwv_kpno** package.

Running Tests
-------------

If desired, you can run the **pwv_kpno** test suite against the installed
package. This can be accomplished using pip:

.. code-block:: bash

   pip install --install-option test

or using the ``setup.py`` file:

.. code-block:: bash

   python setup.py test
