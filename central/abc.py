"""
Interfaces for reading configuration.
"""

from collections import Mapping


class Config(object):
    """
    Interface for reading a configuration.
    The config is read only.
    """

    def get(self, key, default=None):
        """
        Get the value for given key if key is in the configuration, otherwise default.
        :param str key: The key to be found.
        :param default: The default value if the key is not found.
        :return: The value found, otherwise default.
        """
        raise NotImplementedError()

    def get_bool(self, key, default=None):
        """
        Get the value for given key as a bool if key is in the configuration, otherwise None.
        :param str key: The key to be found.
        :param bool default: The default value if the key is not found.
        :return bool: The value found, otherwise default.
        """
        raise NotImplementedError()

    def get_dict(self, key, default=None):
        """
        Get the value for given key as a dict if key is in the configuration, otherwise None.
        :param str key: The key to be found.
        :param dict default: The default value if the key is not found.
        :return dict: The value found, otherwise default.
        """
        raise NotImplementedError()

    def get_int(self, key, default=None):
        """
        Get the value for given key as an int if key is in the configuration, otherwise None.
        :param str key: The key to be found.
        :param int default: The default value if the key is not found.
        :return int: The value found, otherwise default.
        """
        raise NotImplementedError()

    def get_float(self, key, default=None):
        """
        Get the value for given key as a float if key is in the configuration, otherwise None.
        :param str key: The key to be found.
        :param float default: The default value if the key is not found.
        :return float: The value found, otherwise default.
        """
        raise NotImplementedError()

    def get_list(self, key, default=None):
        """
        Get the value for given key as a list if key is in the configuration, otherwise None.
        :param str key: The key to be found.
        :param list default: The default value if the key is not found.
        :return list: The value found, otherwise default.
        """
        raise NotImplementedError()

    def get_raw(self, key):
        """
        Get the raw value for given key if key is in the configuration, otherwise None.
        :param str key: The key to be found.
        :return: The value found, otherwise default.
        """
        raise NotImplementedError()

    def get_str(self, key, default=None):
        """
        Get the value for given key as a str if key is in the configuration, otherwise None.
        :param str key: The key to be found.
        :param str default: The default value if the key is not found.
        :return str: The value found, otherwise default.
        """
        raise NotImplementedError()

    def get_value(self, key, type, default=None):
        """
        Get the value for given key as the specified type if key is in the configuration, otherwise default.
        :param str key: The key to be found.
        :param type: The data type to convert the value to.
        :param default: The default value if the key is not found.
        :return: The value found, otherwise default.
        """
        raise NotImplementedError()

    def keys(self):
        """
        Get the keys of the configuration.
        :return tuple: The keys of the configuration.
        """
        raise NotImplementedError()

    def items(self):
        """
        Get all the items of the configuration (key/value pairs).
        :return tuple: The items of the configuration.
        """
        raise NotImplementedError()

    def values(self):
        """
        Get all the values of the configuration.
        :return tuple: The values of the configuration.
        """
        raise NotImplementedError()

    def load(self):
        """
        Load the configuration.
        This method does not trigger the updated event.
        """
        raise NotImplementedError()

    @property
    def lookup(self):
        """
        Get the lookup object used for interpolation.
        :return StrLookup: The lookup object.
        """
        raise NotImplementedError()

    @lookup.setter
    def lookup(self, value):
        """
        Set the lookup object used for interpolation.
        :param StrLookup value: The lookup object.
        """
        raise NotImplementedError()

    @property
    def updated(self):
        """
        Get the updated event handler.
        :return EventHandler: The event handler.
        """
        raise NotImplementedError()

    def on_updated(self, func):
        """
        Add a new callback for updated event.
        It can also be used as decorator.
        :param func: The callback.
        """
        raise NotImplementedError()

    def prefixed(self, prefix):
        """
        Get a subset of the configuration prefixed by a key.
        :param str prefix: The prefix to prepend to the keys.
        :return abc.Config: The subset of the configuration prefixed by a key.
        """
        raise NotImplementedError()

    def reload_every(self, interval):
        """
        Get a reload configuration to reload the
        current configuration every interval given.
        :param int interval: The interval in milliseconds between loads.
        :return Config: The config object.
        """
        raise NotImplementedError()

    def __contains__(self, key):
        """
        Get true if key is in the configuration, otherwise false.
        :param str key: The key to be checked.
        :return bool: true if key is in the configuration, false otherwise.
        """
        raise NotImplementedError()

    def __getitem__(self, key):
        """
        Get the value if key is in the configuration, otherwise KeyError is raised.
        :param str key: The key to be found.
        :return: The value found.
        """
        raise NotImplementedError()

    def __iter__(self):
        """
        Get a new iterator object that can iterate over the keys of the configuration.
        :return: The iterator.
        """
        raise NotImplementedError()

    def __len__(self):
        """
        Get the number of keys.
        :return int: The number of keys.
        """
        raise NotImplementedError()


