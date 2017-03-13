"""
Core config implementations.
"""

import codecs
import logging
import os
import sys

from collections import KeysView, ItemsView, ValuesView, Mapping
from copy import deepcopy
from .. import abc
from ..compat import text_type, string_types, urlopen
from ..decoders import Decoder
from ..exceptions import ConfigError
from ..interpolation import StrInterpolator, ConfigStrLookup
from ..readers import get_reader
from ..schedulers import FixedIntervalScheduler
from ..utils import Composer, EventHandler, get_file_ext


logger = logging.getLogger(__name__)


NESTED_DELIMITER = '.'


class BaseConfig(abc.Config):
    """
    Base config class for implementing an `abc.Config`.
    """

    def __init__(self):
        self._lookup = ConfigStrLookup(self)
        self._updated = EventHandler()

    def get(self, key, default=None):
        """
        Get the value for given key if key is in the configuration, otherwise default.
        :param str key: The key to be found.
        :param default: The default value if the key is not found.
        :return: The value found, otherwise default.
        """
        return self.get_value(key, object, default)

    def get_bool(self, key, default=None):
        """
        Get the value for given key as a bool if key is in the configuration, otherwise None.
        :param str key: The key to be found.
        :param default: The default value if the key is not found.
        :return bool: The value found, otherwise default.
        """
        return self.get_value(key, bool, default=default)

    def get_dict(self, key, default=None):
        """
        Get the value for given key as a dict if key is in the configuration, otherwise None.
        :param str key: The key to be found.
        :param default: The default value if the key is not found.
        :return dict: The value found, otherwise default.
        """
        return self.get_value(key, dict, default=default)

    def get_int(self, key, default=None):
        """
        Get the value for given key as an int if key is in the configuration, otherwise None.
        :param str key: The key to be found.
        :param default: The default value if the key is not found.
        :return int: The value found, otherwise default.
        """
        return self.get_value(key, int, default=default)

    def get_float(self, key, default=None):
        """
        Get the value for given key as a float if key is in the configuration, otherwise None.
        :param str key: The key to be found.
        :param default: The default value if the key is not found.
        :return float: The value found, otherwise default.
        """
        return self.get_value(key, float, default=default)

    def get_list(self, key, default=None):
        """
        Get the value for given key as a list if key is in the configuration, otherwise None.
        :param str key: The key to be found.
        :param default: The default value if the key is not found.
        :return list: The value found, otherwise default.
        """
        return self.get_value(key, list, default=default)

    def get_str(self, key, default=None):
        """
        Get the value for given key as a str if key is in the configuration, otherwise None.
        :param str key: The key to be found.
        :param default: The default value if the key is not found.
        :return str: The value found, otherwise default.
        """
        return self.get_value(key, text_type, default=default)

    def keys(self):
        """
        Get all the keys of the configuration.
        :return tuple: The keys of the configuration.
        """
        return KeysView(self)

    def items(self):
        """
        Get all the items of the configuration (key/value pairs).
        :return tuple: The items of the configuration.
        """
        return ItemsView(self)

    def values(self):
        """
        Get all the values of the configuration.
        :return tuple: The values of the configuration.
        """
        return ValuesView(self)


    @property
    def lookup(self):
        """
        Get the lookup object used for interpolation.
        :return StrLookup: The lookup object.
        """
        return self._lookup

    @lookup.setter
    def lookup(self, value):
        """
        Set the lookup object used for interpolation.
        :param StrLookup value: The lookup object.
        """
        if value is None:
            self._lookup = ConfigStrLookup(self)
        elif isinstance(value, abc.StrLookup):
            self._lookup = value
        else:
            raise TypeError('lookup must be an abc.StrLookup')

        self._lookup_changed(self._lookup)

    @property
    def updated(self):
        """
        Get the updated event handler.
        :return EventHandler: The event handler.
        """
        return self._updated

    def on_updated(self, func):
        """
        Add a new callback for updated event.
        It can also be used as decorator.

        Example usage:

        .. code-block:: python

            from central.config import MemoryConfig

            config = MemoryConfig()

            @config.on_updated
            def config_updated():
                pass

        :param func: The callback.
        """
        self.updated.add(func)

    def prefixed(self, prefix):
        """
        Get a subset of the configuration prefixed by a key.

        Example usage:

        .. code-block:: python

            from central.config import MemoryConfig

            config = MemoryConfig().prefixed('database')

            host = config.get('host')

        :param str prefix: The prefix to prepend to the keys.
        :return abc.Config: The subset of the configuration prefixed by a key.
        """
        return PrefixedConfig(prefix, self)

    def reload_every(self, interval):
        """
        Get a reload configuration to reload the
        current configuration every interval given.
        :param int interval: The interval in milliseconds between loads.
        :return ReloadConfig: The reload config object.
        """
        return ReloadConfig(self, FixedIntervalScheduler(interval))

    def _lookup_changed(self, lookup):
        """
        Called when the lookup property is changed.
        :param lookup: The new lookup object.
        """
        pass

    def __contains__(self, key):
        """
        Get true if key is in the configuration, otherwise false.
        :param str key: The key to be checked.
        :return bool: true if key is in the configuration, false otherwise.
        """
        return self.get_raw(key) is not None

    def __getitem__(self, key):
        """
        Get the value if key is in the configuration, otherwise KeyError is raised.
        :param str key: The key to be found.
        :return: The value found.
        """
        value = self.get(key)

        if value is None:
            raise KeyError(key)

        return value


