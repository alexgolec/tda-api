from .base import _BaseService
from .fields import _BaseFieldEnum

class LEVELONE_FOREX(_BaseService):
    class Fields(_BaseFieldEnum):
        '''
        `Official documentation <https://developer.tdameritrade.com/content/
        streaming-data#_Toc504640606>`__
        '''

        #: Ticker symbol in upper case. Represented in the stream as the
        #: ``key`` field.
        SYMBOL = 0

        #: Current Best Bid Price
        BID_PRICE = 1

        #: Current Best Ask Price
        ASK_PRICE = 2

        #: Price at which the last trade was matched
        LAST_PRICE = 3

        #: Number of shares for bid
        BID_SIZE = 4

        #: Number of shares for ask
        ASK_SIZE = 5

        #: Aggregated shares traded throughout the day, including pre/post
        #: market hours
        TOTAL_VOLUME = 6

        #: Number of shares traded with last trade
        LAST_SIZE = 7

        #: Trade time of the last quote in milliseconds since epoch
        QUOTE_TIME = 8

        #: Trade time of the last trade in milliseconds since epoch
        TRADE_TIME = 9

        #: Day’s high trade price
        HIGH_PRICE = 10

        #: Day’s low trade price
        LOW_PRICE = 11

        #: Previous day’s closing price
        CLOSE_PRICE = 12

        #: Primary "listing" Exchange
        EXCHANGE_ID = 13

        #: Description of the product
        DESCRIPTION = 14

        #: Day's Open Price
        OPEN_PRICE = 15

        #: Current Last-Prev Close
        NET_CHANGE = 16

        # Disabled because testing indicates the API returns some unparsable
        # characters
        # PERCENT_CHANGE = 17

        #: Name of exchange
        EXCHANGE_NAME = 18

        #: Valid decimal points
        DIGITS = 19

        #: Trading status of the symbol. Indicates a symbols current trading
        #: status, Normal, Halted, Closed.
        SECURITY_STATUS = 20

        #: Minimum price movement
        TICK = 21

        #: Minimum amount that the price of the market can change
        TICK_AMOUNT = 22

        #: Product name
        PRODUCT = 23

        # XXX: Documentation has TRADING_HOURS as 23, but testing suggests it's
        # actually 23. See here for details:
        # https://developer.tdameritrade.com/content/streaming-data#_Toc504640606
        #: Trading hours
        TRADING_HOURS = 24

        #: Flag to indicate if this forex is tradable
        IS_TRADABLE = 25

        MARKET_MAKER = 26

        #: Higest price traded in the past 12 months, or 52 weeks
        HIGH_52_WEEK = 27

        #: Lowest price traded in the past 12 months, or 52 weeks
        LOW_52_WEEK = 28

        #: Mark-to-Market value is calculated daily using current prices to
        #: determine profit/loss
        MARK = 29
