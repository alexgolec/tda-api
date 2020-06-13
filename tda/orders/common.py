from enum import Enum


class InvalidOrderException(Exception):
    '''Raised when attempting to build an incomplete order'''
    pass


class Duration(Enum):
    DAY = 'DAY'
    GOOD_TILL_CANCEL = 'GOOD_TILL_CANCEL'
    FILL_OR_KILL = 'FILL_OR_KILL'


class Session(Enum):
    NORMAL = 'NORMAL'
    AM = 'AM'
    PM = 'PM'
    SEAMESS = 'SEAMLESS'
