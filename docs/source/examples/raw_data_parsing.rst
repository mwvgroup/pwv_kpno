Usage Example
-------------


.. code-block:: python

   from pwv_kpno.file_parsing import read_suomi_file

   test_path = 'my/file/path.plt'
   file_data = read_suomi_file(test_path)
   print(file_data)