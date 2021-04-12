import unittest

from tda.contrib.util import HeuristicJsonDecoder


class HeuristicJsonDecoderTest(unittest.TestCase):
    def test_raw_string_decodes(self):
        self.assertEqual(HeuristicJsonDecoder().decode_json_string(
            r'{"\\\\\\\\": "test"}'),
            {r'\\\\': 'test'})


    def test_replace_backslashes(self):
        # TODO: Actually collect some failing use cases...
        pass
