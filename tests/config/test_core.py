from __future__ import absolute_import

import os
import sys
import time

from central.config import (
    ChainConfig, CommandLineConfig, EnvironmentConfig, MemoryConfig,
    MergeConfig, ModuleConfig, PrefixedConfig, ReloadConfig
)
from central.config.core import BaseConfig
from central.exceptions import ConfigError
from central.schedulers import FixedIntervalScheduler
from central.structures import IgnoreCaseDict
from threading import Event
from unittest import TestCase
from .mixins import BaseConfigMixin, BaseDataConfigMixin, NextMixin


class TestCommandLineConfig(TestCase, BaseDataConfigMixin):
    def tearDown(self):
        sys.argv = []

    def test_dash_argument_with_value(self):
        sys.argv = [
            'filename.py',
            '-key1',
            'value'
        ]

        config = CommandLineConfig()
        config.load()

        self.assertEqual('value', config['key1'])

    def test_dash_argument_without_value(self):
        sys.argv = [
            'filename.py',
            '-key1',
        ]

        config = CommandLineConfig()

        with self.assertRaises(ConfigError):
            config.load()

    def test_dash_dash_argument_with_value(self):
        sys.argv = [
            'filename.py',
            '--key1',
            'value'
        ]

        config = CommandLineConfig()
        config.load()

        self.assertEqual('value', config['key1'])

    def test_dash_dash_argument_without_value(self):
        sys.argv = [
            'filename.py',
            '--key1',
        ]

        config = CommandLineConfig()

        with self.assertRaises(ConfigError):
            config.load()

    def test_two_dash_dash_arguments_without_value(self):
        sys.argv = [
            'filename.py',
            '--key1',
            '--key2',
        ]

        config = CommandLineConfig()
        config.load()

        self.assertEqual('--key2', config['key1'])

    def test_argument_without_equal_operator(self):
        sys.argv = [
            'filename.py',
            'key1'
        ]

        config = CommandLineConfig()

        with self.assertRaises(ConfigError):
            config.load()

    def test_argument_without_key(self):
        sys.argv = [
            'filename.py',
            '=value'
        ]

        config = CommandLineConfig()

        with self.assertRaises(ConfigError):
            config.load()

    def test_argument_without_value(self):
        sys.argv = [
            'filename.py',
            'key1='
        ]

        config = CommandLineConfig()
        config.load()

        self.assertEqual('', config['key1'])

    def _create_base_config(self, load_data=False):
        config = CommandLineConfig()

        if load_data:
            sys.argv = [
                'filename.py',
                'key_str=value',
                'key_int=1',
                'key_int_as_str=1',
                'key_dict_as_str=item_key=value',
                'key_list_as_str=item1,item2',
                'key_interpolated=${key_str}',
                'key_ignore_case=value',
                'key_IGNORE_case=value1',
                'key_delimited.key_str=value'
            ]
            config.load()

        return config


class TestEnvironmentConfig(TestCase, BaseDataConfigMixin):
    def tearDown(self):
        os.environ.pop('key_str', None)
        os.environ.pop('key_int', None)
        os.environ.pop('key_interpolated', None)

    def _create_base_config(self, load_data=False):
        config = EnvironmentConfig()

        if load_data:
            os.environ['key_str'] = 'value'
            os.environ['key_int'] = '1'
            os.environ['key_int_as_str'] = '1'
            os.environ['key_dict_as_str'] = 'item_key=value'
            os.environ['key_list_as_str'] = 'item1,item2'
            os.environ['key_interpolated'] = '${key_str}'
            os.environ['key_ignore_case'] = 'value'
            os.environ['key_IGNORE_case'] = 'value1'
            os.environ['key_delimited.key_str'] = 'value'
            config.load()

        return config


