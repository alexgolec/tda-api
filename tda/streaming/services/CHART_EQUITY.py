from .base import _BaseService
from .fields import _BaseFieldEnum

class CHART_EQUITY(_BaseService):
    class Fields(_BaseFieldEnum):
        '''
        `Official documentation <https://developer.tdameritrade.com/content/
        streaming-data#_Toc504640589>`__

        Dat.fields for equity OHLCV data. Primarily an implementation detail
        and not used in client code. Provided here as documentation for key
        values stored returned in the stream messages.
        '''

        #: Ticker symbol in upper case. Represented in the stream as the
        #: ``key`` field.
        SYMBOL = 0

        #: Opening price for the minute
        OPEN_PRICE = 1

        #: Highest price for the minute
        HIGH_PRICE = 2

        #: Chart’s lowest price for the minute
        LOW_PRICE = 3

        #: Closing price for the minute
        CLOSE_PRICE = 4

        #: Total volume for the minute
        VOLUME = 5

        #: Identifies the candle minute. Explicitly labeled "not useful" in the
        #: official documentation.
        SEQUENCE = 6

        #: Milliseconds since Epoch
        CHART_TIME = 7

        #: Documented as not useful, included for completeness
        CHART_DAY = 8
