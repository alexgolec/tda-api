from .base import _BaseService
from .fields import _BaseFieldEnum

class QUOTE(_BaseService):
    class Fields(_BaseFieldEnum):
        '''
        `Official documentation <https://developer.tdameritrade.com/content/
        streaming-data#_Toc504640599>`__

        Fields for equity quotes.
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
        #: market hours. Note volume is set to zero at 7:28am ET.
        TOTAL_VOLUME = 8

        #: Number of shares traded with last trade, in 100's
        LAST_SIZE = 9

        #: Trade time of the last trade, in seconds since midnight EST
        TRADE_TIME = 10

        #: Trade time of the last quote, in seconds since midnight EST
        QUOTE_TIME = 11

        #: Day’s high trade price. Notes:
        #:
        #:  * According to industry standard, only regular session trades set
        #:    the High and Low.
        #:  * If a stock does not trade in the AM session, high and low will be
        #:    zero.
        #:  * High/low reset to 0 at 7:28am ET
        HIGH_PRICE = 12

        #: Day’s low trade price. Same notes as ``HIGH_PRICE``.
        LOW_PRICE = 13

        #: Indicates Up or Downtick (NASDAQ NMS & Small Cap). Updates whenever
        #: bid updates.
        BID_TICK = 14

        #: Previous day’s closing price. Notes:
        #:
        #:  * Closing prices are updated from the DB when Pre-Market tasks are
        #:    run by TD Ameritrade at 7:29AM ET.
        #:  * As long as the symbol is valid, this data is always present.
        #:  * This field is updated every time the closing prices are loaded
        #:    from DB
        CLOSE_PRICE = 15

        # TODO: Write a wrapper around this to make it easier to interpret.
        #: Primary "listing" Exchange.
        EXCHANGE_ID = 16

        #: Stock approved by the Federal Reserve and an investor's broker as
        #: being suitable for providing collateral for margin debt?
        MARGINABLE = 17

        #: Stock can be sold short?
        SHORTABLE = 18

        #: Deprecated, documented for completeness.
        ISLAND_BID_DEPRECATED = 19

        #: Deprecated, documented for completeness.
        ISLAND_ASK_DEPRECATED = 20

        #: Deprecated, documented for completeness.
        ISLAND_VOLUME_DEPRECATED = 21

        #: Day of the quote
        QUOTE_DAY = 22

        #: Day of the trade
        TRADE_DAY = 23

        #: Option Risk/Volatility Measurement. Notes:
        #:
        #:  * Volatility is reset to 0 when Pre-Market tasks are run at 7:28 AM
        #:    ET
        #:  * Once per day descriptions are loaded from the database when
        #:    Pre-Market tasks are run at 7:29:50 AM ET.
        VOLATILITY = 24

        #: A company, index or fund name
        DESCRIPTION = 25

        #: Exchange where last trade was executed
        LAST_ID = 26

        #: Valid decimal points. 4 digits for AMEX, NASDAQ, OTCBB, and PINKS,
        #: 2 for others.
        DIGITS = 27

        #: Day's Open Price. Notes:
        #:
        #:  * Open is set to ZERO when Pre-Market tasks are run at 7:28.
        #:  * If a stock doesn’t trade the whole day, then the open price is 0.
        #:  * In the AM session, Open is blank because the AM session trades do
        #:    not set the open.
        OPEN_PRICE = 28

        #: Current Last-Prev Close
        NET_CHANGE = 29

        #: Highest price traded in the past 12 months, or 52 weeks
        HIGH_52_WEEK = 30

        #: Lowest price traded in the past 12 months, or 52 weeks
        LOW_52_WEEK = 31

        #: Price to earnings ratio
        PE_RATIO = 32

        #: Dividen earnings Per Share
        DIVIDEND_AMOUNT = 33

        #: Dividend Yield
        DIVIDEND_YIELD = 34

        #: Deprecated, documented for completeness.
        ISLAND_BID_SIZE_DEPRECATED = 35

        #: Deprecated, documented for completeness.
        ISLAND_ASK_SIZE_DEPRECATED = 36

        #: Mutual Fund Net Asset Value
        NAV = 37

        #: Mutual fund price
        FUND_PRICE = 38

        #: Display name of exchange
        EXCHANGE_NAME = 39

        #: Dividend date
        DIVIDEND_DATE = 40

        #: Is last quote a regular quote
        IS_REGULAR_MARKET_QUOTE = 41

        #: Is last trade a regular trade
        IS_REGULAR_MARKET_TRADE = 42

        #: Last price, only used when ``IS_REGULAR_MARKET_TRADE`` is ``True``
        REGULAR_MARKET_LAST_PRICE = 43

        #: Last trade size, only used when ``IS_REGULAR_MARKET_TRADE`` is ``True``
        REGULAR_MARKET_LAST_SIZE = 44

        #: Last trade time, only used when ``IS_REGULAR_MARKET_TRADE`` is ``True``
        REGULAR_MARKET_TRADE_TIME = 45

        #: Last trade date, only used when ``IS_REGULAR_MARKET_TRADE`` is ``True``
        REGULAR_MARKET_TRADE_DAY = 46

        #: ``REGULAR_MARKET_LAST_PRICE`` minus ``CLOSE_PRICE``
        REGULAR_MARKET_NET_CHANGE = 47

        #: Indicates a symbols current trading status, Normal, Halted, Closed
        SECURITY_STATUS = 48

        #: Mark Price
        MARK = 49

        #: Last quote time in milliseconds since Epoch
        QUOTE_TIME_IN_LONG = 50

        #: Last trade time in milliseconds since Epoch
        TRADE_TIME_IN_LONG = 51

        #: Regular market trade time in milliseconds since Epoch
        REGULAR_MARKET_TRADE_TIME_IN_LONG = 52
