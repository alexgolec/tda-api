from abc import ABC, abstractmethod
import json


class StreamJsonParser(ABC):
    @abstractmethod
    def parse_json_string(self, raw):
        '''
        Parse a JSON-formatted string into a proper object. Raises 
        ``JSONDecodeError`` on parse failure.
        '''
        raise NotImplementedError()


class NaiveJsonStreamParser(StreamJsonParser):
    def parse_json_string(self, raw):
        return json.loads(raw)
