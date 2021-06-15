import sys

from .client import Client
from .namespace import Namespace, ClientNamespace

if sys.version_info >= (3, 5):  # pragma: no cover
    from .asyncio_client import AsyncClient
    from .asyncio_namespace import AsyncNamespace, AsyncClientNamespace
else:  # pragma: no cover
    AsyncClient = None
    AsyncServer = None
    AsyncManager = None
    AsyncNamespace = None
    AsyncRedisManager = None
    AsyncAioPikaManager = None

__version__ = '4.6.1'

__all__ = ['__version__', 'Client',
           'Namespace', 'ClientNamespace']
