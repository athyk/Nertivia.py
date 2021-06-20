import sys

from .client import Client
if sys.version_info >= (3, 5):  # pragma: no cover
    from .asyncio_client import AsyncClient
else:  # pragma: no cover
    AsyncClient = None

__version__ = '4.2.0'

__all__ = ['__version__', 'Client']
