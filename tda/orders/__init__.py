from enum import Enum

from . import common
from . import equities
from . import generic
from . import options

def __getattr__(name):
    if name == 'EquityOrderBuilder':
        raise ImportError(
                'EquityOrderBuilder has been deleted from the library. ' +
                'Please use OrderBuilder and its associated templates ' +
                'instead. See here for details: ' +
                'https://tda-api.readthedocs.io/en/latest/' +
                'order-templates.html#what-happened-to-equityorderbuilder')
