#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""Utilities used to ensure a stable and predictable testing environment"""

import functools
import os
from tempfile import TemporaryDirectory


class TestWithCleanEnv:
    """Context manager and decorator for running tests in a clean environment

    Clears all environmental variables and sets ``SUOMINET_DIR`` to a temporary
    directory.
    """

    def __init__(self, data_path: str = None):
        """Clears all environmental variables and set ``SUOMINET_DIR``

        Value for ``SUOMINET_DIR`` defaults to a temporary directory.

        Args:
            data_path: Optional path to set ``SUOMINET_DIR`` to
        """

        self._data_path = data_path

    def __call__(self, obj):
        # Decide whether we should wrap a callable or a class

        if isinstance(obj, type):
            return self._decorate_class(obj)

        return self._decorate_callable(obj)

    def __enter__(self):
        # Store a copy of environmental variables and clear the environment

        self._old_environ = dict(os.environ)
        os.environ.clear()

        if self._data_path:  # Use user defined path
            os.environ['SUOMINET_DIR'] = self._data_path

        else:
            self._temp_dir = TemporaryDirectory()
            os.environ['SUOMINET_DIR'] = self._temp_dir.name

    def __exit__(self, *args):
        # Restore the original environment

        os.environ.clear()
        os.environ.update(self._old_environ)

        if not self._data_path:  # If there is no user defined path
            self._temp_dir.cleanup()

    @staticmethod
    def _decorate_callable(func: callable) -> callable:
        # Decorates a callable

        @functools.wraps(func)
        def inner(*args, **kwargs):
            with TestWithCleanEnv():
                return func(*args, **kwargs)

        return inner

    def _decorate_class(self, wrap_class: type) -> type:
        # Decorates methods in a class with request_mock
        # Method will be decorated only if it name begins with ``test_``

        for attr_name in dir(wrap_class):
            # Skip attributes without correct prefix
            if not attr_name.startswith('test_'):
                continue

            # Skip attributes that are not callable
            attr = getattr(wrap_class, attr_name)
            if not hasattr(attr, '__call__'):
                continue

            setattr(wrap_class, attr_name, self._decorate_callable(attr))

        return wrap_class
