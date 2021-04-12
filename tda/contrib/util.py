import json
from tda.streaming import StreamJsonDecoder


class HeuristicJsonDecoder(StreamJsonDecoder):
    def decode_json_string(self, raw):
        '''
        Attempts the following, in order:
        
        1. Return the JSON decoding of the raw string. 
        2. Replace all instances of ``\\\\\\\\`` with ``\\\\`` and return the 
           decoding.

        Note alternative (and potentially expensive) transformations are only 
        performed when ``JSONDecodeError`` exceptions are raised by earlier 
        stages.
        '''

        try:
            return json.loads(raw)
        except json.decoder.JSONDecodeError:  # pragma: no cover
            raw = raw.replace('\\\\', '\\')

        return json.loads(raw)
