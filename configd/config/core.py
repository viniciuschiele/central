"""
Core config implementations.
"""

import codecs
import logging
import os
import sys

from copy import deepcopy
from threading import Lock
from urllib import request
from .. import abc
from ..decoders import DefaultDecoder
from ..exceptions import ConfigError
from ..interpolators import DefaultInterpolator
from ..readers import get_reader
from ..utils import event, iofile, merger


__all__ = [
    'BaseDataConfig', 'CommandLineConfig', 'CompositeConfig', 'EnvironmentConfig',
    'FileConfig', 'MemoryConfig', 'MemoryConfig', 'PollingConfig', 'UrlConfig'
]


logger = logging.getLogger(__name__)


class BaseDataConfig(abc.Config):
    """
    Base config class for implementing an `abc.Config`.
    """

    nested_delimiter = '.'

    def __init__(self):
        super(BaseDataConfig, self).__init__()
        self._data = {}
        self._decoder = DefaultDecoder()
        self._interpolator = DefaultInterpolator()
        self._updated = event.EventHandler(self)
        self._parent = None

    @property
    def decoder(self):
        """
        Get the decoder.
        :return abc.Decoder: The decoder.
        """
        return self._decoder

    @decoder.setter
    def decoder(self, value):
        """
        Set the decoder.
        :param abc.Decoder value: The decoder.
        """
        if value is None or not isinstance(value, abc.Decoder):
            raise TypeError('decoder must be an abc.Decoder')

        self._decoder = value

    @property
    def interpolator(self):
        """
        Get the interpolator.
        :return abc.Interpolator: The interpolator.
        """
        return self._interpolator

    @interpolator.setter
    def interpolator(self, value):
        """
        Set the interpolator.
        :param abc.Interpolator value: The interpolator.
        """
        if value is None or not isinstance(value, abc.Interpolator):
            raise TypeError('interpolator must be an abc.Interpolator')

        self._interpolator = value

    @property
    def parent(self):
        """
        Get the parent configuration.
        :return abc.Config: The parent or None if no parent.
        """
        return self._parent

    @parent.setter
    def parent(self, value):
        """
        Set the parent configuration.
        :param abc.Config value: The parent.
        """
        if value is not None and not isinstance(value, abc.Config):
            raise TypeError('parent must be an abc.Config')

        self._parent = value

    @property
    def updated(self):
        """
        Get the updated event handler.
        :return event.EventHandler: The event handler.
        """
        return self._updated

    def get(self, key, default=None, cast=None):
        """
        Get the value for given key if key is in the configuration, otherwise default.
        It can access a nested field by passing a . delimited path of keys and
        the interpolator is used to resolve variables.

        Example usage:

        .. code-block:: python

            from configd.config import MemoryConfig

            config = MemoryConfig(data={'host': {'address': 'localhost'}})
            address = config.get('host.address')

        :param str key: The key to be found.
        :param default: The default value if the key is not found.
        :param cast: The data type to convert the value to.
        :return: The value found, otherwise default.
        """
        if key is None or not isinstance(key, str):
            raise TypeError('key must be a str')

        value = self._find_value(key)

        if value is None:
            return default

        if isinstance(value, str):
            value = self._interpolator.resolve(value, self)

        if cast is None:
            return value

        return self._decoder.decode(value, cast)

    def _find_value(self, key):
        """
        Find the given key considering the nested delimiter as nested key.
        :param key: The key to be found.
        :return: The value found, otherwise None.
        """
        value = self._data.get(key)

        if value is not None:
            return value

        paths = key.split(self.nested_delimiter)

        if key == paths[0]:
            return None

        value = self._data.get(paths[0])

        for i in range(1, len(paths)):
            if value is None:
                break

            if not isinstance(value, dict):
                value = None
                break

            value = value.get(paths[i])

        return value


class CommandLineConfig(BaseDataConfig):
    """
    A command line based on `BaseDataConfig`.

    Example usage:

    .. code-block:: python

        from configd.config import CommandLineConfig

        config = CommandLineConfig()
        config.load()

        value = config.get('key1')

    """

    def load(self):
        """
        Loads the configuration data from the command line args.
        """
        data = {}

        for pair in sys.argv:
            kv = pair.split('=')

            if len(kv) != 2:
                continue

            key = kv[0].strip()

            if key == '':
                continue

            value = kv[1].strip()

            data[key] = value

        self._data = data


