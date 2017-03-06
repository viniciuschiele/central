from __future__ import absolute_import

from configd.config import CompositeConfig, MemoryConfig
from configd.exceptions import InterpolatorError
from configd.interpolation import StrInterpolator
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

        nested = CompositeConfig()
        nested.add_config('empty', config)

        root = CompositeConfig()
        root.add_config('mem', MemoryConfig(data={'key': 'value'}))
        root.add_config('nested', nested)

        interpolator = StrInterpolator()
        self.assertEqual('value', interpolator.resolve('{key}', config.lookup))

