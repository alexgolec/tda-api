from . import auth
from . import client
from . import orders
from .version import version as __version__


def __python_version_supports_streaming():
    import sys
    version_info = sys.version_info
    return version_info.major >= 3 and version_info.minor >= 8


if __python_version_supports_streaming():
    from . import streaming
else:
    import sys
    print('python version < 3.8.0, streaming API will not be available',
          file=sys.stderr)
