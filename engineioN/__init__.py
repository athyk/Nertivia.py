import sys

from .client import Client

if sys.version_info >= (3, 5):  # pragma: no cover
    from .asyncio_client import AsyncClient

    try:
        from .async_drivers.tornado import get_tornado_handler
    except ImportError:
        get_tornado_handler = None
else:  # pragma: no cover
    AsyncServer = None
    AsyncClient = None
    get_tornado_handler = None
    ASGIApp = None

__version__ = '3.14.2'

__all__ = ['__version__', 'Client']
