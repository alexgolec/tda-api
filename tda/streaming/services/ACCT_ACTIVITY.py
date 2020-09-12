from .base import _BaseService
from .fields import _BaseFieldEnum

class ACCT_ACTIVITY(_BaseService): 
    implemented = False
    class Fields(_BaseFieldEnum):
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
