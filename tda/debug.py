import sys
import tda


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
    if resp.ok:
        register_redactions(resp.json())


def register_redactions(obj, key_path=None,
                        bad_patterns=[
                            'auth', 'acl', 'displayname', 'id', 'key', 'token'],
                        whitelisted=set([
                            'requestid',
                            'token_type'])):
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


def enable_bug_report_logging(output=sys.stderr, loggers=None):
    '''
    Turns on bug report logging. Will collect all logged output, redact out
    anything that should be kept secret, and emit the result at program exit.

    Notes:
     * This method does a **BEST EFFORT** redaction. Never share its output
       without verifying that all secret information is properly redacted.
     * Because this function records all logged output, it has a performance
       penalty. It should not be called in production code.

    :param output: File to which output will be written. Defaults to ``stderr``.
    :param loggers: List of loggers to register. Primarily available for
                    testing, so passing non-``None`` values is highly
                    discouraged.

    :return: Return value should be ignored.
    '''
    import atexit
    import logging

    if loggers is None:
        loggers = (
            tda.auth.get_logger(),
            tda.client.get_logger(),
            tda.streaming.get_logger())

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
        for msg in handler.messages:
            msg = tda.LOG_REDACTOR.redact(msg)
            print(msg, file=output)
    atexit.register(write_logs)

    return write_logs