class Reader(object):
    """
    Interface for reading a configuration from a specific stream as a dict.
    """

    def read(self, stream):
        """
        Read the given stream and returns it as a dict.
        :param stream: The stream to read the configuration from.
        :return IgnoreCaseDict: The configuration read from the stream.
        """
        raise NotImplementedError()


class Decoder(object):
    """
    Interface decoding values to arbitrary types.
    """

    def decode(self, o, type):
        """
        Decode the given value to the given data type.
        :param o: The value to be decoded.
        :param type: The format to be decoded.
        :return: The value decoded.
        """
        raise NotImplementedError()


class Merger(object):
    """
    Merge two or more dicts.
    """

    def merge(self, base, *data):
        """
        Merge the given list of dicts into `base` dict.
        :param dict base: The base dict that holds the merged data.
        :param tuple data: The list of dicts to be merge.
        """
        raise NotImplementedError()


class Scheduler(object):
    """
    Interface for scheduling execution.
    It is intended to be used for reload configuration.
    """

    def schedule(self, func):
        """
        Schedule a given func to be executed in the future.
        :param func: The function to be executed.
        """
        raise NotImplementedError()


class StrInterpolator(object):
    """
    Interface for interpolating a string.

    The interpolator will extract the key and call the lookup to get the value for that key.
    """

    def resolve(self, value, lookup):
        """
        Resolve a string with replaceable variables using the provided
        lookup object to lookup replacement values.

        An exception is thrown for variables without a replacement value.

        :param str value: The value that contains variables to be resolved.
        :param StrLookup lookup: The lookup object to lookup replacement values.
        :return str: The interpolated string.
        """
        raise NotImplementedError()


class StrLookup(object):
    """
    Interface for looking up of a raw string for replacements.
    """

    def lookup(self, key):
        """
        Get the value for the given key.
        :param str key: The key to lookup.
        :return str: The value if found, otherwise None.
        """
        raise NotImplementedError()


class PropertyManager(object):
    """
    Interface for managing PropertyContainer objects.

    A PropertyManager is attached to the Config source from which it
    receives notification of value changes.
    """

    def get_property(self, name):
        """
        Get a property for the property name.
        :param str name: The name of the property.
        :return PropertyContainer: The property object.
        """
        raise NotImplementedError()


class PropertyContainer(object):
    """
    Interface for a single property that can be parsed as any type.
    """

    def as_bool(self, default):
        """
        Get a bool property object.
        :param bool default: The default value.
        :return Property: The property object.
        """
        raise NotImplementedError()

    def as_float(self, default):
        """
        Get a float property object.
        :param float default: The default value.
        :return Property: The property object.
        """
        raise NotImplementedError()

    def as_int(self, default):
        """
        Get an integer property object.
        :param int default: The default value.
        :return Property: The property object.
        """
        raise NotImplementedError()

    def as_str(self, default):
        """
        Get a string property object.
        :param str default: The default value.
        :return Property: The property object.
        """
        raise NotImplementedError()

    def as_dict(self, default):
        """
        Get a dict property object.
        :param dict default: The default value.
        :return Property: The property object.
        """
        raise NotImplementedError()

    def as_list(self, default):
        """
        Get a list property object.
        :param list default: The default value.
        :return Property: The property object.
        """
        raise NotImplementedError()

    def as_type(self, type, default):
        """
        Get a property object based on the given type.
        :param type: The type to convert the value to.
        :param default: The default value.
        :return Property: The property object.
        """
        raise NotImplementedError()


class Property(object):
    """
    Interface to access latest cached value for a Property.
    """

    def get(self):
        """
        Get the most recent value of the property.
        :return: The most recent value of the property.
        """
        raise NotImplementedError()

    def on_updated(self, func):
        """
        Add a new callback for updated event.
        It can also be used as decorator.
        :param func: The callback.
        """
        raise NotImplementedError()

    @property
    def updated(self):
        """
        Get the updated event handler.
        :return utils.event.EventHandler: The event handler.
        """
        raise NotImplementedError()


# register Config as a compatible Mapping class
# so that isinstance(config, Mapping) returns True.
Mapping.register(Config)
