"""
Interpolator implementations.
"""

import re

from . import abc
from .exceptions import InterpolatorError
from .utils.compat import string_types, text_type


__all__ = [
    'StrInterpolator',
]


class StrInterpolator(abc.StrInterpolator):
    """
    A `abc.StrInterpolator` implementation that resolves a string
    with replaceable variables in such format {variable}
    using the provided lookup object to lookup replacement values.

    Example usage:

    .. code-block:: python

        from configd.config import MemoryConfig
        from configd.interpolation import StrInterpolator, ConfigStrLookup

        config = MemoryConfig(data={'property1': 1})

        interpolator = StrInterpolator()
        lookup = ConfigStrLookup(config)

        value = interpolator.resolve('{property1}', lookup)

        print(value)

    """

    def __init__(self):
        self._pattern = re.compile('\{(.*?)\}')

    def resolve(self, value, lookup):
        """
        Resolve a string with replaceable variables using the provided
        lookup object to lookup replacement values.

        An exception is thrown for variables without a replacement value.

        :param str value: The value that contains variables to be resolved.
        :param abc.StrLookup lookup: The lookup object to lookup replacement values.
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
                raise InterpolatorError('Interpolation variable %s not found' % text_type(variable))

            value = value.replace('{' + variable + '}', replace_value)

        return value


class ConfigStrLookup(abc.StrLookup):
    """
    A `StrLookup` implementation that lookup keys in a `abc.Config` object.

    :param abc.Config config: The config object to lookup keys.
    """
    def __init__(self, config):
        self._config = config

    def lookup(self, key):
        """
        Lookup the given key in a config object.
        :param str key: The key to lookup.
        :return str: The value if found, otherwise None.
        """
        return self._config.get(key, cast=text_type)
