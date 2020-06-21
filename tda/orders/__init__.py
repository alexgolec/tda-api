from enum import Enum

from . import common
from . import equities
from . import generic

__WARNINGS = set()


def __getattr__(name):
    import sys

    def warn(new_package):
        if name not in __WARNINGS:
            replacement_url = ('https://tda-api.readthedocs.io/en/stable/' +
                               'order-templates.html')
            print(('WARNING: {name} has moved from tda.orders to ' +
                   'tda.orders.{new_package}. It will be removed from tda.orders ' +
                   'in a future version. You can find documentation on its '+
                   'replacements here: {url}').format(
                       name=name, new_package=new_package, url=replacement_url),
                   file=sys.stderr)
            __WARNINGS.add(name)

    if name == 'InvalidOrderException':
        warn('equities')
        return common.InvalidOrderException
    elif name == 'Duration':
        warn('common')
        return common.Duration
    elif name == 'Session':
        warn('common')
        return common.Session
    elif name == 'EquityOrderBuilder':
        warn('equities')
        return equities.EquityOrderBuilder
