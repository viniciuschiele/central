"""
Interfaces for reading configuration.
"""


class Config(object):
    """
    Interface for reading a configuration.
    The config is read only.
    """

    @property
    def parent(self):
        """
        Get the parent configuration.
        :return Config: The parent or None if no parent.
        """
        raise NotImplemented()

    @parent.setter
    def parent(self, value):
        """
        Set the parent configuration.
        :param Config value: The parent.
        """
        raise NotImplemented()

    @property
    def updated(self):
        """
        Get the updated event handler.
        :return utils.event.EventHandler: The event handler.
        """
        raise NotImplemented()

    def get(self, key, default=None, cast=None):
        """
        Get the value for given key if key is in the configuration, otherwise default.
        :param str key: The key to be found.
        :param default: The default value if the key is not found.
        :param cast: The data type to convert the value to.
        :return: The value found, otherwise default.
        """
        raise NotImplemented()

    def load(self):
        """
        Load all the keys and values.
        This method does not trigger the updated event.
        """
        raise NotImplemented()


class CompositeConfig(Config):
    """
    Config that is a composite of multiple configuration and as such doesn't track
    properties of its own.

    The composite does not merge the configurations but instead treats them as
    overrides so that a property existing in a configuration supersedes the same
    property in configuration based on some ordering.

    Implementations of this interface should specify and implement the override ordering.
    """

    def add_config(self, name, config):
        """
        Add a named configuration.
        Duplicate configurations are not allowed.
        :param str name: The name of the configuration.
        :param Config config: The configuration.
        """
        raise NotImplemented()

    def get_config(self, name):
        """
        Get a configuration by name.
        :param str name: The name of the configuration.
        :return Config: The configuration found or None.
        """
        raise NotImplemented()

    def get_config_names(self):
        """
        Get the names of all configurations previously added.
        :return list: The list of configuration names.
        """
        raise NotImplemented()

    def remove_config(self, name):
        """
        Remove a configuration by name.
        :param str name: The name of the configuration
        :return Config: The configuration removed or None if not found.
        """
        raise NotImplemented()


class Reader(object):
    """
    Interface for reading a configuration from a specific stream as a dict.
    """

    def read(self, stream):
        """
        Read the given stream and returns it as a dict.
        :param stream: The stream to read the configuration from.
        :return dict: The configuration read from the stream.
        """
        raise NotImplemented()


class Decoder(object):
    """
    Interface decoding values to arbitrary types.
    """

    def decode(self, o, cast):
        """
        Decode the given value to the given data type.
        :param o: The value to be decoded.
        :param cast: The format to be decoded.
        :return: The value decoded.
        """
        raise NotImplemented()


class Scheduler(object):
    """
    Interface for scheduling execution.
    It is intended to be used for polling configuration.
    """

    def schedule(self, func):
        """
        Schedule a given func to be executed in the future.
        :param func: The function to be executed.
        """
        raise NotImplementedError()


class Interpolator(object):
    """
    Interface for interpolating a string.
    """

    def resolve(self, value, config):
        """
        Resolve a string with replaceable variables using the provided
        config to lookup replacement values.
        The implementation should throw an exception for variables without
        a replacement value.
        :param str value: The value which contains variables to be resolved.
        :param Config config: The configuration to lookup replacement values.
        :return str: The interpolated string.
        """
        raise NotImplemented()
