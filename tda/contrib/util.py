from abc import ABC, abstractmethod
import json


class StreamJsonDecoder(ABC):
    @abstractmethod
    def parse_json_string(self, raw):
        '''
        Parse a JSON-formatted string into a proper object. Raises 
        ``JSONDecodeError`` on parse failure.
        '''
        raise NotImplementedError()


class NaiveJsonStreamDecoder(StreamJsonDecoder):
    def parse_json_string(self, raw):
        return json.loads(raw)