class CompositeConfig(abc.CompositeConfig):
    """
    Config that is a composite of multiple configuration and as such does not track
    properties of its own.

    The composite does not merge the configurations but instead
    treats them as overrides so that a property existing in a configuration supersedes
    the same property in configuration that was added previously.

    Example usage:

    .. code-block:: python

        from configd.config import CompositeConfig, CommandLineConfig, EnvironmentConfig

        config = CompositeConfig()
        config.add_config('cmd', CommandLineConfig())
        config.add_config('env', EnvironmentConfig())

        value = config.get('key1')

    :param bool load_on_add: True to auto load child on addition.
    """

    def __init__(self, load_on_add=False):
        super(CompositeConfig, self).__init__()

        if load_on_add is None or not isinstance(load_on_add, bool):
            raise TypeError('load_on_add must be a bool')

        self._load_on_add = load_on_add
        self._config_list = []
        self._config_dict = {}
        self._updated = event.EventHandler(self)
        self._parent = None

    @property
    def load_on_add(self):
        """
        Get the load on add.
        :return bool: True to load child on addition.
        """
        return self._load_on_add

    @property
    def parent(self):
        """
        Get the parent configuration.
        :return abc.Config: The parent or None if no parent.
        """
        return self._parent

    @parent.setter
    def parent(self, value):
        """
        Set the parent configuration.
        :param abc.Config value: The parent.
        """
        if value is not None and not isinstance(value, abc.Config):
            raise TypeError('parent must be an abc.Config')

        self._parent = value

    @property
    def updated(self):
        """
        Get the updated event handler.
        :return event.EventHandler: The event handler.
        """
        return self._updated

    def add_config(self, name, config):
        """
        Add a named configuration.
        The newly added configuration takes precedence over all previously added configurations.
        Duplicate configurations are not allowed.
        :param str name: The name of the configuration.
        :param abc.Config config: The configuration.
        """
        if name is None or not isinstance(name, str):
            raise TypeError('name must be a str')

        if config is None or not isinstance(config, abc.Config):
            raise TypeError('config must be an abc.Config')

        if name in self._config_dict:
            raise ConfigError('Configuration with name %s already exists' % name)

        if config.parent is not None:
            raise ConfigError('Configuration with name %s has already a parent' % name)

        config.parent = self

        self._config_dict[name] = config

        self._config_list.insert(0, config)

        if self._load_on_add:
            config.load()

        config.updated.add(self._config_updated)

    def get_config(self, name):
        """
        Get a configuration by name.
        :param str name: The name of the configuration.
        :return abc.Config: The configuration found or None.
        """
        if name is None or not isinstance(name, str):
            raise TypeError('name must be a str')

        return self._config_dict.get(name)

    def get_config_names(self):
        """
        Get the names of all configurations previously added.
        :return list: The list of configuration names.
        """
        return list(self._config_dict.keys())

    def remove_config(self, name):
        """
        Remove a configuration by name.
        :param str name: The name of the configuration
        :return abc.Config: The configuration removed or None if not found.
        """
        if name is None or not isinstance(name, str):
            raise TypeError('name must be a str')

        config = self._config_dict.pop(name, None)
        if config is None:
            return None

        self._config_list.remove(config)

        config.updated.remove(self._config_updated)

        config.parent = None

        return config

    def get(self, key, default=None, cast=None):
        """
        Get the value for given key if key is in the configuration, otherwise default.
        It will go through every child to find the given key.
        :param str key: The key to be found.
        :param default: The default value if the key is not found.
        :param cast: The data type to convert the value to.
        :return: The value found, otherwise default.
        """
        if key is None or not isinstance(key, str):
            raise TypeError('key must be a str')

        for config in self._config_list:
            value = config.get(key, cast=cast)
            if value is not None:
                return value

        return default

    def load(self):
        """
        Load all the children configuration.
        This method does not trigger the updated event.
        """
        for config in self._config_list:
            config.load()

    def _config_updated(self, config):
        """
        Raised by updated event from the children.
        It is not intended to be called directly.
        :param config: The config that triggered the event.
        """
        self.updated()