class TestChainConfig(TestCase, BaseConfigMixin):
    def test_configs_with_none_as_value(self):
        with self.assertRaises(TypeError):
            ChainConfig(None)

    def test_configs_with_str_as_value(self):
        with self.assertRaises(TypeError):
            ChainConfig('non configs')

    def test_configs_with_tuple_of_configs_as_value(self):
        child = MemoryConfig()

        config = ChainConfig(child)

        self.assertEqual(id(child), id(config.configs[0]))

    def test_configs_with_list_of_configs_as_value(self):
        child = MemoryConfig()

        config = ChainConfig(child)

        self.assertEqual(id(child), id(config.configs[0]))

    def test_configs_with_list_of_str_as_value(self):
        with self.assertRaises(TypeError):
            ChainConfig(['non config'])

    def test_child_lookup(self):
        child = MemoryConfig()

        config = ChainConfig(child)

        self.assertEqual(config.lookup, child.lookup)

    def test_get_value_with_overridden_key(self):
        config = ChainConfig(
            MemoryConfig(data={'key': 1}),
            MemoryConfig(data={'key': 2})
        )

        self.assertEqual(2, config.get_value('key', int))

    def test_load_with_configs(self):
        os.environ['key'] = 'value'

        config = ChainConfig(EnvironmentConfig())
        config.load()

        self.assertEqual('value', config['key'])

    def test_updated_trigger(self):
        child = MemoryConfig()

        config = ChainConfig(child)

        passed = []
        config.updated.add(lambda: passed.append(True))

        child.set('key', 'value')

        self.assertEqual(1, len(passed))

    def _create_base_config(self, load_data=False):
        if load_data:
            config = ChainConfig(
                MemoryConfig(data={
                    'key_str': 'value',
                    'key_int': 1,
                    'key_int_as_str': '1',
                    'key_dict': {'key_str': 'value'},
                    'key_dict_as_str': 'item_key=value',
                    'key_list_as_str': 'item1,item2'}),

                MemoryConfig(data={
                    'key_interpolated': '${key_str}',
                    'key_ignore_case': 'value',
                    'key_IGNORE_case': 'value1',
                    'key_delimited': {'key_str': 'value'}})
            )
            config.load()
        else:
            config = ChainConfig()

        return config


class TestModuleConfig(TestCase, BaseDataConfigMixin, NextMixin):
    def test_init_name_with_none_value(self):
        with self.assertRaises(TypeError):
            ModuleConfig(name=None)

    def test_init_name_with_int_value(self):
        with self.assertRaises(TypeError):
            ModuleConfig(name=123)

    def test_init_name_with_str_value(self):
        config = ModuleConfig('config.json')
        self.assertEqual('config.json', config.name)

    def test_load_with_module_not_found(self):
        config = ModuleConfig('not_found')
        with self.assertRaises(ImportError):
            config.load()

    def _create_base_config(self, load_data=False):
        class Config(ModuleConfig):
            def _import_module(self, name):
                Object = type('Object', (object,), {})
                if name == 'config':
                    o = Object()
                    o.key_str = 'value'
                    o.key_int = 1
                    o.key_int_as_str = '1'
                    o.key_dict = {'key_str': 'value'}
                    o.key_dict_as_str = 'item_key=value'
                    o.key_list_as_str = 'item1,item2'
                    o.key_interpolated = '${key_str}'
                    o.key_ignore_case = 'value'
                    o.key_IGNORE_case = 'value1'
                    o.key_delimited = {'key_str': 'value'}
                    o.key_overridden = 'value not overridden'
                    o._next = 'config_next'
                    return o

                if name == 'config_next':
                    o = Object()
                    o.key_new = 'new value'
                    o.key_overridden = 'value overridden'
                    return o

                raise Exception('Invalid name ' + name)

        config = Config('config')

        if load_data:
            config.load()

        return config

    def _create_config_with_invalid_next(self):
        Object = type('Object', (object,), {})

        class Config(ModuleConfig):
            def _import_module(self, name):
                o = Object()
                o._next = 123
                return o

        return Config('config')


