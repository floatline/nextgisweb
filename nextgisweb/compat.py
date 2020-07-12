# -*- coding: utf-8 -*-
from __future__ import division, absolute_import, print_function, unicode_literals
import six

if six.PY3:
    from functools import lru_cache
    from pathlib import Path
else:
    from backports.functools_lru_cache import lru_cache
    from pathlib2 import Path

__all__ = [
    'lru_cache',
    'Path'
]


def datetime_to_timestamp(value):
    if six.PY3:
        return value.timestamp()
    else:
        from time import mktime
        return mktime(value.timetuple())


def timestamp_to_datetime(value):
    from datetime import datetime
    if six.PY3:
        return datetime.fromtimestamp(value)
    else:
        return datetime.utcfromtimestamp(value)
