"""
Core config implementations.
"""

import importlib
import logging
import os
import sys

from collections import KeysView, ItemsView, ValuesView, Mapping
from .. import abc
from ..compat import text_type, string_types
from ..decoders import Decoder
from ..exceptions import ConfigError
from ..interpolation import BashInterpolator, ConfigLookup, ChainLookup, EnvironmentLookup
from ..schedulers import FixedIntervalScheduler
from ..structures import IgnoreCaseDict
from ..utils import EventHandler, make_ignore_case, merge_dict


logger = logging.getLogger(__name__)


NESTED_DELIMITER = '.'


class BaseConfig(abc.Config):
    """
    Base config class for implementing an `abc.Config`.
    """

    def __init__(self):
        self._lookup = ConfigLookup(self)
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
            self._lookup = ConfigLookup(self)
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
        :param Number interval: The interval in seconds between loads.
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
        value = self.get_value(key, object)

        if value is None:
            raise KeyError(key)

        return value


class BaseDataConfig(BaseConfig):
    """
    Base config class that holds keys.
    """

    def __init__(self):
        super(BaseDataConfig, self).__init__()
        self._data = IgnoreCaseDict()
        self._decoder = Decoder.instance()
        self._interpolator = BashInterpolator()

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
        if not isinstance(value, abc.Decoder):
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
        if not isinstance(value, abc.StrInterpolator):
            raise TypeError('interpolator must be an abc.StrInterpolator')

        self._interpolator = value

    def get_raw(self, key):
        """
        Get the raw value for given key if key is in the configuration, otherwise None.
        Find the given key considering the nested delimiter as nested key.
        :param str key: The key to be found.
        :return: The value found, otherwise None.
        """
        if key is None:
            raise TypeError('key cannot be None')

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
        if key is None:
            raise TypeError('key cannot be None')

        if type is None:
            raise TypeError('type cannot be None')

        value = self.get_raw(key)

        if value is None:
            if callable(default):
                return default()

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