class TestMemoryConfig(TestCase, BaseDataConfigMixin):
    def test_init_data_with_none_value(self):
        config = MemoryConfig(data=None)
        with self.assertRaises(KeyError):
            config['key1']

    def test_init_data_with_str_value(self):
        with self.assertRaises(TypeError):
            MemoryConfig(data='non dict')

    def test_init_data_with_dict_value(self):
        data = {'key1': 'value'}
        config = MemoryConfig(data)

        self.assertEqual('value', config['key1'])

        config.set('key1', 'value1')

        self.assertEqual('value1', config['key1'])

        # the initial dict should be cloned by MemoryConfig
        self.assertEqual(data['key1'], 'value')

    def test_load(self):
        # it should do nothing
        config = MemoryConfig()
        config.load()

    def test_set_with_key_as_none(self):
        config = MemoryConfig()
        with self.assertRaises(TypeError):
            config.set(key=None, value='value')

    def test_set_with_key_as_int(self):
        config = MemoryConfig()
        with self.assertRaises(TypeError):
            config.set(key=123, value='value')

    def test_set_with_key_as_str(self):
        config = MemoryConfig()
        config.set('key1', 'value1')
        self.assertEqual('value1', config['key1'])

    def test_set_with_dict_as_value(self):
        config = MemoryConfig()
        config.set('key', {'item': {'subitem': 'value'}})
        self.assertIsInstance(config.get('key'), IgnoreCaseDict)
        self.assertIsInstance(config.get('key.item'), IgnoreCaseDict)

    def test_set_with_ignore_case_dict_as_value(self):
        data = IgnoreCaseDict(item='value')

        config = MemoryConfig()
        config.set('key', data)
        self.assertIsInstance(config.get('key'), IgnoreCaseDict)
        self.assertEqual(id(config.get('key')), id(data))

    def test_trigger_updated_event_on_set_key(self):
        ev = Event()

        config = MemoryConfig()

        @config.on_updated
        def on_updated():
            ev.set()

        config.set('key1', 'value1')

        self.assertTrue(ev.is_set)

    def _create_base_config(self, load_data=False):
        config = MemoryConfig()

        if load_data:
            config.set('key_str', 'value')
            config.set('key_int', 1)
            config.set('key_int_as_str', '1')
            config.set('key_dict', {'key_str': 'value'})
            config.set('key_dict_as_str', 'item_key=value')
            config.set('key_list_as_str', 'item1,item2')
            config.set('key_interpolated', '${key_str}')
            config.set('key_ignore_case', 'value')
            config.set('key_IGNORE_case', 'value1')
            config.set('key_delimited', {'key_str': 'value'})

        return config


class TestMergeConfig(TestCase, BaseDataConfigMixin):
    def test_configs_with_none_as_value(self):
        with self.assertRaises(TypeError):
            MergeConfig(None)

    def test_configs_with_str_as_value(self):
        with self.assertRaises(TypeError):
            MergeConfig('non configs')

    def test_configs_with_tuple_of_configs_as_value(self):
        child = MemoryConfig()

        config = MergeConfig(child)

        self.assertEqual(id(child), id(config.configs[0]))

    def test_configs_with_list_of_configs_as_value(self):
        child = MemoryConfig()

        config = MergeConfig(child)

        self.assertEqual(id(child), id(config.configs[0]))

    def test_configs_with_list_of_str_as_value(self):
        with self.assertRaises(TypeError):
            MergeConfig(['non config'])

    def test_child_lookup(self):
        child = MemoryConfig()

        config = MergeConfig(child)

        self.assertEqual(config.lookup, child.lookup)

    def test_get_value_with_overridden_key(self):
        config = MergeConfig(
            MemoryConfig(data={'key': 1}),
            MemoryConfig(data={'key': 2})
        )
        config.load()

        self.assertEqual(2, config.get_value('key', int))

    def test_load_with_configs(self):
        os.environ['key'] = 'value'

        config = MergeConfig(EnvironmentConfig())
        config.load()

        self.assertEqual('value', config['key'])

    def test_updated_trigger(self):
        child = MemoryConfig()

        config = MergeConfig(child)

        passed = []
        config.updated.add(lambda: passed.append(True))

        child.set('key', 'value')

        self.assertEqual(1, len(passed))

    def _create_base_config(self, load_data=False):
        if load_data:
            config = MergeConfig(
                MemoryConfig(data={
                    'key_str': 'value',
                    'key_int': 1,
                    'key_int_as_str': '1',
                    'key_dict': {'key_str': 'value'},
                    'key_dict_as_str': 'item_key=value',
                    'key_list_as_str': 'item1,item2'}),

                MemoryConfig(data={
                    'key_interpolated': '${key_str}',
                    'key_ignore_case': 'value',
                    'key_IGNORE_case': 'value1',
                    'key_delimited': {'key_str': 'value'}
                })
            )
            config.load()
        else:
            config = MergeConfig()

        return config


