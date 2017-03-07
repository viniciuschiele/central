from __future__ import absolute_import

import os
import sys

from configd.config import (
    CommandLineConfig, CompositeConfig, EnvironmentConfig, FileConfig, MemoryConfig, PollingConfig, PrefixedConfig
)
from configd.decoders import Decoder
from configd.exceptions import ConfigError
from configd.interpolation import StrInterpolator, ConfigStrLookup
from configd.schedulers import FixedIntervalScheduler
from configd.utils.event import EventHandler
from unittest import TestCase


class BaseConfigMixin(object):
    def _create_empty_config(self):
        raise NotImplementedError()

    def _load_config(self, config):
        config.load()

    def test_default_lookup(self):
        config = self._create_empty_config()
        self.assertTrue(isinstance(config.lookup, ConfigStrLookup))

    def test_set_lookup_with_lookup_as_value(self):
        config = self._create_empty_config()

        lookup = MemoryConfig().lookup
        config.lookup = lookup

        self.assertEqual(lookup, config.lookup)

    def test_set_lookup_with_none_as_value(self):
        config = self._create_empty_config()
        config.lookup = None
        self.assertTrue(isinstance(config.lookup, ConfigStrLookup))

    def test_set_lookup_with_string_as_value(self):
        config = self._create_empty_config()
        with self.assertRaises(TypeError):
            config.lookup = 'non config'

    def test_default_updated(self):
        config = self._create_empty_config()
        self.assertEqual(EventHandler, type(config.updated))

    def test_on_updated(self):
        def dummy():
            pass

        config = self._create_empty_config()
        config.on_updated(dummy)

        self.assertEqual(1, len(config.updated))

    def test_polling_with_valid_args(self):
        config = self._create_empty_config().polling(12345)
        self.assertTrue(isinstance(config, PollingConfig))
        self.assertEqual(12345, config.scheduler.interval)

    def test_prefixed_with_valid_args(self):
        config = self._create_empty_config().prefixed('database')
        self.assertTrue(isinstance(config, PrefixedConfig))
        self.assertEqual('database.', config.prefix)

    def test_get_with_none_as_name(self):
        config = self._create_empty_config()
        with self.assertRaises(TypeError):
            config.get(None)

    def test_get_with_integer_as_name(self):
        config = self._create_empty_config()
        with self.assertRaises(TypeError):
            config.get(1234)

    def test_get_with_existent_key(self):
        config = self._create_empty_config()
        self._load_config(config)
        self.assertEqual('value', config.get('key_str'))

    def test_get_with_nonexistent_key(self):
        config = self._create_empty_config()
        self.assertIsNone(config.get('not_found'))

    def test_get_with_default_value(self):
        config = self._create_empty_config()
        self.assertEqual(2, config.get('not_found', default=2))

    def test_get_with_cast(self):
        config = self._create_empty_config()
        self._load_config(config)
        self.assertEqual('1', config.get('key_int', cast=str))

    def test_get_before_loading(self):
        config = self._create_empty_config()
        self.assertIsNone(config.get('key_int'))

    def test_get_after_loading(self):
        config = self._create_empty_config()
        self._load_config(config)
        self.assertEqual('value', config.get('key_str'))

    def test_get_with_interpolation(self):
        config = self._create_empty_config()
        self._load_config(config)
        self.assertEqual('value', config.get('key_interpolated'))

    def test_get_with_delimited_key(self):
        config = self._create_empty_config()
        self._load_config(config)
        self.assertEqual('child', config.get('key_parent.key_child', cast=str))

    def test_get_with_delimited_key_and_nested_key_not_found(self):
        config = self._create_empty_config()
        self._load_config(config)
        self.assertIsNone(config.get('key_parent.not_found', cast=str))

    def test_get_with_delimited_key_and_root_key_not_dict(self):
        config = self._create_empty_config()
        self._load_config(config)
        self.assertIsNone(config.get('key_str.other_key', cast=str))


class BaseDataConfigMixin(BaseConfigMixin):
    def test_default_decoder(self):
        config = self._create_empty_config()
        self.assertEqual(Decoder, type(config.decoder))

    def test_set_decoder_with_decoder_as_value(self):
        config = self._create_empty_config()

        decoder = Decoder()
        config.decoder = decoder

        self.assertEqual(decoder, config.decoder)

    def test_set_decoder_with_none_as_value(self):
        config = self._create_empty_config()
        with self.assertRaises(TypeError):
            config.decoder = None

    def test_set_decoder_with_string_as_value(self):
        config = self._create_empty_config()
        with self.assertRaises(TypeError):
            config.decoder = 'non decoder'

    def test_default_interpolator(self):
        config = self._create_empty_config()
        self.assertEqual(StrInterpolator, type(config.interpolator))

    def test_set_interpolator_with_interpolator_as_value(self):
        config = self._create_empty_config()

        interpolator = StrInterpolator()
        config.interpolator = interpolator

        self.assertEqual(interpolator, config.interpolator)

    def test_set_interpolator_with_none_as_value(self):
        config = self._create_empty_config()
        with self.assertRaises(TypeError):
            config.interpolator = None

    def test_set_interpolator_with_string_as_value(self):
        config = self._create_empty_config()
        with self.assertRaises(TypeError):
            config.interpolator = 'non interpolator'


