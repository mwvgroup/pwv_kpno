Downloading PWV Data
====================

The ``DownloadManager`` class automates the process of downloading SuomiNet
data for use by the **pwv_kpno** package. Instances of the ``DownloadManager``
class will automatically determine where
data is located on on the current machine. By default, data is downloaded into
the installation directory of the parent package. This prevents permission
errors and prohibits data sharing across Python environments.

Downloading PWV Data
--------------------

.. code-block:: python

   from pwv_kpno.downloads import DownloadManager

   manager = DownloadManager()
   print('Default download director:', manager.data_dir

You can also specify an alternative download destination

.. code-block:: python

   custom_manager = DownloadManager('./data')

To permanently change where data is downloaded on your local machine,
the desired path can be configured by defining the ``SUOMINET_DIR`` variable
in the working environment (See installation instruction for more details).

Data can be downloaded for a given GPS receiver using the receiver's
SuomiNet Id and the desired years to download data for.

.. code-block:: python

   custom_manager.download_available_data('kitt', year=2015)
   custom_manager.download_available_data('kitt', year=[2016, 2017])


Managing Local Data
-------------------

Manager objects can identify what receivers have locally available data.

.. code-block:: python

   custom_manager.check_downloaded_receivers()  # List of receivers with local data

For a specific GPS receiver 
   custom_manager.check_downloaded_data('KITT')  # List of receivers with local data


Data can be delete for a given receiver in a similar fashion.

.. code-block:: python

   custom_manager.delete_local_data('Kitt')

