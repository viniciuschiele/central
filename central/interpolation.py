"""
Interpolator implementations.
"""

import re
import os

from . import abc
from .compat import string_types


__all__ = [
    'StrInterpolator',
    'ChainStrLookup',
    'ConfigStrLookup',
    'EnvironmentStrLookup',
]


class StrInterpolator(abc.StrInterpolator):
    """
    A `abc.StrInterpolator` implementation that resolves a string
    with replaceable variables in such format ${variable}
    using the provided lookup object to lookup replacement values.

    Example usage:

    .. code-block:: python

        from central.config import MemoryConfig
        from central.interpolation import StrInterpolator, ConfigStrLookup

        config = MemoryConfig(data={'property1': 1})

        interpolator = StrInterpolator()
        lookup = ConfigStrLookup(config)

        value = interpolator.resolve('${property1}', lookup)

        print(value)

    """

    def __init__(self):
        self._pattern = re.compile('\${(.*?)\}')

    def resolve(self, value, lookup):
        """
        Resolve a string with replaceable variables using the provided
        lookup object to lookup replacement values.
        :param str value: The value that contains variables to be resolved.
        :param abc.StrLookup lookup: The lookup object to lookup replacement values.
        :return str: The interpolated string.
        """
        if not isinstance(value, string_types):
            raise TypeError('value must be a str')

        if not isinstance(lookup, abc.StrLookup):
            raise TypeError('lookup must be an abc.StrLookup')

        variables = self._pattern.findall(value)

        for variable in variables:
            replace_value = lookup.lookup(variable)

            value = value.replace('${' + variable + '}', '' if replace_value is None else replace_value)

        return value


class ChainStrLookup(abc.StrLookup):
    """
    A `ChainStrLookup` groups multiple `StrLookup` together to create a single view.
    Lookups search the underlying lookups in reserved order successively until a key is found.

    :param lookups: The list of `StrLookup` objects. 
    """
    def __init__(self, *lookups):
        for lookup in lookups:
            if not isinstance(lookup, abc.StrLookup):
                raise TypeError('lookup must be an `abc.StrLookup`')

        self._lookups = lookups

    def lookup(self, key):
        """
        Lookup the given key in the environment variables.
        :param str key: The key to lookup.
        :return str: The value if found, otherwise None.
        """
        for lookup in reversed(self._lookups):
            value = lookup.lookup(key)

            if value is not None:
                return value

        return None


class ConfigStrLookup(abc.StrLookup):
    """
    A `ConfigStrLookup` lookups keys in a `abc.Config` object.

    :param abc.Config config: The config object to lookup keys.
    """
    def __init__(self, config):
        if not isinstance(config, abc.Config):
            raise TypeError('config must be an abc.Config')

        self._config = config

    @property
    def config(self):
        """
        Get the config object.
        :return abc.Config: The config object.
        """
        return self._config

    def lookup(self, key):
        """
        Lookup the given key in a config object.
        :param str key: The key to lookup.
        :return str: The value if found, otherwise None.
        """
        return self._config.get_str(key)


class EnvironmentStrLookup(abc.StrLookup):
    """
    An `EnvironmentStrLookup` lookups keys in the environment variables.
    """

    def lookup(self, key):
        """
        Lookup the given key in the environment variables.
        :param str key: The key to lookup.
        :return str: The value if found, otherwise None.
        """
        return os.environ.get(key)