class AtNextMixin(object):
    def _create_config_with_invalid_next(self):
        raise NotImplementedError()

    def test_get_new_key(self):
        config = self._create_empty_config()
        self._load_config(config)
        self.assertEqual('new value', config.get('key_new'))

    def test_get_overridden_key(self):
        config = self._create_empty_config()
        self._load_config(config)
        self.assertEqual('value overridden', config.get('key_overridden'))

    def test_invalid_next(self):
        config = self._create_config_with_invalid_next()
        with self.assertRaises(ConfigError):
            config.load()


class TestCommandLineConfig(TestCase, BaseDataConfigMixin):
    def tearDown(self):
        sys.argv = []

    def _create_empty_config(self):
        return CommandLineConfig()

    def _load_config(self, config):
        sys.argv = ['key_str=value',
                    'key_int=1',
                    'key_interpolated={key_str}',
                    'key_parent.key_child=child',
                    ]
        config.load()

    def test_argument_without_equal_operator(self):
        sys.argv = ['key1']

        config = CommandLineConfig()
        config.load()

        self.assertIsNone(config.get('key1'))

    def test_argument_without_key(self):
        sys.argv = ['=value']

        config = CommandLineConfig()
        config.load()

        self.assertIsNone(config.get('key1'))

    def test_argument_without_value(self):
        sys.argv = ['key1=']

        config = CommandLineConfig()
        config.load()

        self.assertEqual('', config.get('key1'))


class TestCompositeConfig(TestCase):
    def test_auto_load_with_none_as_value(self):
        self.assertRaises(TypeError, CompositeConfig, auto_load=None)

    def test_auto_load_with_string_as_value(self):
        with self.assertRaises(TypeError):
            CompositeConfig(auto_load='non bool')

    def test_default_load_on_add(self):
        self.assertFalse(CompositeConfig().load_on_add)

    def test_default_lookup(self):
        self.assertTrue(isinstance(CompositeConfig().lookup, ConfigStrLookup))

    def test_set_lookup_with_lookup_as_value(self):
        lookup = MemoryConfig().lookup
        config = CompositeConfig()
        config.lookup = lookup

        self.assertEqual(lookup, config.lookup)

    def test_set_lookup_with_none_as_value(self):
        config = CompositeConfig()
        config.lookup = None
        self.assertTrue(isinstance(config.lookup, ConfigStrLookup))

    def test_set_lookup_with_string_as_value(self):
        with self.assertRaises(TypeError):
            config = CompositeConfig()
            config.lookup = 'non lookup'

    def test_add_config(self):
        child = MemoryConfig()
        config = CompositeConfig()
        config.add_config('mem', child)

        self.assertEqual(child, config.get_config('mem'))

    def test_add_config_with_none_as_name(self):
        config = CompositeConfig()
        with self.assertRaises(TypeError):
            config.add_config(None, MemoryConfig())

    def test_add_config_with_integer_as_name(self):
        config = CompositeConfig()
        with self.assertRaises(TypeError):
            config.add_config(1234, MemoryConfig())

    def test_add_config_with_none_as_config(self):
        config = CompositeConfig()
        with self.assertRaises(TypeError):
            config.add_config('cfg', None)

    def test_add_config_with_string_as_config(self):
        config = CompositeConfig()
        with self.assertRaises(TypeError):
            config.add_config('cfg', 'non config')

    def test_add_config_with_duplicated_name(self):
        config = CompositeConfig()
        config.add_config('cfg', MemoryConfig())
        with self.assertRaises(ConfigError):
            config.add_config('cfg', MemoryConfig())

    def test_get_config_with_none_as_name(self):
        config = CompositeConfig()
        with self.assertRaises(TypeError):
            config.get_config(None)

    def test_get_config_with_integer_as_name(self):
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

    def test_remove_config_with_integer_as_name(self):
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

    def test_lookup_after_add_config(self):
        child = MemoryConfig()

        config = CompositeConfig()
        config.add_config('cfg', child)

        self.assertEqual(config.lookup, child.lookup)

    def test_lookup_after_remove_config(self):
        child = MemoryConfig()

        config = CompositeConfig()
        config.add_config('cfg', child)
        config.remove_config('cfg')

        self.assertNotEqual(config.lookup, child.lookup)

    def test_load_on_add_with_none_as_value(self):
        with self.assertRaises(TypeError):
            CompositeConfig(load_on_add=None)

    def test_load_on_add_with_string_as_value(self):
        with self.assertRaises(TypeError):
            CompositeConfig(load_on_add='non bool')

    def test_load_on_add_true_after_add_config(self):
        sys.argv = ['key=value']

        config = CompositeConfig(load_on_add=True)
        config.add_config('cmd', CommandLineConfig())

        self.assertEqual('value', config.get('key'))

    def test_load_on_add_false_after_add_config(self):
        sys.argv = ['key=value']

        config = CompositeConfig(load_on_add=False)
        config.add_config('cmd', CommandLineConfig())

        self.assertIsNone(config.get('key'))

    def test_load_with_children(self):
        os.environ['key'] = 'value'

        config = CompositeConfig()
        config.add_config('env', EnvironmentConfig())
        config.load()

        self.assertEqual('value', config.get('key'))

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

    def test_get_with_integer_as_name(self):
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
        sys.argv = ['key1=value']

        config = CommandLineConfig()
        self.assertIsNone(config.get('key1'))

    def test_get_after_loading(self):
        sys.argv = ['key1=value']

        config = CommandLineConfig()
        config.load()

        self.assertEqual('value', config.get('key1'))


