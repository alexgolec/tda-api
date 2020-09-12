from .base import _BaseService
from .fields import _BaseFieldEnum

class CHART_FUTURES(_BaseService):
    class Fields(_BaseFieldEnum):
        '''
        `Official documentation <https://developer.tdameritrade.com/content/
        streaming-data#_Toc504640592>`__

        Dat.fields for equity OHLCV data. Primarily an implementation detail
        and not used in client code. Provided here as documentation for key
        values stored returned in the stream messages.
        '''

        #: Ticker symbol in upper case. Represented in the stream as the
        #: ``key`` field.
        SYMBOL = 0

        #: Milliseconds since Epoch
        CHART_TIME = 1

        #: Opening price for the minute
        OPEN_PRICE = 2

        #: Highest price for the minute
        HIGH_PRICE = 3

        #: Chart’s lowest price for the minute
        LOW_PRICE = 4

        #: Closing price for the minute
        CLOSE_PRICE = 5

        #: Total volume for the minute
        VOLUME = 6