class EnvironmentConfig(BaseDataConfig):
    """
    An environment variable configuration based on `BaseDataConfig`.

    Example usage:

    .. code-block:: python

        from configd.config import EnvironmentConfig

        config = EnvironmentConfig()
        config.load()

        value = config.get('key1')

    """

    def load(self):
        """
        Load the environment variables.
        """
        data = {}

        for key in os.environ.keys():
            data[key] = os.environ[key]

        self._data = data


class FileConfig(BaseDataConfig):
    """
    A file configuration based on `BaseDataConfig`.

    Example usage:

    .. code-block:: python

        from configd.config import FileConfig

        config = FileConfig('config.json')
        config.load()

        value = config.get('key')

    :param str filename: The filename to be read.
    :param abc.Reader reader: The reader used to read the file content as a dict,
        if None a reader based on the filename is going to be used.
    """

    def __init__(self, filename, reader=None):
        super(FileConfig, self).__init__()
        if filename is None or not isinstance(filename, str):
            raise TypeError('filename must be a str')

        if reader is not None and not isinstance(reader, abc.Reader):
            raise TypeError('reader must be an abc.Reader')

        self._filename = filename
        self._reader = reader

    @property
    def filename(self):
        """
        Get the filename.
        :return str: The filename.
        """
        return self._filename

    def load(self):
        """
        Load the resource.
        """
        data = {}

        self._read(self._filename, data)

        self._data = data

    def _read(self, filename, data):
        """
        Read a given filename and merge its content with the given data.
        Recursively load any file referenced by an @next property in the response.

        :param str filename: The filename to be read.
        :param dict data: The data to merged on.
        """
        reader = self._reader

        if not reader:
            reader = self._get_reader(filename)

        with open(filename) as f:
            new_data = reader.read(f)

        next_filename = new_data.pop('@next', None)

        merger.merge_properties(data, new_data)

        if next_filename:
            if not isinstance(next_filename, str):
                raise ConfigError('@next must be a str')

            next_filename = self._interpolator.resolve(next_filename, self)
            self._read(next_filename, data)

    def _get_reader(self, filename):
        """
        Get an appropriated reader based on the filename,
        if not found an `ConfigError` is raised.
        :param str filename: The filename used to guess the appropriated reader.
        :return abc.Reader: A reader.
        """
        extension = iofile.get_file_ext(filename)

        if not extension:
            raise ConfigError('File %s is not supported' % filename)

        reader_cls = get_reader(extension)

        if reader_cls is None:
            raise ConfigError('File %s is not supported' % filename)

        return reader_cls()


class MemoryConfig(BaseDataConfig):
    """
    In-memory implementation of `BaseDataConfig`.

    Example usage:

    .. code-block:: python

        from configd.config import MemoryConfig

        config = MemoryConfig(data={'key': 'value'})

        value = config.get('key')

        config.set('other key', 'other value')

        value = config.get('other key')

    :param dict data: The initial data.
    """

    def __init__(self, data=None):
        super(MemoryConfig, self).__init__()

        if data is not None:
            if not isinstance(data, dict):
                raise TypeError('data must be a dict')

            self._data = deepcopy(data)

    def set(self, key, value):
        """
        Set a value for the given key.
        The updated event is triggered.
        :param str key: The key.
        :param value: The value.
        """
        if key is None or not isinstance(key, str):
            raise TypeError('key must be a str')

        self._data[key] = value
        self.updated()

    def load(self):
        """
        Do nothing.
        """


class PollingConfig(CompositeConfig):
    """
    An polling config that loads the configuration from its children
    from time to time, it is scheduled by a scheduler.

    Example usage:

    .. code-block:: python

        from configd.config import PollingConfig, FileConfig
        from configd.schedulers import FixedIntervalScheduler

        config = PollingConfig(FixedIntervalScheduler())
        config.add_config('json', FileConfig('config.json'))
        config.load()

        value = config.get('key')

    :param abc.Scheduler scheduler: The scheduler used to reload the configuration from the children.
    """
    def __init__(self, scheduler):
        super(PollingConfig, self).__init__()

        if scheduler is None or not isinstance(scheduler, abc.Scheduler):
            raise TypeError('scheduler must be an abc.Scheduler')

        self._scheduler = scheduler
        self._loaded = False
        self._reload_lock = Lock()

    @property
    def scheduler(self):
        """
        Get the scheduler.
        :return abc.Scheduler: The scheduler.
        """
        return self._scheduler

    def load(self):
        """
        Load all the children configuration and start the scheduler
        to reload the configuration from time to time.
        This method does not trigger the updated event.
        """
        super(PollingConfig, self).load()

        if not self._loaded:
            self._scheduler.schedule(self._reload)
            self._loaded = True

    def _reload(self):
        """
        Reload the children configuration and trigger the updated event.
        It is intended to be called by the scheduler.
        """
        if self._reload_lock.acquire(blocking=False):
            try:
                for config in self._config_list:
                    try:
                        config.load()
                    except:
                        logger.warning('Error loading config from ' + str(config), exc_info=True)

                try:
                    self.updated()
                except:
                    logger.warning('Error notifying updated config', exc_info=True)
            finally:
                self._reload_lock.release()


