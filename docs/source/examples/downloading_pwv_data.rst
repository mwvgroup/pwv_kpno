Downloading PWV Data
====================

The ``ReleaseDownloader`` class is best suited for situations where explicit
control is required over the individual files that are downloaded.
For all other cases, use the ``DownloadManager`` class.

Usage Example
-------------

Here is an example on how to download and delete data from your local machine.

.. code-block:: python

   from pwv_kpno.downloads import DownloadManager

   # The DownloadManager will automatically determine where data is located on
   # the local machine
   manager = DownloadManager()
   print('Default download director:', manager.data_dir

   # You can also specify an alternative download destination
   custom_manager = DownloadManager('./data')

   # Here we download data for Kitt Peak
   custom_manager.download_available_data('kitt', year=2015)
   custom_manager.download_available_data('kitt', year=[2016, 2017])

   # We can also delete local data
   custom_manager.delete_local_data('Kitt')
