Installation
============

To install the **pwv_kpno** API, please choose one of the options below.

Using PIP (Recommended)
-----------------------

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

Legacy Install
--------------

If you don’t have pip available on your system, the package source code can
be downloaded from GitHub. The package can then be installed by running the
following from the project’s root directory:

.. code-block:: bash

   python setup.py install --user

As in the previous method, any missing dependencies in your Python environment
should be installed automatically. If you have any issues installing the
package, install each dependency from requirements.txt and then try again.

Running Tests
-------------

If desired, you can run the **pwv_kpno** test suite against the installed
package. This can be accomplished using pip:

.. code-block:: bash

   pip install --install-option test

or using the ``setup.py`` file:

.. code-block:: bash

   python setup.py test
