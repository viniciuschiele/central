"""
etcd config implementation.
"""

import logging

from threading import Event, Thread
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


logger = logging.getLogger(__name__)


class EtcdConfig(BaseDataConfig):
    """
    A etcd configuration based on `BaseDataConfig`.

    This implementation requires the path to the etcd directory that contains
    nodes that represent each configuration property.

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
        self._etcd_index = None
        self._watching = False
        self._closed = Event()

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

    @property
    def path(self):
        """
        Get the path to the etcd directory that contains nodes.
        :return str: The path to the etcd directory that contains nodes.
        """
        return self._path

    def close(self):
        """
        Stop watching the path for changes.
        """
        self._closed.set()

    def load(self):
        """
        Read the configuration stored in the etcd.
        """
        data = IgnoreCaseDict()

        result = self._client.read(self._path, recursive=True)

        for item in result.leaves:
            # directories are ignored
            if item.dir:
                continue

            # strips off the path from the key.
            key = self._transform_key(item.key)
            value = item.value

            data[key] = value

        self._etcd_index = result.etcd_index + 1
        self._data = data

        if not self._watching:
            thread = Thread(target=self._watch, name='EtcdConfig')
            thread.daemon = True
            thread.start()

            self._watching = True

    def _transform_key(self, key):
        """
        Strip off the from the key.
        :param str key: The key from etcd.
        :return str: The key without the base path.
        """
        return key.lstrip(self._path).lstrip('/').replace('/', '.')

    def _watch(self):
        """
        Watch the path for changes.
        """
        while not self._closed.is_set():
            try:
                result = self._client.watch(self._path, index=self._etcd_index, recursive=True)

                for item in result.leaves:
                    # directories are ignored
                    if item.dir:
                        continue

                    key = self._transform_key(item.key)
                    value = item.value

                    if item.action == 'create':
                        self._data[key] = value

                    elif item.action == 'set':
                        self._data[key] = value

                    elif item.action == 'delete':
                        self._data.pop(key, None)

                    else:
                        logger.warning('Unrecognized etcd action %s ', item.action)

                self._etcd_index = result.modifiedIndex + 1

                try:
                    self.updated()
                except:
                    logger.warning('Error calling updated event from ' + str(self), exc_info=True)

            except etcd.EtcdWatchTimedOut:
                pass
            except:
                logger.exception('Etcd watch for path %s failed' % self._path)