class BaseDataConfig(BaseConfig):
    """
    Base config class that holds keys.
    """

    def __init__(self):
        super(BaseDataConfig, self).__init__()
        self._data = {}
        self._decoder = Decoder.instance()
        self._interpolator = StrInterpolator()

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
        :return abc.StrInterpolator: The interpolator.
        """
        return self._interpolator

    @interpolator.setter
    def interpolator(self, value):
        """
        Set the interpolator.
        :param abc.StrInterpolator value: The interpolator.
        """
        if value is None or not isinstance(value, abc.StrInterpolator):
            raise TypeError('interpolator must be an abc.StrInterpolator')

        self._interpolator = value

    def get_raw(self, key):
        """
        Get the raw value for given key if key is in the configuration, otherwise None.
        Find the given key considering the nested delimiter as nested key.
        :param str key: The key to be found.
        :return: The value found, otherwise None.
        """
        value = self._data.get(key)

        if value is not None:
            return value

        paths = key.split(NESTED_DELIMITER)

        if key == paths[0]:
            return None

        value = self._data.get(paths[0])

        for i in range(1, len(paths)):
            if value is None:
                break

            if not isinstance(value, Mapping):
                value = None
                break

            value = value.get(paths[i])

        return value

    def get_value(self, key, type, default=None):
        """
        Get the value for given key as the specified type if key is in the configuration, otherwise default.
        It can access a nested field by passing a . delimited path of keys and
        the interpolator is used to resolve variables.
        :param str key: The key to be found.
        :param type: The data type to convert the value to.
        :param default: The default value if the key is not found.
        :return: The value found, otherwise default.
        """
        if key is None or not isinstance(key, string_types):
            raise TypeError('key must be a str')

        if type is None:
            raise ValueError('type cannot be None')

        value = self.get_raw(key)

        if value is None:
            return default

        if isinstance(value, string_types):
            value = self._interpolator.resolve(value, self._lookup)

        if type is object:
            return value

        return self._decoder.decode(value, type)

    def __iter__(self):
        """
        Get a new iterator object that can iterate over the keys of the configuration.
        :return: The iterator.
        """
        return iter(self._data)

    def __len__(self):
        """
        Get the number of keys.
        :return int: The number of keys.
        """
        return len(self._data)


class CommandLineConfig(BaseDataConfig):
    """
    A command line based on `BaseDataConfig`.

    Example usage:

    .. code-block:: python

        from central.config import CommandLineConfig

        config = CommandLineConfig()
        config.load()

        value = config.get('key1')

    """

    def load(self):
        """
        Loads the configuration data from the command line args.

        This method does not trigger the updated event.
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


