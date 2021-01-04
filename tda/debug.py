import atexit
import logging
import sys
import tda

# This creates a tuple of JSONDecodeError types as a mechanism to catch multiple
# errors. This is needed because currently the `requests` library either uses
# the `simplejson` library or the builtin `json` library. This tuple-based
# approach makes it somewhat future-proof.
# Note: the `requests` is migrating to always use the builtin `json` library.
import json.decoder
try:
    import simplejson.errors
    __json_errors = (json.decoder.JSONDecodeError,
                     simplejson.errors.JSONDecodeError)
except ImportError:
    __json_errors = (json.decoder.JSONDecodeError,)


def get_logger():
    return logging.getLogger(__name__)


class LogRedactor:
    '''
    Collects strings that should not be emitted and replaces them with safe
    placeholders.
    '''

    def __init__(self):
        from collections import defaultdict

        self.redacted_strings = {}
        self.label_counts = defaultdict(int)

    def register(self, string, label):
        '''
        Registers a string that should not be emitted and the label with with
        which it should be replaced.
        '''
        string = str(string)
        if string not in self.redacted_strings:
            self.label_counts[label] += 1
            self.redacted_strings[string] = (label, self.label_counts[label])

    def redact(self, msg):
        '''
        Scans the string for secret strings and returns a sanitized version with
        the secrets replaced with placeholders.
        '''
        for string, label in self.redacted_strings.items():
            label, count = label
            msg = msg.replace(string, '<REDACTED {}{}>'.format(
                label, '-{}'.format(count) if
                self.label_counts[label] > 1 else ''))
        return msg


def register_redactions_from_response(resp):
    '''
    Convenience method that calls ``register_redactions`` if resp represents a
    successful response. Note this method assumes that resp has a JSON contents.
    '''
    if resp.status_code == 200:
        try:
            register_redactions(resp.json())
        except __json_errors:
            pass


def register_redactions(obj, key_path=None,
                        bad_patterns=[
                            'auth', 'acl', 'displayname', 'id', 'key', 'token'],
                        whitelisted=set([
                            'requestid',
                            'token_type',
                            'legid',
                            'bidid',
                            'askid',
                            'lastid',
                            'bidsizeinlong',
                            'bidsizeindouble',
                            'bidpriceindouble'])):
    '''
    Recursively iterates through the leaf elements of ``obj`` and registers
    elements with keys matching a blacklist with the global ``Redactor``.
    '''
    if key_path is None:
        key_path = []

    if isinstance(obj, list):
        for idx, value in enumerate(obj):
            key_path.append(str(idx))
            register_redactions(value, key_path, bad_patterns, whitelisted)
            key_path.pop()
    elif isinstance(obj, dict):
        for key, value in obj.items():
            key_path.append(key)
            register_redactions(value, key_path, bad_patterns, whitelisted)
            key_path.pop()
    else:
        if key_path:
            last_key = key_path[-1].lower()
            if last_key in whitelisted:
                return
            elif any(bad in last_key for bad in bad_patterns):
                tda.LOG_REDACTOR.register(obj, '-'.join(key_path))


def enable_bug_report_logging():
    '''
    Turns on bug report logging. Will collect all logged output, redact out
    anything that should be kept secret, and emit the result at program exit.

    Notes:
     * This method does a best effort redaction. Never share its output
       without verifying that all secret information is properly redacted.
     * Because this function records all logged output, it has a performance
       penalty. It should not be called in production code.
    '''
    _enable_bug_report_logging()


def _enable_bug_report_logging(output=sys.stderr, loggers=None):
    '''
    Module-internal version of :func:`enable_bug_report_logging`, intended for
    use in tests.
    '''
    if loggers is None:
        loggers = (
            tda.auth.get_logger(),
            tda.client.base.get_logger(),
            tda.streaming.get_logger(),
            get_logger())

    class RecordingHandler(logging.Handler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.messages = []

        def emit(self, record):
            self.messages.append(self.format(record))

    handler = RecordingHandler()
    handler.setFormatter(logging.Formatter(
        '[%(filename)s:%(lineno)s:%(funcName)s] %(message)s'))

    for logger in loggers:
        logger.setLevel(logging.DEBUG)
        logger.addHandler(handler)

    def write_logs():
        print(file=output)
        print(' ### BEGIN REDACTED LOGS ###', file=output)
        print(file=output)

        for msg in handler.messages:
            msg = tda.LOG_REDACTOR.redact(msg)
            print(msg, file=output)
    atexit.register(write_logs)

    get_logger().debug('tda-api version {}'.format(tda.__version__))

    return write_logs
