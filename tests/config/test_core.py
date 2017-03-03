from configd.config import (
    CommandLineConfig, CompositeConfig, EnvironmentConfig, FileConfig, MemoryConfig, PollingConfig
)
from configd.decoders import DefaultDecoder
from configd.exceptions import ConfigError
from configd.interpolators import DefaultInterpolator
from unittest import TestCase


class BaseDataConfigMixin(object):
    def __init__(self):
        self._base_config = None

    def _load_config(self):
        self._base_config.load()

    def test_default_decoder(self):
        self.assertTrue(isinstance(self._base_config.decoder, DefaultDecoder))

    def test_set_decoder_with_decoder_as_value(self):
        decoder = DefaultDecoder()
        self._base_config.decoder = decoder

        self.assertEqual(decoder, self._base_config.decoder)

    def test_set_decoder_with_none_as_value(self):
        with self.assertRaises(TypeError):
            self._base_config.decoder = None

    def test_set_decoder_with_non_decoder_as_value(self):
        with self.assertRaises(TypeError):
            self._base_config.decoder = 'non decoder'

    def test_default_interpolator(self):
        self.assertTrue(isinstance(self._base_config.interpolator, DefaultInterpolator))

    def test_set_interpolator_with_interpolator_as_value(self):
        interpolator = DefaultInterpolator()
        self._base_config.interpolator = interpolator

        self.assertEqual(interpolator, self._base_config.interpolator)

    def test_set_interpolator_with_none_as_value(self):
        with self.assertRaises(TypeError):
            self._base_config.interpolator = None

    def test_set_interpolator_with_non_interpolator_as_value(self):
        with self.assertRaises(TypeError):
            self._base_config.interpolator = 'non interpolator'

    def test_default_parent(self):
        self.assertIsNone(self._base_config.parent)

    def test_set_parent_with_config_as_value(self):
        parent = MemoryConfig()
        self._base_config.parent = parent

        self.assertEqual(parent, self._base_config.parent)

    def test_set_parent_with_none_as_value(self):
        self._base_config.parent = None
        self.assertIsNone(self._base_config.parent)

    def test_set_parent_with_non_config_as_value(self):
        with self.assertRaises(TypeError):
            self._base_config.parent = 'non config'

    def test_get_with_none_as_name(self):
        with self.assertRaises(TypeError):
            self._base_config.get(None)

    def test_get_with_non_str_as_name(self):
        with self.assertRaises(TypeError):
            self._base_config.get(1234)

    def test_get_with_existent_key(self):
        self._load_config()
        self.assertEqual('value', self._base_config.get('key_str'))

    def test_get_with_nonexistent_key(self):
        self.assertIsNone(self._base_config.get('not_found'))

    def test_get_with_default_value(self):
        self.assertEqual(2, self._base_config.get('not_found', default=2))

    def test_get_with_cast(self):
        self._load_config()
        self.assertEqual('1', self._base_config.get('key_int', cast=str))

    def test_get_before_loading(self):
        self.assertIsNone(self._base_config.get('key_int'))

    def test_get_after_loading(self):
        self._load_config()
        self.assertEqual('value', self._base_config.get('key_str'))

    def test_get_with_interpolation(self):
        self._load_config()
        self.assertEqual('value', self._base_config.get('key_interpolated'))


class AtNextMixin(object):
    def test_get_new_key(self):
        self._base_config.load()
        self.assertEqual('new value', self._base_config.get('key_new'))

    def test_get_overridden_key(self):
        self._base_config.load()
        self.assertEqual('value overridden', self._base_config.get('key_overridden'))


class TestCommandLineConfig(TestCase, BaseDataConfigMixin):
    def setUp(self):
        self._base_config = CommandLineConfig()

    def tearDown(self):
        import sys
        sys.argv = []

    def _load_config(self):
        import sys
        sys.argv = ['key_str=value',
                    'key_int=1',
                    'key_interpolated={key_str}',
                    ]
        self._base_config.load()

    def test_argument_without_equal_operator(self):
        import sys
        sys.argv = ['key1']

        config = CommandLineConfig()
        config.load()

        self.assertIsNone(config.get('key1'))

    def test_argument_without_key(self):
        import sys
        sys.argv = ['=value']

        config = CommandLineConfig()
        config.load()

        self.assertIsNone(config.get('key1'))

    def test_argument_without_value(self):
        import sys
        sys.argv = ['key1=']

        config = CommandLineConfig()
        config.load()

        self.assertEqual('', config.get('key1'))


