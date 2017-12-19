**********************
Installation and Setup
**********************

**pwv_kpno** is designed to be compatible with both Python 2.7 and 3.6.
The use of other python versions is possible, but not explicitly supported.
If you experience problems installing **pwv_kpno** that are not resolved by
trying the suggestions below, please raise an issue on `GitHub
<https://github.com/mwvgroup/pwv_kpno>`_.

Installation
============

To install the package, please choose from one of the following options:

Using PIP (Recommended)
-----------------------

Using the pip package manager is the recommended method for installing
**pwv_kpno**. To install with pip, use::

    pip install pwv_kpno

The pip package manager will automatically install any missing dependencies
in your Python environment. If you have any issues installing the package,
try installing each dependency individually and then reinstall **pwv_kpno**.
Dependencies can be installed with pip by running::

    pip install numpy
    pip install astropy
    pip install requests
    pip install pytz
    pip install scipy

|
Using setup.py (Legacy)
-----------------------

If you don't have pip available on your system, **pwv_kpno** can be installed
by directly running::

    python setup.py install --user

As in the previous method, any missing dependencies in your Python environment
should be installed automatically. If you have any issues installing the
package, first install each dependency individually and then try again.


Package Setup
=============

**pwv_kpno** relies on PWV measurements taken by the SuomiNet project. In order
to model the PWV transmission function for a given date, SuomiNet data for that
date must be available on the host machine. By default, **pwv_kpno** contains
all necessary SuomiNet data from 2010 through the end of 2016. It is
recommended to update the local SuomiNet data after installing or updating the
package, and periodically as necessary.

To download any new SuomiNet data use the update_models
function::

    >>> import pwv_kpno
    >>> pwv_kpno.update_models()

Optionally, you can download data only for a specific year by passing the year
as an argument::

    >>> pwv_kpno.update_models(year=2017)

Note that the update_models function requires the user to have permission to
write and modify files within the package directory.

|
Running Tests
=============

If desired, the full test suite can be run using::

    python setup.py tests

Note that **pwv_kpno** includes tests that download SuomiNet data from the
internet (under 16 MB).