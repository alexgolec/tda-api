from enum import Enum

from . import common
from . import equities
from . import generic
from . import options

import sys
assert sys.version_info[0] >= 3

__error_message = (
        'EquityOrderBuilder has been deleted from the library. Please use ' +
        'OrderBuilder and its associated templates instead. See here for ' +
        'details: https://tda-api.readthedocs.io/en/latest/' +
        'order-templates.html#what-happened-to-equityorderbuilder')

if sys.version_info[1] >= 7:
    def __getattr__(name):
        if name == 'EquityOrderBuilder':
            raise ImportError(__error_message)
        raise AttributeError(name)
else:  # pragma: no cover
    class EquityOrderBuilder:
        def __init__(self, *args, **kwargs):
            raise NotImplementedError(globals()['__error_message'])
