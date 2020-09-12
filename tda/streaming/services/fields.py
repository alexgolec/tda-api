from enum import Enum
import copy

class _BaseFieldEnum(Enum):
    @classmethod
    def all_fields(cls):
        return list(cls)

    @classmethod
    def key_mapping(cls):
        try:
            print(cls._key_mapping)
            return cls._key_mapping
        except AttributeError:
            cls._key_mapping = { str(enum.value):name for name, enum in cls.__members__.items() }
            return cls._key_mapping

    @classmethod
    def relabel_message(cls, msg):
        # Make a copy of the items so we can modify the dict during iteration
        new_msg = { cls.key_mapping().get(x,x):y for x,y in msg.items() }
        msg.clear()
        msg.update(new_msg)

##########################################################################
# Common book utilities

class BookFields(_BaseFieldEnum):
    SYMBOL = 0
    BOOK_TIME = 1
    BIDS = 2
    ASKS = 3

class BidFields(_BaseFieldEnum):
    BID_PRICE = 0
    TOTAL_VOLUME = 1
    NUM_BIDS = 2
    BIDS = 3

class PerExchangeBidFields(_BaseFieldEnum):
    EXCHANGE = 0
    BID_VOLUME = 1
    SEQUENCE = 2

class AskFields(_BaseFieldEnum):
    ASK_PRICE = 0
    TOTAL_VOLUME = 1
    NUM_ASKS = 2
    ASKS = 3

class PerExchangeAskFields(_BaseFieldEnum):
    EXCHANGE = 0
    ASK_VOLUME = 1
    SEQUENCE = 2

class AccountActivityFields(_BaseFieldEnum):
    '''
    `Official documentation <https://developer.tdameritrade.com/content/
    streaming-data#_Toc504640580>`__

    Dat.fields for equity account activity. Primarily an implementation detail
    and not used in client code. Provided here as documentation for key
    values stored returned in the stream messages.
    '''

    #: Subscription key. Represented in the stream as the
    #: ``key`` field.
    SUBSCRIPTION_KEY = 0

    #: Account # subscribed
    ACCOUNT = 1

    #: Refer to the `message type table in the official documentation
    #: <https://developer.tdameritrade.com/content/streaming-data
    #: #_Toc504640581>`__
    MESSAGE_TYPE = 2

    #: The core data for the message.  Either XML Message data describing
    #: the update, ``NULL`` in some cases, or plain text in case of
    #: ``ERROR``.
    MESSAGE_DATA = 3

#########################################################################
# Common Timesale utilities

class TimesaleFields(_BaseFieldEnum):
    '''
    `Official documentation <https://developer.tdameritrade.com/content/
    streaming-data#_Toc504640626>`__
    '''

    #: Ticker symbol in upper case. Represented in the stream as the
    #: ``key`` field.
    SYMBOL = 0

    #: Trade time of the last trade in milliseconds since epoch
    TRADE_TIME = 1

    #: Price at which the last trade was matched
    LAST_PRICE = 2

    #: Number of shares traded with last trade
    LAST_SIZE = 3

    #: Number of shares for bid
    LAST_SEQUENCE = 4