class TestCompositeConfig(TestCase):
    def test_auto_load_with_none_as_value(self):
        self.assertRaises(TypeError, CompositeConfig, auto_load=None)

    def test_auto_load_with_non_bool_value(self):
        self.assertRaises(TypeError, CompositeConfig, auto_load='non bool')

    def test_default_load_on_add(self):
        self.assertFalse(CompositeConfig().load_on_add)

    def test_default_parent(self):
        self.assertIsNone(CompositeConfig().parent)

    def test_set_parent_with_config_as_value(self):
        parent = MemoryConfig()
        config = CompositeConfig()
        config.parent = parent

        self.assertEqual(parent, config.parent)

    def test_set_parent_with_none_as_value(self):
        config = CompositeConfig()
        config.parent = None
        self.assertIsNone(config.parent)

    def test_set_parent_with_non_config_as_value(self):
        with self.assertRaises(TypeError):
            config = CompositeConfig()
            config.parent = 'non config'

    def test_add_config(self):
        child = MemoryConfig()
        config = CompositeConfig()
        config.add_config('mem', child)

        self.assertEqual(child, config.get_config('mem'))

    def test_add_config_with_none_as_name(self):
        config = CompositeConfig()
        with self.assertRaises(TypeError):
            config.add_config(None, MemoryConfig())

    def test_add_config_with_non_str_as_name(self):
        config = CompositeConfig()
        with self.assertRaises(TypeError):
            config.add_config(1234, MemoryConfig())

    def test_add_config_with_none_as_config(self):
        config = CompositeConfig()
        with self.assertRaises(TypeError):
            config.add_config('cfg', None)

    def test_add_config_with_non_config_as_config(self):
        config = CompositeConfig()
        with self.assertRaises(TypeError):
            config.add_config('cfg', 'non config')

    def test_add_config_with_duplicated_name(self):
        config = CompositeConfig()
        config.add_config('cfg', MemoryConfig())
        with self.assertRaises(ConfigError):
            config.add_config('cfg', MemoryConfig())

    def test_add_config_with_parent_set(self):
        child = MemoryConfig()
        parent = MemoryConfig()
        child.parent = parent

        config = CompositeConfig()
        with self.assertRaises(ConfigError):
            config.add_config('cfg', child)

    def test_get_config_with_none_as_name(self):
        config = CompositeConfig()
        with self.assertRaises(TypeError):
            config.get_config(None)

    def test_get_config_with_non_string_as_name(self):
        config = CompositeConfig()
        with self.assertRaises(TypeError):
            config.get_config(123)

    def test_get_config_with_nonexistent_config(self):
        config = CompositeConfig()
        self.assertIsNone(config.get_config('not found'))

    def test_get_config_with_existent_config(self):
        child = MemoryConfig()

        config = CompositeConfig()
        config.add_config('mem', child)

        self.assertEqual(child, config.get_config('mem'))

    def test_get_config_names(self):
        config = CompositeConfig()
        self.assertEqual([], config.get_config_names())

        config.add_config('mem1', MemoryConfig())
        self.assertEqual(['mem1'], config.get_config_names())

    def test_remove_config_with_none_as_name(self):
        config = CompositeConfig()
        with self.assertRaises(TypeError):
            config.remove_config(None)

    def test_remove_config_with_non_str_as_name(self):
        config = CompositeConfig()
        with self.assertRaises(TypeError):
            config.remove_config(1234)

    def test_remove_config_with_nonexistent_config(self):
        config = CompositeConfig()
        self.assertIsNone(config.remove_config('not found'))

    def test_remove_config_with_existent_config(self):
        child = MemoryConfig()

        config = CompositeConfig()
        config.add_config('mem', child)

        self.assertEqual(child, config.remove_config('mem'))
        self.assertIsNone(config.get_config('mem'))

    def test_parent_after_add_config(self):
        child = MemoryConfig()

        config = CompositeConfig()
        config.add_config('cfg', child)

        self.assertEqual(config, child.parent)

    def test_parent_after_remove_config(self):
        child = MemoryConfig()

        config = CompositeConfig()
        config.add_config('cfg', child)
        config.remove_config('cfg')

        self.assertIsNone(child.parent)

    def test_load_on_add_true_after_add_config(self):
        import sys
        sys.argv = ['key=value']

        config = CompositeConfig(load_on_add=True)
        config.add_config('cmd', CommandLineConfig())

        self.assertEqual('value', config.get('key'))

    def test_load_on_add_false_after_add_config(self):
        import sys
        sys.argv = ['key=value']

        config = CompositeConfig(load_on_add=False)
        config.add_config('cmd', CommandLineConfig())

        self.assertIsNone(config.get('key'))

    def test_updated_after_add_config(self):
        child = MemoryConfig()

        config = CompositeConfig()
        config.add_config('mem', child)

        passed = []
        config.updated.add(lambda: passed.append(True))

        child.set('key', 'value')

        self.assertEqual(1, len(passed))

    def test_updated_after_remove_config(self):
        child = MemoryConfig()

        config = CompositeConfig()
        config.add_config('mem', child)
        config.remove_config('mem')

        passed = []
        config.updated.add(lambda cfg: passed.append(True))

        child.set('key', 'value')

        self.assertEqual(0, len(passed))

    def test_get_with_none_as_name(self):
        config = CompositeConfig()
        with self.assertRaises(TypeError):
            config.get(None)

    def test_get_with_non_str_as_name(self):
        config = CompositeConfig()
        with self.assertRaises(TypeError):
            config.get(1234)

    def test_get_with_existent_key(self):
        config = CompositeConfig()
        config.add_config('mem', MemoryConfig(data={'key': 1}))

        self.assertEqual(1, config.get('key'))

    def test_get_with_nonexistent_key(self):
        config = CompositeConfig()
        config.add_config('mem', MemoryConfig())

        self.assertIsNone(config.get('key'))

    def test_get_with_default_value(self):
        config = CompositeConfig()
        config.add_config('mem', MemoryConfig())

        self.assertEqual(2, config.get('key', default=2))

    def test_get_with_cast(self):
        config = CompositeConfig()
        config.add_config('mem', MemoryConfig(data={'key': 1}))

        self.assertEqual('1', config.get('key', cast=str))

    def test_get_with_overridden_key(self):
        config = CompositeConfig()
        config.add_config('mem1', MemoryConfig(data={'key': 1}))
        config.add_config('mem2', MemoryConfig(data={'key': 2}))

        self.assertEqual(2, config.get('key'))

    def test_get_before_loading(self):
        import sys
        sys.argv = ['key1=value']

        config = CommandLineConfig()
        self.assertIsNone(config.get('key1'))

    def test_get_after_loading(self):
        import sys
        sys.argv = ['key1=value']

        config = CommandLineConfig()
        config.load()

        self.assertEqual('value', config.get('key1'))


