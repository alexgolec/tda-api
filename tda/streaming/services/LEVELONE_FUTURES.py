from .base import _BaseService
from .fields import _BaseFieldEnum

class LEVELONE_FUTURES(_BaseService):
    class Fields(_BaseFieldEnum):
        '''
        `Official documentation <https://developer.tdameritrade.com/content/
        streaming-data#_Toc504640603>`__
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

        #: Exchange with the best ask
        ASK_ID = 6

        #: Exchange with the best bid
        BID_ID = 7

        #: Aggregated shares traded throughout the day, including pre/post
        #: market hours
        TOTAL_VOLUME = 8

        #: Number of shares traded with last trade
        LAST_SIZE = 9

        #: Trade time of the last quote in milliseconds since epoch
        QUOTE_TIME = 10

        #: Trade time of the last trade in milliseconds since epoch
        TRADE_TIME = 11

        #: Day’s high trade price
        HIGH_PRICE = 12

        #: Day’s low trade price
        LOW_PRICE = 13

        #: Previous day’s closing price
        CLOSE_PRICE = 14

        #: Primary "listing" Exchange. Notes:
        #:  * I → ICE
        #:  * E → CME
        #:  * L → LIFFEUS
        EXCHANGE_ID = 15

        #: Description of the product
        DESCRIPTION = 16

        #: Exchange where last trade was executed
        LAST_ID = 17

        #: Day's Open Price
        OPEN_PRICE = 18

        #: Current Last-Prev Close
        NET_CHANGE = 19

        #: Current percent change
        FUTURE_PERCENT_CHANGE = 20

        #: Name of exchange
        EXCHANGE_NAME = 21

        #: Trading status of the symbol. Indicates a symbol's current trading
        #: status, Normal, Halted, Closed.
        SECURITY_STATUS = 22

        #: The total number of futures ontracts that are not closed or delivered
        #: on a particular day
        OPEN_INTEREST = 23

        #: Mark-to-Market value is calculated daily using current prices to
        #: determine profit/loss
        MARK = 24

        #: Minimum price movement
        TICK = 25

        #: Minimum amount that the price of the market can change
        TICK_AMOUNT = 26

        #: Futures product
        PRODUCT = 27

        #: Display in fraction or decimal format.
        FUTURE_PRICE_FORMAT = 28

        #: Trading hours. Notes:
        #:
        #:  * days: 0 = monday-friday, 1 = sunday.
        #:  * 7 = Saturday
        #:  * 0 = [-2000,1700] ==> open, close
        #:  * 1 = [-1530,-1630,-1700,1515] ==> open, close, open, close
        #:  * 0 = [-1800,1700,d,-1700,1900] ==> open, close, DST-flag, open, close
        #:  * If the DST-flag is present, the following hours are for DST days:
        #:    http://www.cmegroup.com/trading_hours/
        FUTURE_TRADING_HOURS = 29

        #: Flag to indicate if this future contract is tradable
        FUTURE_IS_TRADEABLE = 30

        #: Point value
        FUTURE_MULTIPLIER = 31

        #: Indicates if this contract is active
        FUTURE_IS_ACTIVE = 32

        #: Closing price
        FUTURE_SETTLEMENT_PRICE = 33

        #: Symbol of the active contract
        FUTURE_ACTIVE_SYMBOL = 34

        #: Expiration date of this contract in milliseconds since epoch
        FUTURE_EXPIRATION_DATE = 35
