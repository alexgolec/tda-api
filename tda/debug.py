import tda


class LogRedactor:
    def __init__(self):
        from collections import defaultdict

        self.redacted_strings = {}
        self.labels = defaultdict(lambda: 1)

    def register(self, string, label):
        if string not in self.redacted_strings:
            self.redacted_strings[string] = '<REDACTED {}{}>'.format(
                label, '-{}'.format(self.labels[label]) if
                self.labels[label] > 1 else '')
            self.labels[label] += 1

    def redact(self, msg):
        for string, label in self.redacted_strings.items():
            msg = msg.replace(string, label)
        return msg


def register_redactions_from_response(resp):
    if resp.ok:
        register_redactions(resp.json())


def register_redactions(obj, key_path=None,
        bad_patterns=[
            'auth', 'acl', 'displayname', 'id', 'key', 'token'],
        whitelisted=set([
            'requestid'])):
    if key_path is None:
        key_path = []

    if isinstance(obj, list):
        for idx, value in enumerate(obj):
            key_path.append(str(idx))
            register_redactions(value, key_path)
            key_path.pop()
    elif isinstance(obj, dict):
        for key, value in obj.items():
            key_path.append(key)
            register_redactions(value, key_path)
            key_path.pop()
    else:
        if key_path:
            last_key = key_path[-1].lower()
            if last_key in whitelisted:
                return
            elif any(bad in last_key for bad in bad_patterns):
                tda.LOG_REDACTOR.register(obj, '-'.join(key_path))


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

    for m in (tda.auth, tda.client, tda.streaming):
        logger = m.get_logger()
        logger.setLevel(logging.DEBUG)
        logger.addHandler(handler)

    def write_logs():
        for msg in handler.messages:
            msg = tda.LOG_REDACTOR.redact(msg)
            print(msg)
    atexit.register(write_logs)