class TestEnvironmentConfig(TestCase, BaseDataConfigMixin):
    def tearDown(self):
        os.environ.pop('key_str', None)
        os.environ.pop('key_int', None)
        os.environ.pop('key_interpolated', None)

    def _create_empty_config(self):
        return EnvironmentConfig()

    def _load_config(self, config):
        os.environ['key_str'] = 'value'
        os.environ['key_int'] = '1'
        os.environ['key_interpolated'] = '{key_str}'
        os.environ['key_parent.key_child'] = 'child'

        config.load()


class TestFileConfig(TestCase, BaseDataConfigMixin, AtNextMixin):
    def _create_empty_config(self):
        return FileConfig('./tests/config/files/config.json')

    def _create_config_with_invalid_next(self):
        return FileConfig('./tests/config/files/config.invalid_next.json')

    def _load_config(self, config):
        config.load()

    def test_filename_with_none_as_value(self):
        with self.assertRaises(TypeError):
            FileConfig(filename=None)

    def test_filename_with_integer_as_value(self):
        with self.assertRaises(TypeError):
            FileConfig(filename=123)

    def test_filename_with_valid_value(self):
        config = FileConfig('config.json')
        self.assertEqual('config.json', config.filename)

    def test_default_reader(self):
        config = FileConfig('config.json')
        self.assertIsNone(config.reader)

    def test_reader_with_string_as_value(self):
        with self.assertRaises(TypeError):
            FileConfig(filename='config.json', reader='non reader')

    def test_default_paths(self):
        config = FileConfig(filename='config.json')
        self.assertEqual((), config.paths)

    def test_paths_with_string_as_value(self):
        with self.assertRaises(TypeError):
            FileConfig('config.json', paths='non list')

    def test_paths_with_list_as_value(self):
        config = FileConfig('config.json', paths=['${HOME}'])
        self.assertEqual(('${HOME}',), config.paths)

    def test_load_filename_with_unknown_extension(self):
        config = FileConfig('./tests/config/files/config.unk')
        with self.assertRaises(ConfigError):
            config.load()

    def test_load_filename_without_extension(self):
        config = FileConfig('./tests/config/files/config_without_extension')
        with self.assertRaises(ConfigError):
            config.load()

    def test_load_filename_not_found(self):
        config = FileConfig('not_found')
        with self.assertRaises(FileNotFoundError):
            config.load()


class TestMemoryConfig(TestCase, BaseDataConfigMixin):
    def _create_empty_config(self):
        return MemoryConfig()

    def _load_config(self, config):
        config.set('key_str', 'value')
        config.set('key_int', 1)
        config.set('key_interpolated', '{key_str}')
        config.set('key_parent', {'key_child': 'child'})

    def test_none_as_initial_data(self):
        config = MemoryConfig(data=None)
        self.assertIsNone(config.get('key1'))

    def test_string_as_initial_data(self):
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

    def test_set_with_integer_as_key(self):
        with self.assertRaises(TypeError):
            config = MemoryConfig()
            config.set(key=123, value='value')

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


class TestPollingConfig(TestCase, BaseConfigMixin):
    def _create_empty_config(self):
        return FileConfig('./tests/config/files/config.json').polling(12345)

    def _load_config(self, config):
        config.load()

    def test_config_with_none_as_value(self):
        with self.assertRaises(TypeError):
            PollingConfig(config=None, scheduler=FixedIntervalScheduler())

    def test_config_with_string_as_value(self):
        with self.assertRaises(TypeError):
            PollingConfig(config='non config', scheduler=FixedIntervalScheduler())

    def test_config_with_valid_value(self):
        child = MemoryConfig()
        config = PollingConfig(config=child, scheduler=FixedIntervalScheduler())
        self.assertEqual(child, config.config)

    def test_scheduler_with_none_as_value(self):
        with self.assertRaises(TypeError):
            PollingConfig(MemoryConfig(), scheduler=None)

    def test_scheduler_with_string_as_value(self):
        with self.assertRaises(TypeError):
            PollingConfig(MemoryConfig(), scheduler='non scheduler')
