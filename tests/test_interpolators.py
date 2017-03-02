from configd.config import CompositeConfig, MemoryConfig
from configd.exceptions import InterpolatorError
from configd.interpolators import DefaultInterpolator
from unittest import TestCase


class TestDefaultInterpolator(TestCase):
    def test_resolve_with_none_as_value(self):
        interpolator = DefaultInterpolator()
        self.assertRaises(TypeError, interpolator.resolve, None, MemoryConfig())

    def test_resolve_with_non_string_as_value(self):
        interpolator = DefaultInterpolator()
        self.assertRaises(TypeError, interpolator.resolve, 123, MemoryConfig())

    def test_resolve_with_config_as_none(self):
        interpolator = DefaultInterpolator()
        self.assertRaises(TypeError, interpolator.resolve, 'key', None)

    def test_resolve_with_non_config_as_config(self):
        interpolator = DefaultInterpolator()
        self.assertRaises(TypeError, interpolator.resolve, 'key', 'non-config')

    def test_resolve_with_missing_variable(self):
        interpolator = DefaultInterpolator()
        self.assertRaises(InterpolatorError, interpolator.resolve, '{key}', MemoryConfig())

    def test_resolve_with_variable(self):
        interpolator = DefaultInterpolator()
        self.assertEqual('value', interpolator.resolve('{key}', MemoryConfig(data={'key': 'value'})))

    def test_resolve_without_variables(self):
        interpolator = DefaultInterpolator()
        self.assertEqual('value', interpolator.resolve('value', MemoryConfig()))

    def test_resolve_with_variable_in_a_composite_config(self):
        config = MemoryConfig()

        nested = CompositeConfig()
        nested.add_config('empty', config)

        root = CompositeConfig()
        root.add_config('mem', MemoryConfig(data={'key': 'value'}))
        root.add_config('nested', nested)

        interpolator = DefaultInterpolator()
        self.assertEqual('value', interpolator.resolve('{key}', config))

