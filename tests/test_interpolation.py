from __future__ import absolute_import

import os

from central.config import ChainConfig, MemoryConfig
from central.interpolation import BashInterpolator, ChainLookup, ConfigLookup, EnvironmentLookup
from unittest import TestCase


class TestBashInterpolator(TestCase):
    def setUp(self):
        self._interpolator = BashInterpolator()

    def test_resolve_with_none_as_value(self):
        with self.assertRaises(TypeError):
            self._interpolator.resolve(None, MemoryConfig().lookup)

    def test_resolve_with_non_string_as_value(self):
        with self.assertRaises(TypeError):
            self._interpolator.resolve(123, MemoryConfig().lookup)

    def test_resolve_with_none_as_lookup(self):
        with self.assertRaises(TypeError):
            self._interpolator.resolve('key', None)

    def test_resolve_with_string_as_lookup(self):
        with self.assertRaises(TypeError):
            self._interpolator.resolve('key', 'string lookup')

    def test_resolve_with_missing_variable(self):
        self.assertEqual('', self._interpolator.resolve('${key}', MemoryConfig().lookup))

    def test_resolve_with_variable(self):
        self.assertEqual('value', self._interpolator.resolve('${key}', MemoryConfig(data={'key': 'value'}).lookup))

    def test_resolve_without_variables(self):
        self.assertEqual('value', self._interpolator.resolve('value', MemoryConfig().lookup))

    def test_resolve_with_variable_in_a_composite_config(self):
        config = MemoryConfig()

        root = ChainConfig(
            MemoryConfig(data={'key': 'value'}),
            ChainConfig(config)
        )

        self.assertEqual('value', self._interpolator.resolve('${key}', config.lookup))


class TestChainLookup(TestCase):
    def test_init_lookups_with_none_value(self):
        with self.assertRaises(TypeError):
            ChainLookup(None)

    def test_lookup_with_existent_key(self):
        os.environ['KEY'] = 'value'
        lookup = ChainLookup(EnvironmentLookup())
        self.assertEqual('value', lookup.lookup('KEY'))

    def test_lookup_with_nonexistent_key(self):
        lookup = ChainLookup(EnvironmentLookup())
        self.assertEqual(None, lookup.lookup('not_found'))


class TestConfigLookup(TestCase):
    def test_init_config_with_none_value(self):
        with self.assertRaises(TypeError):
            ConfigLookup(config=None)

    def test_init_config_with_str_value(self):
        with self.assertRaises(TypeError):
            ConfigLookup(config='str')

    def test_init_config_with_config_value(self):
        config = MemoryConfig()
        lookup = ConfigLookup(config)
        self.assertEqual(config, lookup.config)

    def test_lookup_with_existent_key(self):
        config = MemoryConfig(data={'key': 1})
        lookup = ConfigLookup(config)
        self.assertEqual('1', lookup.lookup('key'))

    def test_lookup_with_nonexistent_key(self):
        config = MemoryConfig()
        lookup = ConfigLookup(config)
        self.assertEqual(None, lookup.lookup('key'))


class TestEnvironmentLookup(TestCase):
    def test_lookup_with_existent_key(self):
        os.environ['KEY'] = 'value'
        lookup = EnvironmentLookup()
        self.assertEqual('value', lookup.lookup('KEY'))

    def test_lookup_with_nonexistent_key(self):
        lookup = EnvironmentLookup()
        self.assertEqual(None, lookup.lookup('not_found'))
