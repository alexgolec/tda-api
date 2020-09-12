from .base import _BaseService
from .fields import _BaseFieldEnum

class OPTION(_BaseService):
    class Fields(_BaseFieldEnum):
        '''
        `Official documentation <https://developer.tdameritrade.com/content/
        streaming-data#_Toc504640601>`__
        '''

        #: Ticker symbol in upper case. Represented in the stream as the
        #: ``key`` field.
        SYMBOL = 0

        #: A company, index or fund name
        DESCRIPTION = 1

        #: Current Best Bid Price
        BID_PRICE = 2

        #: Current Best Ask Price
        ASK_PRICE = 3

        #: Price at which the last trade was matched
        LAST_PRICE = 4

        #: Day’s high trade price. Notes:
        #:
        #:  * According to industry standard, only regular session trades set
        #:    the High and Low.
        #:  * If an option does not trade in the AM session, high and low will
        #:    be zero.
        #:  * High/low reset to 0 at 7:28am ET.
        HIGH_PRICE = 5

        #: Day’s low trade price. Same notes as ``HIGH_PRICE``.
        LOW_PRICE = 6

        #: Previous day’s closing price. Closing prices are updated from the
        #: DB when Pre-Market tasks are run at 7:29AM ET.
        CLOSE_PRICE = 7

        #: Aggregated shares traded throughout the day, including pre/post
        #: market hours. Reset to zero at 7:28am ET.
        TOTAL_VOLUME = 8

        #: Open interest
        OPEN_INTEREST = 9

        #: Option Risk/Volatility Measurement. Volatility is reset to 0 when
        #: Pre-Market tasks are run at 7:28 AM ET.
        VOLATILITY = 10

        #: Trade time of the last quote in seconds since midnight EST
        QUOTE_TIME = 11

        #: Trade time of the last quote in seconds since midnight EST
        TRADE_TIME = 12

        #: Money intrinsic value
        MONEY_INTRINSIC_VALUE = 13

        #: Day of the quote
        QUOTE_DAY = 14

        #: Day of the trade
        TRADE_DAY = 15

        #: Option expiration year
        EXPIRATION_YEAR = 16

        #: Option multiplier
        MULTIPLIER = 17

        #: Valid decimal points. 4 digits for AMEX, NASDAQ, OTCBB, and PINKS,
        #: 2 for others.
        DIGITS = 18

        #: Day's Open Price. Notes:
        #:
        #:  * Open is set to ZERO when Pre-Market tasks are run at 7:28.
        #:  * If a stock doesn’t trade the whole day, then the open price is 0.
        #:  * In the AM session, Open is blank because the AM session trades do
        #:    not set the open.
        OPEN_PRICE = 19

        #: Number of shares for bid
        BID_SIZE = 20

        #: Number of shares for ask
        ASK_SIZE = 21

        #: Number of shares traded with last trade, in 100's
        LAST_SIZE = 22

        #: Current Last-Prev Close
        NET_CHANGE = 23
        STRIKE_PRICE = 24
        CONTRACT_TYPE = 25
        UNDERLYING = 26
        EXPIRATION_MONTH = 27
        DELIVERABLES = 28
        TIME_VALUE = 29
        EXPIRATION_DAY = 30
        DAYS_TO_EXPIRATION = 31
        DELTA = 32
        GAMMA = 33
        THETA = 34
        VEGA = 35
        RHO = 36

        #: Indicates a symbols current trading status, Normal, Halted, Closed
        SECURITY_STATUS = 37
        THEORETICAL_OPTION_VALUE = 38
        UNDERLYING_PRICE = 39
        UV_EXPIRATION_TYPE = 40

        #: Mark Price
        MARK = 41
