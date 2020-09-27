Usage Example
-------------

Aliases from this module can be used to assign type hints for custom functions.

.. code-block:: python

   from pwv_kpno.types import ArrayLike, PathLike

   def custom_file_parser(path: PathLike) -> ArrayLike:
       ...