class TestEnvironmentConfig(TestCase, BaseDataConfigMixin):
    def setUp(self):
        self._base_config = EnvironmentConfig()

    def tearDown(self):
        import os
        os.environ.pop('key_str', None)
        os.environ.pop('key_int', None)
        os.environ.pop('key_interpolated', None)

    def _load_config(self):
        import os
        os.environ['key_str'] = 'value'
        os.environ['key_int'] = '1'
        os.environ['key_interpolated'] = '{key_str}'

        self._base_config.load()


class TestFileConfig(TestCase, BaseDataConfigMixin, AtNextMixin):
    def setUp(self):
        self._base_config = FileConfig('./tests/config/files/config.json')

    def test_filename_with_none_as_value(self):
        self.assertRaises(TypeError, FileConfig, filename=None)

    def test_filename_with_non_str_as_value(self):
        self.assertRaises(TypeError, FileConfig, filename=123)

    def test_filename_with_unknown_extension_and_without_reader(self):
        config = FileConfig(filename='config.unk')
        with self.assertRaises(ConfigError):
            config.load()

    def test_filename_without_extension_and_reader(self):
        config = FileConfig(filename='config')
        with self.assertRaises(ConfigError):
            config.load()

    def test_reader_with_non_reader_as_value(self):
        self.assertRaises(TypeError, FileConfig, filename='config.json', reader='non reader')

    def test_get_filename_with_value(self):
        config = FileConfig('config.json')
        self.assertEqual('config.json', config.filename)


class TestMemoryConfig(TestCase, BaseDataConfigMixin):
    def setUp(self):
        self._base_config = MemoryConfig()

    def _load_config(self):
        self._base_config.set('key_str', 'value')
        self._base_config.set('key_int', 1)
        self._base_config.set('key_interpolated', '{key_str}')

    def test_none_as_initial_data(self):
        config = MemoryConfig(data=None)
        self.assertIsNone(config.get('key1'))

    def test_non_dict_as_initial_data(self):
        self.assertRaises(TypeError, MemoryConfig, data='non dict')

    def test_dict_as_initial_data(self):
        data = {'key1': 'value'}
        config = MemoryConfig(data)

        self.assertEqual('value', config.get('key1'))

        config.set('key1', 'value1')

        self.assertEqual('value1', config.get('key1'))

        # the initial dict should be cloned by MemoryConfig
        self.assertEqual(data['key1'], 'value')

    def test_load(self):
        # it should do nothing
        MemoryConfig().load()

    def test_set_with_none_as_key(self):
        config = MemoryConfig()
        self.assertRaises(TypeError, config.set, key=None, value='value')

    def test_set_with_non_str_as_key(self):
        config = MemoryConfig()
        self.assertRaises(TypeError, config.set, key=123, value='value')

    def test_set_with_valid_parameters(self):
        config = MemoryConfig()
        config.set('key1', 'value1')
        self.assertEqual('value1', config.get('key1'))

    def test_set_with_updated_event_triggered(self):
        passed = []

        def on_updated():
            passed.append(True)

        config = MemoryConfig()
        config.updated.add(on_updated)
        config.set('key1', 'value1')

        self.assertEqual(1, len(passed))


class TestPollingConfig(TestCase):
    def test_scheduler_with_none_as_value(self):
        self.assertRaises(TypeError, PollingConfig, scheduler=None)

    def test_scheduler_with_non_bool_value(self):
        self.assertRaises(TypeError, PollingConfig, scheduler='non bool')
