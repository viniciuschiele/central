"""
Interpolator implementations.
"""

import re

from . import abc
from .compat import string_types, text_type
from .exceptions import InterpolatorError


__all__ = [
    'StrInterpolator',
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

    def resolve(self, value, lookup, raise_on_missing=True):
        """
        Resolve a string with replaceable variables using the provided
        lookup object to lookup replacement values.

        An exception is thrown for variables without a replacement value.

        :param str value: The value that contains variables to be resolved.
        :param abc.StrLookup lookup: The lookup object to lookup replacement values.
        :param bool raise_on_missing: True to raise an exception if replacement value is missing.
        :return str: The interpolated string.
        """
        if value is None or not isinstance(value, string_types):
            raise TypeError('value must be a str')

        if lookup is None or not isinstance(lookup, abc.StrLookup):
            raise TypeError('lookup must be an abc.StrLookup')

        variables = self._pattern.findall(value)

        for variable in variables:
            replace_value = lookup.lookup(variable)

            if replace_value is None:
                if raise_on_missing:
                    raise InterpolatorError('Interpolation variable %s not found' % text_type(variable))
            else:
                value = value.replace('${' + variable + '}', replace_value)

        return value


class ConfigStrLookup(abc.StrLookup):
    """
    A `StrLookup` implementation that lookup keys in a `abc.Config` object.

    :param abc.Config config: The config object to lookup keys.
    """
    def __init__(self, config):
        if config is None or not isinstance(config, abc.Config):
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
