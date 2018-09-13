**********************
Installation and Setup
**********************

**pwv_kpno** is designed to be compatible with Python 2.7, and 3.5 through 3.7.
The use of other python versions is possible, but not explicitly supported.
If you experience installation problems that are not resolved by trying the
suggestions below, please raise an issue on `GitHub
<https://github.com/mwvgroup/pwv_kpno>`_.

Installation
============

To install the package, please choose from one of the following options:

Using PIP (Recommended)
-----------------------

Using the `pip package manager <https://pip.pypa.io/en/stable/>`_ is the
recommended method for installing **pwv_kpno**. To install with pip, run:

.. code-block:: bash
   :linenos:

    pip install pwv_kpno

The pip package manager will automatically install any missing dependencies
in your Python environment. If you have any issues installing the package,
try installing each dependency individually and then reinstall **pwv_kpno**.
Dependencies can be installed with pip by running:

.. code-block:: bash
   :linenos:

    pip install numpy
    pip install astropy
    pip install requests
    pip install pytz
    pip install scipy


Using setup.py
--------------

If you don't have pip available on your system, the source code can be
downloaded from `GitHub <https://github.com/mwvgroup/pwv_kpno>`_. **pwv_kpno**
can be installed by directly running:

.. code-block:: bash
   :linenos:

    python setup.py install --user

As in the previous method, any missing dependencies in your Python environment
should be installed automatically. If you have any issues installing the
package, first install each dependency individually and then try again.

Package Setup
=============

**pwv_kpno** relies on PWV measurements taken by the SuomiNet project. In order
to model the PWV transmission function for a given date, SuomiNet data for that
date must be available on the host machine. By default, each release of
**pwv_kpno** contains all SuomiNet data for Kitt Peak National Observatory
from 2010 through the end of the previous year. It is recommended to update the
local SuomiNet data after installing or updating the package, and periodically
as necessary.

To download any new SuomiNet data use the ``update_models`` function:

.. code-block:: python
    :linenos:

    >>> from pwv_kpno import pwv_atm
    >>> pwv_atm.update_models()

Further documentation on updating the locally available data can be found
`here <./accessing_data.html>`_.
