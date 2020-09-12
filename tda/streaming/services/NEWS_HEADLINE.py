from .base import _BaseService
from .fields import _BaseFieldEnum

class NEWS_HEADLINE(_BaseService):
    class Fields(_BaseFieldEnum):
        '''
        `Official documentation <https://developer.tdameritrade.com/content/
        streaming-data#_Toc504640626>`__
        '''

        #: Ticker symbol in upper case. Represented in the stream as the
        #: ``key`` field.
        SYMBOL = 0

        #: Specifies if there is any error
        ERROR_CODE = 1

        #: Headline’s datetime in milliseconds since epoch
        STORY_DATETIME = 2

        #: Unique ID for the headline
        HEADLINE_ID = 3
        STATUS = 4

        #: News headline
        HEADLINE = 5
        STORY_ID = 6
        COUNT_FOR_KEYWORD = 7
        KEYWORD_ARRAY = 8
        IS_HOT = 9
        STORY_SOURCE = 10
