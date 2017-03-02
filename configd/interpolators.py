"""
Interpolator implementations.
"""

import re

from . import abc
from .exceptions import InterpolatorError


__all__ = [
    'DefaultInterpolator',
]


class DefaultInterpolator(abc.Interpolator):
    """
    Default interpolator implementation that resolves a string
    with replaceable variables in such format {variable}
    using the provided config to lookup replacement values.

    Example usage:

    .. code-block:: python

        from configd.config import MemoryConfig
        from configd.interpolators import DefaultInterpolator

        config = MemoryConfig(data={'property1': 1})

        interpolator = DefaultInterpolator()
        value = interpolator.resolve('{property1}', config)

        print(value)

    """

    def __init__(self):
        self._pattern = re.compile('\{(.*?)\}')

    def resolve(self, value, config):
        """
        Resolve a string with replaceable variables using the provided
        config to lookup replacement values.
        An exception is thrown for variables without a replacement value.
        :param str value: The value which contains variables to be resolved.
        :param abc.Config config: The configuration to lookup replacement values.
        :return str: The interpolated string.
        """
        if value is None or not isinstance(value, str):
            raise TypeError('value must be a str')

        if config is None or not isinstance(config, abc.Config):
            raise TypeError('config must be an abc.Config')

        variables = self._pattern.findall(value)

        for variable in variables:
            replace_value = self._lookup(variable, config)

            if replace_value is None:
                raise InterpolatorError('Interpolation variable %s not found' % str(variable))

            value = value.replace('{' + variable + '}', replace_value)

        return value

    def _lookup(self, variable, config):
        """
        Lookup a variable in the given configuration.
        :param str variable: The variable name.
        :param abc.Config config: The configuration to lookup.
        :return str: The variable value found, otherwise None.
        """
        root = self._get_root(config)
        return root.get(variable, cast=str)

    def _get_root(self, config):
        """
        Get the root configuration for the given configuration.
        :param abc.Config config: The config.
        :return abc.Config: The root configuration.
        """
        while config.parent:
            config = config.parent
        return config