class ChainConfig(BaseConfig):
    """
    Combine multiple `abc.Config` in a fallback chain.

    The chain does not merge the configurations but instead
    treats them as overrides so that a key existing in a configuration supersedes
    the same key in the previous configuration.

    The chain works in reverse order, that means the last configuration
    in the chain overrides the previous one.

    Example usage:

    .. code-block:: python

        from central.config import CommandLineConfig, EnvironmentConfig, FallbackConfig

        config = ChainConfig(EnvironmentConfig(), CommandLineConfig())
        config.load()

        value = config.get('key1')

    :param configs: The list of `abc.Config`.
    """
    def __init__(self, *configs):
        super(ChainConfig, self).__init__()

        for config in configs:
            if not isinstance(config, abc.Config):
                raise TypeError('config must be an abc.Config')

            config.lookup = self._lookup
            config.updated.add(self._config_updated)

        self._configs = configs
        self._keys_cached = None

    @property
    def configs(self):
        """
        Get the sub configurations.
        :return tuple: The list of `abc.Config`.
        """
        return self._configs

    def get_raw(self, key):
        """
        Get the raw value for given key if key is in the configuration, otherwise None.
        It goes through every child to find the given key.
        :param str key: The key to be found.
        :return: The value found, otherwise None.
        """
        for config in reversed(self._configs):
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
        for config in reversed(self._configs):
            value = config.get_value(key, type)
            if value is not None:
                return value

        if callable(default):
            return default()

        return default

    def load(self):
        """
        Load the sub configurations.

        This method does not trigger the updated event.
        """
        self._keys_cached = None

        for config in self._configs:
            config.load()

    def _config_updated(self):
        """
        Called by updated event from the children.
        It is not intended to be called directly.
        """
        # reset the cache because the children's
        # configuration has been changed.
        self._keys_cached = None

        self.updated()

    def _lookup_changed(self, lookup):
        """
        Set the new lookup to the children.
        :param lookup: The new lookup object.
        """
        for config in self._configs:
            config.lookup = lookup

    def _build_cached_keys(self):
        """
        Build the cache for the children's keys.
        :return IgnoreCaseDict: The dict containing the keys. 
        """
        keys = IgnoreCaseDict()

        for config in self._configs:
            for key in config.keys():
                keys[key] = True

        return keys

    def _get_cached_keys(self):
        """
        Get the cache for the children's keys.
        :return IgnoreCaseDict: The dict containing the keys. 
        """
        if self._keys_cached is None:
            self._keys_cached = self._build_cached_keys()
        return self._keys_cached

    def __iter__(self):
        """
        Get a new iterator object that can iterate over the keys of the configuration.
        :return: The iterator.
        """
        return iter(self._get_cached_keys())

    def __len__(self):
        """
        Get the number of keys.
        :return int: The number of keys.
        """
        return len(self._get_cached_keys())


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
        Load the configuration from the command line args.

        This method does not trigger the updated event.
        """
        data = IgnoreCaseDict()

        # the first item is the file name.
        args = sys.argv[1:]

        iterator = iter(args)

        while True:
            try:
                current_arg = next(iterator)
            except StopIteration:
                break

            key_start_index = 0

            if current_arg.startswith('--'):
                key_start_index = 2

            elif current_arg.startswith('-'):
                key_start_index = 1

            separator = current_arg.find('=')

            if separator == -1:
                if key_start_index == 0:
                    raise ConfigError('Unrecognized argument %s format' % current_arg)

                key = current_arg[key_start_index:]

                try:
                    value = next(iterator)
                except StopIteration:
                    raise ConfigError('Value for argument %s is missing' % key)
            else:
                key = current_arg[key_start_index:separator].strip()

                if not key:
                    raise ConfigError('Unrecognized argument %s format' % current_arg)

                value = current_arg[separator + 1:].strip()

            data[key] = value

        self._data = data


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
        Load the configuration from environment variables.

        This method does not trigger the updated event.
        """
        self._data = IgnoreCaseDict(os.environ)


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

            self._data = make_ignore_case(data)

    def set(self, key, value):
        """
        Set a value for the given key.
        The updated event is triggered.
        :param str key: The key.
        :param value: The value.
        """
        if key is None:
            raise TypeError('key cannot be None')

        if isinstance(value, Mapping):
            value = make_ignore_case(value)

        self._data[key] = value
        self.updated()

    def load(self):
        """
        Do nothing
        """


class MergeConfig(BaseDataConfig):
    """
    Merge multiple `abc.Config`, in case of key collision last-match wins.

    Example usage:

    .. code-block:: python

        from central.config import FileConfig, MergeConfig

        config = MergeConfig(FileConfig('base.json'), FileConfig('dev.json'))
        config.load()

        value = config.get('key1')

    :param configs: The list of `abc.Config`.
    """
    def __init__(self, *configs):
        super(MergeConfig, self).__init__()

        if not isinstance(configs, (tuple, list)):
            raise TypeError('configs must be a list or tuple')

        for config in configs:
            if not isinstance(config, abc.Config):
                raise TypeError('config must be an abc.Config')

            config.lookup = self._lookup
            config.updated.add(self._config_updated)

        self._configs = configs
        self._raw_configs = [self._RawConfig(config) for config in self._configs]

    @property
    def configs(self):
        """
        Get the sub configurations.
        :return tuple: The list of `abc.Config`.
        """
        return self._configs

    def load(self):
        """
        Load the sub configurations and merge them
        into a single configuration.

        This method does not trigger the updated event.
        """
        for config in self._configs:
            config.load()

        data = IgnoreCaseDict()

        if len(self._configs) == 0:
            return data

        merge_dict(data, *self._raw_configs)

        self._data = data

    def _config_updated(self):
        """
        Called by updated event from the children.
        It is not intended to be called directly.
        """
        self.updated()

    class _RawConfig(Mapping):
        """
        Internal class used to merge a `abc.Config`.

        When we merge configs we want to merge the raw value
        rather than decoded and interpolated value.
        """
        def __init__(self, config):
            self._config = config

        def get(self, key, default=None):
            value = self._config.get_raw(key)
            if value is None:
                return default
            return value

        def __contains__(self, key):
            return key in self._config

        def __getitem__(self, key):
            value = self._config.get_raw(key)
            if value is None:
                raise KeyError(key)
            return value

        def __iter__(self):
            return iter(self._config)

        def __len__(self):
            return len(self._config)