class UrlConfig(BaseDataConfig):
    """
    A url configuration based on `BaseDataConfig`.

    Example usage:

    .. code-block:: python

        from configd.config import UrlConfig

        config = UrlConfig('http://date.jsontest.com/')
        config.load()

        value = config.get('time')

    :param str url: The url to be read.
    :param abc.Reader reader: The reader used to read the response from url as a dict,
        if None a reader based on the content type of the response is going to be used.
    """
    def __init__(self, url, reader=None):
        super(UrlConfig, self).__init__()

        if url is None or not isinstance(url, str):
            raise TypeError('url must be a str')

        if reader and not isinstance(reader, abc.Reader):
            raise TypeError('reader must be an abc.Reader')

        self._url = url
        self._reader = reader

    @property
    def url(self):
        """
        Get the url.
        :return str: The url.
        """
        return self._url

    def load(self):
        """
        Load the configuration from the url.
        """
        data = {}

        self._read(self._url, data)

        self._data = data

    def _read(self, url, data):
        """
        Read a given url and merge the response with the given data.
        Recursively load any url referenced by an @next property in the response.

        :param str url: The url to be read.
        :param dict data: The data to merged on.
        """
        with request.urlopen(url) as response:
            content_type = response.headers.get('content-type')
            encoding = self._get_encoding(content_type)

            reader = self._reader
            if reader is None:
                reader = self._get_reader(url, content_type)

            text_reader_cls = codecs.getreader(encoding)

            with text_reader_cls(response) as text_reader:
                new_data = reader.read(text_reader)

        next_url = new_data.pop('@next', None)

        merger.merge_properties(data, new_data)

        if next_url:
            if not isinstance(next_url, str):
                raise ConfigError('@next must be a str')

            next_url = self._interpolator.resolve(next_url, self)
            self._read(next_url, data)

    def _get_reader(self, url, content_type):
        """
        Get an appropriated reader based on the url and the content type,
        if not found an `ConfigError` is raised.
        :param str url: The url used to guess the appropriated reader.
        :param str content_type: The content type used to guess the appropriated reader.
        :return abc.Reader: A reader.
        """
        names = []

        if content_type:
            # it handles those formats for content type.
            # text/vnd.yaml
            # text/yaml
            # text/x-yaml

            if ';' in content_type:
                content_type = content_type.split(';')[0]

            if '.' in content_type:
                names.append(content_type.split('.')[-1])
            elif '-' in content_type:
                names.append(content_type.split('-')[-1])
            elif '/' in content_type:
                names.append(content_type.split('/')[-1])

        # it handles a url with file extension.
        # http://example.com/config.json
        path = url.strip().rstrip('/')

        i = path.rfind('/')

        if i > 10:  # > http:// https://
            path = path[i:]

            if '.' in path:
                names.append(path.split('.')[-1])

        for name in names:
            reader_cls = get_reader(name)
            if reader_cls:
                return reader_cls()

        raise ConfigError('Response from %s provided content type %s which is not supported' % (url, content_type))

    def _get_encoding(self, content_type, default='utf-8'):
        """
        Get the encoding from the given content type.
        :param str content_type: The content type from the response.
        :param str default: The default content type.
        :return str: The encoding.
        """
        if not content_type:
            return default

        # e.g: application/json;charset=iso-8859-x

        pairs = content_type.split(';')

        # skip the mime type
        for pair in pairs[1:]:
            kv = pair.split('=')
            if len(kv) != 2:
                continue

            key = kv[0].strip()
            value = kv[1].strip()

            if key == 'charset' and value:
                return value

        return default
