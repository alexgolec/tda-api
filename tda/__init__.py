from . import auth
from . import client
from . import orders
from . import streaming

from .version import version as __version__

def enable_bug_report_logging():
    import atexit
    import logging
    import logging.handlers
    import queue

    formatter = logging.Formatter(
            '[%(filename)s:%(lineno)s:%(funcName)s] %(message)s')

    messages = queue.Queue()

    for m in (auth, client, streaming):
        logger = m.get_logger()
        logger.setLevel(logging.DEBUG)

        handler = logging.handlers.QueueHandler(messages)
        handler.setFormatter(formatter)

        logger.addHandler(handler)
