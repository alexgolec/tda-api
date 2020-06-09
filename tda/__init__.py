from . import auth
from . import client
from . import orders
from . import streaming

from .version import version as __version__

class LogRedactor:
    def __init__(self):
        from collections import defaultdict

        self.redacted_strings = {}
        self.labels = defaultdict(lambda: 1)

    def register(self, string, label):
        if string not in self.redacted_strings:
            self.redacted_strings[string] = '<REDACTED {} {}>'.format(
                    label, self.labels[label])
            self.labels[label] += 1

    def redact(self, msg):
        for string, label in self.redacted_strings.items():
            msg = msg.replace(string, label)
        return msg


LOG_REDACTOR = LogRedactor()


def enable_bug_report_logging():
    import atexit
    import logging

    class RecordingHandler(logging.Handler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.messages = []

        def emit(self, record):
            self.messages.append(self.format(record))

    handler = RecordingHandler()
    handler.setFormatter(logging.Formatter(
        '[%(filename)s:%(lineno)s:%(funcName)s] %(message)s'))

    for m in (auth, client, streaming):
        logger = m.get_logger()
        logger.setLevel(logging.DEBUG)
        logger.addHandler(handler)

    def write_logs():
        for msg in handler.messages:
            msg = LOG_REDACTOR.redact(msg)
            print(msg)
    atexit.register(write_logs)