class TestReloadConfig(TestCase, BaseConfigMixin):
    def test_init_config_with_none_value(self):
        with self.assertRaises(TypeError):
            ReloadConfig(config=None, scheduler=FixedIntervalScheduler())

    def test_init_config_with_str_value(self):
        with self.assertRaises(TypeError):
            ReloadConfig(config='non config', scheduler=FixedIntervalScheduler())

    def test_init_config_with_config_value(self):
        child = MemoryConfig()
        config = ReloadConfig(config=child, scheduler=FixedIntervalScheduler())
        self.assertEqual(child, config.config)

    def test_init_scheduler_with_none_value(self):
        with self.assertRaises(TypeError):
            ReloadConfig(MemoryConfig(), scheduler=None)

    def test_init_scheduler_with_str_value(self):
        with self.assertRaises(TypeError):
            ReloadConfig(MemoryConfig(), scheduler='non scheduler')

    def test_reload(self):
        config = EnvironmentConfig().reload_every(0.005)
        config.load()

        with self.assertRaises(KeyError):
            config['key_str']

        os.environ['key_str'] = 'value'

        time.sleep(0.02)

        self.assertEqual('value', config['key_str'])

    def test_reload_with_load_error(self):
        ev = Event()

        class ErrorConfig(BaseConfig):
            def load(self):
                if ev.is_set():
                    raise MemoryError()
                ev.set()

        config = ErrorConfig().reload_every(5)
        config.load()

        time.sleep(0.02)

        self.assertTrue(ev.is_set())

    def test_reload_with_updated_error(self):
        config = MemoryConfig().reload_every(0.005)

        ev = Event()

        @config.on_updated
        def updated():
            ev.set()
            raise MemoryError()

        config.load()

        time.sleep(0.02)

        self.assertTrue(ev.is_set())

    def _create_base_config(self, load_data=False):
        config = MemoryConfig()

        if load_data:
            config.set('key_str', 'value')
            config.set('key_int', 1)
            config.set('key_int_as_str', '1')
            config.set('key_dict', {'key_str': 'value'})
            config.set('key_dict_as_str', 'item_key=value')
            config.set('key_list_as_str', 'item1,item2')
            config.set('key_interpolated', '${key_str}')
            config.set('key_ignore_case', 'value')
            config.set('key_IGNORE_case', 'value1')
            config.set('key_delimited', {'key_str': 'value'})

        return config.reload_every(12345)


class TestPrefixedConfig(TestCase, BaseConfigMixin):
    def test_init_prefix_with_none_value(self):
        with self.assertRaises(TypeError):
            PrefixedConfig(prefix=None, config=MemoryConfig())

    def test_init_prefix_with_int_value(self):
        with self.assertRaises(TypeError):
            PrefixedConfig(prefix=123, config=MemoryConfig())

    def test_init_prefix_with_str_value(self):
        config = PrefixedConfig('prefix.', config=MemoryConfig())
        self.assertEqual('prefix', config.prefix)

    def test_init_config_with_none_value(self):
        with self.assertRaises(TypeError):
            PrefixedConfig('prefix', config=None)

    def test_init_config_with_str_value(self):
        with self.assertRaises(TypeError):
            PrefixedConfig('prefix', config='non config')

    def test_init_config_with_config_value(self):
        child = MemoryConfig()
        config = PrefixedConfig('prefix', config=child)
        self.assertEqual(child, config.config)

    def _create_base_config(self, load_data=False):
        config = MemoryConfig()

        if load_data:
            config.set('prefix', {
                'key_str': 'value',
                'key_int': 1,
                'key_int_as_str': '1',
                'key_dict': {'key_str': 'value'},
                'key_dict_as_str': 'item_key=value',
                'key_list_as_str': 'item1,item2',
                'key_interpolated': '${key_str}',
                'key_ignore_case': 'value',
                'key_IGNORE_case': 'value1',
                'key_delimited': {'key_str': 'value'}
            })
            config.set('prefix.nested_delimited', 'value')

        prefixed = config.prefixed('prefix')

        if load_data:
            prefixed.load()

        return prefixed