class ModuleConfig(BaseDataConfig):
    """
    A config implementation that loads the configuration
    from a Python module.

    Example usage:

    .. code-block:: python

        from central.config import ModuleConfig

        config = ModuleConfig('module_name')
        config.load()

        value = config.get('key')

    :param str name: The module name to be loaded.
    """

    def __init__(self, name):
        super(ModuleConfig, self).__init__()
        if not isinstance(name, string_types):
            raise TypeError('name must be a str')

        self._name = name

    @property
    def name(self):
        """
        Get the module name.
        :return str: The module name.
        """
        return self._name

    def load(self):
        """
        Load the configuration from a file.
        Recursively load any filename referenced by an @next property in the configuration.

        This method does not trigger the updated event.
        """
        to_merge = []
        name = self._name

        # create a chain lookup to resolve any variable left
        # using environment variable.
        lookup = ChainLookup(EnvironmentLookup(), self._lookup)

        while name:
            o = self._import_module(self._interpolator.resolve(name, lookup))

            data = {}

            for key in dir(o):
                if not key.startswith('_'):
                    data[key] = getattr(o, key)

            name = getattr(o, '_next', None)

            if name is not None and not isinstance(name, string_types):
                raise ConfigError('_next must be a str')

            to_merge.append(data)

        data = make_ignore_case(to_merge[0])

        if len(to_merge) > 1:
            merge_dict(data, *to_merge[1:])

        self._data = data

    def _import_module(self, name):
        """
        Import module by name.
        :param str name: The name of the module.
        :return: The module loaded. 
        """
        return importlib.import_module(name)


class PrefixedConfig(BaseConfig):
    """
    A config implementation to view into another Config
    for keys starting with a specified prefix.

    Example usage:

    .. code-block:: python

        from central.config import PrefixedConfig, MemoryConfig

        config = MemoryConfig(data={'production.timeout': 10})

        prefixed = PrefixedConfig('production', config)

        value = prefixed.get('timeout')

    :param str prefix: The prefix to prepend to the keys.
    :param abc.Config config: The config to load the keys from.
    """
    def __init__(self, prefix, config):
        super(PrefixedConfig, self).__init__()

        if not isinstance(prefix, string_types):
            raise TypeError('prefix must be a str')

        if not isinstance(config, abc.Config):
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
        if key is None:
            raise TypeError('key cannot be None')

        try:
            key = self._prefix_delimited + key
        except TypeError:
            raise TypeError('key must be a str')

        return self._config.get_raw(key)

    def get_value(self, key, type, default=None):
        """
        Get the value for given key as the specified type if key is in the configuration, otherwise default.
        :param str key: The key to be found.
        :param type: The data type to convert the value to.
        :param default: The default value if the key is not found.
        :return: The value found, otherwise default.
        """
        if key is None:
            raise TypeError('key cannot be None')

        try:
            key = self._prefix_delimited + key
        except TypeError:
            raise TypeError('key must be a str')

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
                if isinstance(value, Mapping):
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
                if isinstance(value, Mapping):
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

        if not isinstance(config, abc.Config):
            raise TypeError('config must be an abc.Config')

        if not isinstance(scheduler, abc.Scheduler):
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
        to reload the child configuration from time to time.

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
