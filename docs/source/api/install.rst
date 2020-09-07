**********************
Installation and Setup
**********************

Version 2.0+ of **pwv_kpno** is designed to be compatible with 3.5 onward.
The use of other python versions is possible, but not explicitly supported.
If you experience installation problems that are not resolved by trying the
suggestions below, please raise an issue on
`GitHub <https://github.com/mwvgroup/pwv_kpno/issues/new/choose>`_.

Installation
============

To install the package, please choose from one of the options below.

Using PIP (Recommended)
-----------------------

Using the `pip package manager <https://pip.pypa.io/en/stable/>`_ is the
recommended method for installing **pwv_kpno**. To install with pip, run:

.. code-block:: bash
   :linenos:

    pip install pwv_kpno

The pip package manager will automatically install any missing dependencies
in your Python environment. If you have any issues installing the package,
try installing the dependency manually and then reinstall **pwv_kpno**.
Dependencies can be installed with pip by running:

.. code-block:: bash
   :linenos:

    pip install -r requirements.txt


Using setup.py
--------------

If you don't have pip available on your system, the package source code can be
downloaded from `GitHub <https://github.com/mwvgroup/pwv_kpno>`_.
The package can then be installed by running the following from the project's
root directory:

.. code-block:: bash
   :linenos:

    python setup.py install --user

As in the previous method, any missing dependencies in your Python environment
should be installed automatically. If you have any issues installing the
package, install each dependency from ``requirements.txt`` and then try again.