class CompositeConfig(abc.CompositeConfig, BaseConfig):
    """
    Config that is a composite of multiple configuration and as such does not track
    properties of its own.

    The composite does not merge the configurations but instead
    treats them as overrides so that a property existing in a configuration supersedes
    the same property in configuration that was added previously.

    Example usage:

    .. code-block:: python

        from central.config import CompositeConfig, CommandLineConfig, EnvironmentConfig

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

    @property
    def load_on_add(self):
        """
        Get the load on add.
        :return bool: True to load child on addition.
        """
        return self._load_on_add

    def add_config(self, name, config):
        """
        Add a named configuration.
        The newly added configuration takes precedence over all previously added configurations.
        Duplicate configurations are not allowed.
        :param str name: The name of the configuration.
        :param abc.Config config: The configuration.
        """
        if name is None or not isinstance(name, string_types):
            raise TypeError('name must be a str')

        if config is None or not isinstance(config, abc.Config):
            raise TypeError('config must be an abc.Config')

        if name in self._config_dict:
            raise ConfigError('Configuration with name %s already exists' % name)

        self._config_dict[name] = config

        self._config_list.append(config)

        config.lookup = self._lookup

        config.updated.add(self._config_updated)

        if self._load_on_add:
            config.load()

    def get_config(self, name):
        """
        Get a configuration by name.
        :param str name: The name of the configuration.
        :return abc.Config: The configuration found or None.
        """
        if name is None or not isinstance(name, string_types):
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
        if name is None or not isinstance(name, string_types):
            raise TypeError('name must be a str')

        config = self._config_dict.pop(name, None)
        if config is None:
            return None

        self._config_list.remove(config)

        config.updated.remove(self._config_updated)

        config.lookup = None

        return config

    def get_raw(self, key):
        """
        Get the raw value for given key if key is in the configuration, otherwise None.
        It goes through every child to find the given key.
        :param str key: The key to be found.
        :return: The value found, otherwise None.
        """
        if key is None or not isinstance(key, string_types):
            raise TypeError('key must be a str')

        for config in reversed(self._config_list):
            value = config.get_raw(key)
            if value is not None:
                return value

        return None

    def get_value(self, key, type, default=None):
        """
        Get the value for given key as the specified type if key is in the configuration, otherwise default.
        It goes through every child to find the given key.
        :param str key: The key to be found.
        :param type: The data type to convert the value to.
        :param default: The default value if the key is not found.
        :return: The value found, otherwise default.
        """
        if key is None or not isinstance(key, string_types):
            raise TypeError('key must be a str')

        if type is None:
            raise ValueError('type cannot be None')

        for config in reversed(self._config_list):
            value = config.get_value(key, type)
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

    def _config_updated(self):
        """
        Called by updated event from the children.
        It is not intended to be called directly.
        """
        self.updated()

    def _lookup_changed(self, lookup):
        """
        Set the new lookup to the children.
        :param lookup: The new lookup object.
        """
        for config in self._config_list:
            config.lookup = lookup

    def __iter__(self):
        """
        Get a new iterator object that can iterate over the keys of the configuration.
        :return: The iterator.
        """
        s = set()

        for config in self._config_list:
            s.update(config.keys())

        return iter(s)

    def __len__(self):
        """
        Get the number of keys.
        :return int: The number of keys.
        """
        s = set()

        for config in self._config_list:
            s.update(config.keys())

        return len(s)


class EnvironmentConfig(BaseDataConfig):
    """
    An environment variable configuration based on `BaseDataConfig`.

    Example usage:

    .. code-block:: python

        from central.config import EnvironmentConfig

        config = EnvironmentConfig()
        config.load()

        value = config.get('key1')

    """

    def load(self):
        """
        Load the environment variables.

        This method does not trigger the updated event.
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

        from central.config import FileConfig

        config = FileConfig('config.json')
        config.load()

        value = config.get('key')

    :param str filename: The filename to be read.
    :param list|tuple paths: The list of path to locate the config file.
    :param abc.Reader reader: The reader used to read the file content as a dict,
        if None a reader based on the filename is going to be used.
    """

    def __init__(self, filename, paths=None, reader=None):
        super(FileConfig, self).__init__()
        if filename is None or not isinstance(filename, string_types):
            raise TypeError('filename must be a str')

        if paths is None:
            paths = ()
        elif isinstance(paths, (tuple, list)):
            paths = tuple(paths)
        else:
            raise TypeError('paths must be a tuple or list')

        if reader is not None and not isinstance(reader, abc.Reader):
            raise TypeError('reader must be an abc.Reader')

        self._filename = filename
        self._paths = paths
        self._reader = reader
        self._composer = Composer()

    @property
    def filename(self):
        """
        Get the filename.
        :return str: The filename.
        """
        return self._filename

    @property
    def paths(self):
        """
        Get the paths to locate the config file.
        :return tuple: The paths to locate the config file.
        """
        return self._paths

    @property
    def reader(self):
        """
        Get the reader.
        :return abc.Reader: The reader.
        """
        return self._reader

    def load(self):
        """
        Load the file content.

        This method does not trigger the updated event.
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
        fname = self._find_file(filename, self._paths)

        if fname is None:
            raise ConfigError('File %s not found' % filename)

        reader = self._reader or self._get_reader(fname)

        with self._read_file(fname) as stream:
            text_reader_cls = codecs.getreader('utf-8')

            with text_reader_cls(stream) as text_reader:
                new_data = reader.read(text_reader)

        next_filename = new_data.pop('@next', None)

        self._composer.compose(data, new_data)

        if next_filename:
            if not isinstance(next_filename, string_types):
                raise ConfigError('@next must be a str')

            self._read(next_filename, data)

    def _read_file(self, filename):
        """
        Open a stream for the given filename.
        :param str filename: The filename to be read.
        :return: The stream to read the file content.
        """
        return open(filename, mode='rb')

    def _find_file(self, filename, paths):
        """
        Search all the given paths for the given config file.
        Returns the first path that exists and is a config file.
        :param filename: The filename to be found.
        :param paths: The paths to be searched.
        :return: The first file found, otherwise None.
        """
        filenames = [os.path.join(path, filename) for path in paths]
        filenames.insert(0, filename)

        for filename in filenames:
            # resolve ~/ or any variable using the environment variables.
            filename = os.path.expanduser(os.path.expandvars(filename))

            # resolve any variable left using the interpolator.
            filename = self._interpolator.resolve(filename, self._lookup)

            if os.path.exists(filename):
                return filename

        return None

    def _get_reader(self, filename):
        """
        Get an appropriated reader based on the filename,
        if not found an `ConfigError` is raised.
        :param str filename: The filename used to guess the appropriated reader.
        :return abc.Reader: A reader.
        """
        extension = get_file_ext(filename)

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

        from central.config import MemoryConfig

        config = MemoryConfig(data={'key': 'value'})

        value = config.get('key')

        config.set('other key', 'other value')

        value = config.get('other key')

    :param dict data: The initial data.
    """

    def __init__(self, data=None):
        super(MemoryConfig, self).__init__()

        if data is not None:
            if not isinstance(data, Mapping):
                raise TypeError('data must be a dict')

            self._data = deepcopy(data)

    def set(self, key, value):
        """
        Set a value for the given key.
        The updated event is triggered.
        :param str key: The key.
        :param value: The value.
        """
        if key is None or not isinstance(key, string_types):
            raise TypeError('key must be a str')

        self._data[key] = value
        self.updated()

    def load(self):
        """
        Do nothing.
        """


class PrefixedConfig(BaseConfig):
    """
    A config implementation to view into another Config
    for keys starting with a specified prefix.

    Example usage:

    .. code-block:: python

        from central.config import PrefixedConfig, MemoryConfig

        config = MemoryConfig(data={'production.timeout': 10})

        prefixed = config.prefixed('production')

        value = prefixed.get('timeout')

    :param str prefix: The prefix to prepend to the keys.
    :param abc.Config config: The config to load the keys from.
    """
    def __init__(self, prefix, config):
        super(PrefixedConfig, self).__init__()

        if prefix is None or not isinstance(prefix, string_types):
            raise TypeError('prefix must be a str')

        if config is None or not isinstance(config, abc.Config):
            raise TypeError('config must be an abc.Config')

        self._prefix = prefix.rstrip(NESTED_DELIMITER)
        self._prefix_delimited = prefix if prefix.endswith(NESTED_DELIMITER) else prefix + NESTED_DELIMITER
        self._config = config
        self._config.lookup = self.lookup

    @property
    def config(self):
        """
        Get the config.
        :return abc.Config: The config.
        """
        return self._config

    @property
    def prefix(self):
        """
        Get the prefix.
        :return str: The prefix.
        """
        return self._prefix

    def get_raw(self, key):
        """
        Get the raw value for given key if key is in the configuration, otherwise None.
        :param str key: The key to be found.
        :return: The value found, otherwise default.
        """
        if key is None or not isinstance(key, string_types):
            raise TypeError('key must be a str')

        key = self._prefix_delimited + key

        return self._config.get_raw(key)

    def get_value(self, key, type, default=None):
        """
        Get the value for given key as the specified type if key is in the configuration, otherwise default.
        :param str key: The key to be found.
        :param type: The data type to convert the value to.
        :param default: The default value if the key is not found.
        :return: The value found, otherwise default.
        """
        if key is None or not isinstance(key, string_types):
            raise TypeError('key must be a str')

        key = self._prefix_delimited + key

        return self._config.get_value(key, type, default=default)

    def load(self):
        """
        Load the child configuration.

        This method does not trigger the updated event.
        """
        self._config.load()

    def _lookup_changed(self, lookup):
        """
        Set the new lookup to the child.
        :param lookup: The new lookup object.
        """
        self._config.lookup = lookup

    def __iter__(self):
        """
        Get a new iterator object that can iterate over the keys of the configuration.
        :return: The iterator.
        """
        keys = set()

        for key in self._config:
            if key == self._prefix:
                value = self._config.get(key)
                if value is not None and isinstance(value, Mapping):
                    keys.update(value.keys())

            elif key.startswith(self._prefix_delimited):
                keys.update((key[len(self._prefix_delimited):],))

        return iter(keys)

    def __len__(self):
        """
        Get the number of keys.
        :return int: The number of keys.
        """
        length = 0

        for key in self._config:
            if key == self._prefix:
                value = self._config.get(key)
                if value is not None and isinstance(value, Mapping):
                    length += len(value)

            elif key.startswith(self._prefix_delimited):
                length += 1

        return length


class ReloadConfig(BaseConfig):
    """
    A reload config that loads the configuration from its child
    from time to time, it is scheduled by a scheduler.

    Example usage:

    .. code-block:: python

        from central.config import ReloadConfig, FileConfig
        from central.schedulers import FixedIntervalScheduler

        config = ReloadConfig(FileConfig('config.json'), FixedIntervalScheduler())
        config.load()

        value = config.get('key')

    :param abc.Config config: The config to be reloaded from time to time.
    :param abc.Scheduler scheduler: The scheduler used to reload the configuration from the child.
    """
    def __init__(self, config, scheduler):
        super(ReloadConfig, self).__init__()

        if config is None or not isinstance(config, abc.Config):
            raise TypeError('config must be an abc.Config')

        if scheduler is None or not isinstance(scheduler, abc.Scheduler):
            raise TypeError('scheduler must be an abc.Scheduler')

        self._config = config
        self._config.lookup = self.lookup
        self._scheduler = scheduler
        self._loaded = False

    @property
    def config(self):
        """
        Get the config.
        :return abc.Config: The config.
        """
        return self._config

    @property
    def scheduler(self):
        """
        Get the scheduler.
        :return abc.Scheduler: The scheduler.
        """
        return self._scheduler

    def get_raw(self, key):
        """
        Get the raw value for given key if key is in the configuration, otherwise None.
        :param str key: The key to be found.
        :return: The value found, otherwise default.
        """
        return self._config.get_raw(key)

    def get_value(self, key, type, default=None):
        """
        Get the value for given key as the specified type if key is in the configuration, otherwise default.
        :param str key: The key to be found.
        :param type: The data type to convert the value to.
        :param default: The default value if the key is not found.
        :return: The value found, otherwise default.
        """
        return self._config.get_value(key, type, default=default)

    def load(self):
        """
        Load the child configuration and start the scheduler
        to reload the configuration from time to time.

        This method does not trigger the updated event.
        """
        self._config.load()

        if not self._loaded:
            self._scheduler.schedule(self._reload)
            self._loaded = True

    def _reload(self):
        """
        Reload the child configuration and trigger the updated event.
        It is only intended to be called by the scheduler.
        """
        try:
            self._config.load()
        except:
            logger.warning('Unable to load config ' + text_type(self._config), exc_info=True)

        try:
            self.updated()
        except:
            logger.warning('Error calling updated event from ' + str(self), exc_info=True)

    def _lookup_changed(self, lookup):
        """
        Set the new lookup to the child.
        :param lookup: The new lookup object.
        """
        self._config.lookup = lookup

    def __iter__(self):
        """
        Get a new iterator object that can iterate over the keys of the configuration.
        :return: The iterator.
        """
        return iter(self._config)

    def __len__(self):
        """
        Get the number of keys.
        :return int: The number of keys.
        """
        return len(self._config)


class UrlConfig(BaseDataConfig):
    """
    A url configuration based on `BaseDataConfig`.

    Example usage:

    .. code-block:: python

        from central.config import UrlConfig

        config = UrlConfig('http://date.jsontest.com/')
        config.load()

        value = config.get('time')

    :param str url: The url to be read.
    :param abc.Reader reader: The reader used to read the response from url as a dict,
        if None a reader based on the content type of the response is going to be used.
    """
    def __init__(self, url, reader=None):
        super(UrlConfig, self).__init__()

        if url is None or not isinstance(url, string_types):
            raise TypeError('url must be a str')

        if reader and not isinstance(reader, abc.Reader):
            raise TypeError('reader must be an abc.Reader')

        self._url = url
        self._reader = reader
        self._composer = Composer()

    @property
    def url(self):
        """
        Get the url.
        :return str: The url.
        """
        return self._url

    @property
    def reader(self):
        """
        Get the reader.
        :return abc.Reader: The reader.
        """
        return self._reader

    def load(self):
        """
        Load the configuration from the url.

        This method does not trigger the updated event.
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
        content_type, stream = self._read_url(url)

        try:
            reader = self._reader or self._get_reader(url, content_type)

            encoding = self._get_encoding(content_type)

            text_reader_cls = codecs.getreader(encoding)

            with text_reader_cls(stream) as text_reader:
                new_data = reader.read(text_reader)
        finally:
            stream.close()

        next_url = new_data.pop('@next', None)

        self._composer.compose(data, new_data)

        if next_url:
            if not isinstance(next_url, string_types):
                raise ConfigError('@next must be a str')

            next_url = self._interpolator.resolve(next_url, self._lookup)
            self._read(next_url, data)

    def _read_url(self, url):
        """
        Open the given url and returns its content type and the stream to read it.
        :param url: The url to be opened.
        :return tuple: The content type and the stream to read from.
        """
        response = urlopen(url)
        content_type = response.headers.get('content-type')
        return content_type, response

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
