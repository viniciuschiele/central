from __future__ import absolute_import

from central.config import ChainConfig, MemoryConfig
from central.exceptions import InterpolatorError
from central.interpolation import StrInterpolator, ConfigStrLookup
from unittest import TestCase


class TestStrInterpolator(TestCase):
    def test_resolve_with_none_as_value(self):
        interpolator = StrInterpolator()
        self.assertRaises(TypeError, interpolator.resolve, None, MemoryConfig().lookup)

    def test_resolve_with_non_string_as_value(self):
        interpolator = StrInterpolator()
        self.assertRaises(TypeError, interpolator.resolve, 123, MemoryConfig().lookup)

    def test_resolve_with_none_as_lookup(self):
        interpolator = StrInterpolator()
        self.assertRaises(TypeError, interpolator.resolve, 'key', None)

    def test_resolve_with_string_as_lookup(self):
        interpolator = StrInterpolator()
        with self.assertRaises(TypeError):
            interpolator.resolve('key', 'string lookup')

    def test_resolve_with_missing_variable(self):
        interpolator = StrInterpolator()
        with self.assertRaises(InterpolatorError):
            interpolator.resolve('{key}', MemoryConfig().lookup)

    def test_resolve_with_variable(self):
        interpolator = StrInterpolator()
        self.assertEqual('value', interpolator.resolve('{key}', MemoryConfig(data={'key': 'value'}).lookup))

    def test_resolve_without_variables(self):
        interpolator = StrInterpolator()
        self.assertEqual('value', interpolator.resolve('value', MemoryConfig().lookup))

    def test_resolve_with_variable_in_a_composite_config(self):
        config = MemoryConfig()

        root = ChainConfig([
            MemoryConfig(data={'key': 'value'}),
            ChainConfig([config])
        ])

        interpolator = StrInterpolator()
        self.assertEqual('value', interpolator.resolve('{key}', config.lookup))


class TestConfigStrLookup(TestCase):
    def test_init_config_with_none_value(self):
        with self.assertRaises(TypeError):
            ConfigStrLookup(config=None)

    def test_init_config_with_str_value(self):
        with self.assertRaises(TypeError):
            ConfigStrLookup(config='str')

    def test_init_config_with_config_value(self):
        config = MemoryConfig()
        lookup = ConfigStrLookup(config)
        self.assertEqual(config, lookup.config)

    def test_lookup_with_existent_key(self):
        config = MemoryConfig(data={'key': 1})
        lookup = ConfigStrLookup(config)
        self.assertEqual('1', lookup.lookup('key'))

    def test_lookup_with_nonexistent_key(self):
        config = MemoryConfig()
        lookup = ConfigStrLookup(config)
        self.assertEqual(None, lookup.lookup('key'))
