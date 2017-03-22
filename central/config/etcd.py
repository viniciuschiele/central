"""
etcd config implementation.
"""

from ..compat import string_types
from ..exceptions import LibraryRequiredError
from ..structures import IgnoreCaseDict
from .core import BaseDataConfig

try:
    import etcd
except:
    etcd = None


__all__ = [
    'EtcdConfig',
]


class EtcdConfig(BaseDataConfig):
    """
    A etcd configuration based on `BaseDataConfig`.

    This implementation requires the path to the etcd directory that contains
    nodes that represent each configuration property. Sub nodes are not read.

    An example etcd configuration path is /appname/config
    An example etcd property node path is /appname/config/database.host

    When a property is updated via etcd a callback will be notified and the value managed
    by EtcdConfig will be updated.

    The library python-etcd must be installed.

    Example usage:

    .. code-block:: python

        import etcd

        from central.config.etcd import EtcdConfig

        client = etcd.Client()

        config = EtcdConfig(client, '/appname/config')
        config.load()

        value = config.get('database.host')

    :param etcd.Client client: The etcd client.
    :param str path: The path to the etcd directory that contains nodes.
    """
    def __init__(self, client, path):
        if etcd is None:
            raise LibraryRequiredError('python-etcd', 'https://pypi.python.org/pypi/python-etcd')

        super(EtcdConfig, self).__init__()

        if client is None:
            raise TypeError('client cannot be None')

        if not isinstance(path, string_types):
            raise TypeError('path must be a str')

        self._client = client
        self._path = path

    @property
    def client(self):
        """
        Get the etcd client.
        :return str: The etcd client.
        """
        return self._client

    @property
    def path(self):
        """
        Get the path to the etcd directory that contains nodes.
        :return str: The path to the etcd directory that contains nodes.
        """
        return self._path

    def load(self):
        """
        Read the configuration stored in the etcd.
        """
        result = self._client.read(self._path)

        data = IgnoreCaseDict()

        for item in result.leaves:
            # sub nodes are ignored
            if item.dir:
                continue

            # strips off the path from the key.
            index = item.key.rfind('/') + 1

            key = item.key[index:].replace('/', '.')
            value = item.value

            data[key] = value

        self._data = data
