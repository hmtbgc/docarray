__version__ = '0.13.1'

import os

from .document import Document
from .array import DocumentArray
from .dataclasses import dataclass, field

if 'DA_NO_RICH_HANDLER' not in os.environ:
    from rich.traceback import install

    install()

if 'NO_VERSION_CHECK' not in os.environ:
    from .helper import is_latest_version

    is_latest_version()
