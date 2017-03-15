from __future__ import absolute_import

import os
import sys
import time

from central.config import (
    CommandLineConfig, CompositeConfig, EnvironmentConfig, FileConfig, MemoryConfig, PrefixedConfig,
    ReloadConfig, UrlConfig
)
from central import abc
from central.config.core import BaseConfig
from central.exceptions import ConfigError
from central.readers import JsonReader
from central.schedulers import FixedIntervalScheduler
from io import BytesIO
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
                'key_interpolated={key_str}',
                'key_parent.key_child=child'
            ]
            config.load()

        return config


class TestCompositeConfig(TestCase, BaseConfigMixin):
    def test_auto_load_with_none_as_value(self):
        self.assertRaises(TypeError, CompositeConfig, auto_load=None)

    def test_auto_load_with_string_as_value(self):
        with self.assertRaises(TypeError):
            CompositeConfig(auto_load='non bool')

    def test_default_load_on_add(self):
        self.assertFalse(CompositeConfig().load_on_add)

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

    def test_get_value_with_overridden_key(self):
        config = CompositeConfig()
        config.add_config('mem1', MemoryConfig(data={'key': 1}))
        config.add_config('mem2', MemoryConfig(data={'key': 2}))

        self.assertEqual(2, config.get_value('key', int))

    def test_load_on_add_with_none_as_value(self):
        with self.assertRaises(TypeError):
            CompositeConfig(load_on_add=None)

    def test_load_on_add_with_string_as_value(self):
        with self.assertRaises(TypeError):
            CompositeConfig(load_on_add='non bool')

    def test_load_on_add_true_after_add_config(self):
        os.environ['key'] = 'value'

        config = CompositeConfig(load_on_add=True)
        config.add_config('env', EnvironmentConfig())

        self.assertEqual('value', config['key'])

    def test_load_on_add_false_after_add_config(self):
        os.environ['key'] = 'value'

        config = CompositeConfig(load_on_add=False)
        config.add_config('env', EnvironmentConfig())

        with self.assertRaises(KeyError):
            config['key']

    def test_load_with_children(self):
        os.environ['key'] = 'value'

        config = CompositeConfig()
        config.add_config('env', EnvironmentConfig())
        config.load()

        self.assertEqual('value', config['key'])

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

    def _create_base_config(self, load_data=False):
        config = CompositeConfig()

        if load_data:
            config.add_config('mem1', MemoryConfig(data={
                'key_str': 'value',
                'key_int': 1,
                'key_int_as_str': '1',
                'key_dict_as_str': 'item_key=value',
                'key_list_as_str': 'item1,item2'}))
            config.add_config('mem2', MemoryConfig(data={
                'key_interpolated': '{key_str}',
                'key_parent': {'key_child': 'child'}}))

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
            os.environ['key_interpolated'] = '{key_str}'
            os.environ['key_parent.key_child'] = 'child'
            config.load()

        return config


class TestFileConfig(TestCase, BaseDataConfigMixin, NextMixin):
    def test_init_filename_with_none_value(self):
        with self.assertRaises(TypeError):
            FileConfig(filename=None)

    def test_init_filename_with_int_value(self):
        with self.assertRaises(TypeError):
            FileConfig(filename=123)

    def test_init_filename_with_str_value(self):
        config = FileConfig('config.json')
        self.assertEqual('config.json', config.filename)

    def test_get_reader_with_default_value(self):
        config = FileConfig('config.json')
        self.assertIsNone(config.reader)

    def test_init_reader_with_str_value(self):
        with self.assertRaises(TypeError):
            FileConfig('config.json', reader='non reader')

    def test_init_reader_with_reader_value(self):
        reader = JsonReader()
        config = FileConfig('config.json', reader=reader)
        self.assertEqual(reader, config.reader)

    def test_get_paths_with_default_values(self):
        config = FileConfig('config.json')
        self.assertEqual((), config.paths)

    def test_init_paths_with_str_value(self):
        with self.assertRaises(TypeError):
            FileConfig('config.json', paths='non list')

    def test_init_paths_with_list_value(self):
        config = FileConfig('config.json', paths=['${HOME}'])
        self.assertEqual(('${HOME}',), config.paths)

    def test_load_with_unknown_file_extension(self):
        class Config(FileConfig):
            def _find_file(self, filename, paths):
                return filename

            def _open_file(self, filename):
                return BytesIO()

        config = Config('./config.unk')
        with self.assertRaises(ConfigError):
            config.load()

    def test_load_with_file_not_found(self):
        config = FileConfig('not_found')
        with self.assertRaises(ConfigError):
            config.load()

    def test_load_without_file_extension(self):
        class Config(FileConfig):
            def _find_file(self, filename, paths):
                return filename

        config = Config('./config')
        with self.assertRaises(ConfigError):
            config.load()

    def test_load_without_file_extension_and_custom_reader(self):
        class Config(FileConfig):
            def _find_file(self, filename, paths):
                return filename

            def _open_file(self, filename):
                stream = BytesIO()
                stream.write(b'{"key": "value"}')
                stream.seek(0, 0)
                return stream

        config = Config('./config', reader=JsonReader())
        config.load()

        self.assertEqual('value', config['key'])

    def test_load_with_real_file(self):
        import tempfile
        with tempfile.NamedTemporaryFile() as f:
            f.write(b'{"key": "value"}')
            f.flush()

            config = FileConfig(f.name, reader=JsonReader())
            config.load()

            self.assertEqual('value', config['key'])

    def test_load_with_reader_case_sensitive(self):
        class Config(FileConfig):
            def _find_file(self, filename, paths):
                return filename

            def _open_file(self, filename):
                stream = BytesIO()
                stream.write(b'''{"Key": "value"}''')
                stream.seek(0, 0)
                return stream

        class Reader(abc.Reader):
            def read(self, stream):
                import json
                return json.load(stream)

        config = Config('config.json', reader=Reader())
        config.load()

        self.assertEqual('value', config['KEY'])

    def _create_base_config(self, load_data=False):
        class Config(FileConfig):
            def _find_file(self, filename, paths):
                return filename

            def _open_file(self, filename):
                if filename == './config.json':
                    stream = BytesIO()
                    stream.write(b'''
                    {
                      "key_str": "value",
                      "key_int": 1,
                      "key_int_as_str": "1",
                      "key_dict_as_str": "item_key=value",
                      "key_list_as_str": "item1,item2",
                      "key_interpolated": "{key_str}",
                      "key_overridden": "value not overridden",
                      "key_parent": {"key_child": "child"},
                      "@next": "./config.next.json"
                    }''')
                    stream.seek(0, 0)
                    return stream

                if filename == './config.next.json':
                    stream = BytesIO()
                    stream.write(b'''
                    {
                      "key_new": "new value",
                      "key_overridden": "value overridden"
                    }
                    ''')
                    stream.seek(0, 0)
                    return stream

                raise Exception('Invalid filename ' + filename)

        config = Config('./config.json')

        if load_data:
            config.load()

        return config

    def _create_config_with_invalid_next(self):
        class Config(FileConfig):
            def _find_file(self, filename, paths):
                return filename

            def _open_file(self, filename):
                stream = BytesIO()
                stream.write(b'''
                {
                  "@next": 123
                }
                ''')
                stream.seek(0, 0)
                return stream

        return Config('./config.json')


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
            config.set('key_dict_as_str', 'item_key=value')
            config.set('key_list_as_str', 'item1,item2')
            config.set('key_interpolated', '{key_str}')
            config.set('key_parent', {'key_child': 'child'})

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
        config = EnvironmentConfig().reload_every(5)
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
        config = MemoryConfig().reload_every(5)

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
            config.set('key_dict_as_str', 'item_key=value')
            config.set('key_list_as_str', 'item1,item2')
            config.set('key_interpolated', '{key_str}')
            config.set('key_parent', {'key_child': 'child'})

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
                'key_dict_as_str': 'item_key=value',
                'key_list_as_str': 'item1,item2',
                'key_interpolated': '{key_str}',
                'key_parent': {'key_child': 'child'}
            })
            config.set('prefix.nested_delimited', 'value')

        prefixed = config.prefixed('prefix')

        if load_data:
            prefixed.load()

        return prefixed


class TestUrlConfig(TestCase, BaseDataConfigMixin, NextMixin):
    def test_init_url_with_none_value(self):
        with self.assertRaises(TypeError):
            UrlConfig(url=None)

    def test_init_url_with_int_value(self):
        with self.assertRaises(TypeError):
            UrlConfig(url=123)

    def test_init_url_with_str_value(self):
        config = UrlConfig('http://config.json')
        self.assertEqual('http://config.json', config.url)

    def test_get_reader_with_default_value(self):
        config = UrlConfig('http://config.json')
        self.assertIsNone(config.reader)

    def test_init_reader_with_str_as_value(self):
        with self.assertRaises(TypeError):
            UrlConfig('http://config.json', reader='non reader')

    def test_init_reader_with_reader_value(self):
        reader = JsonReader()
        config = UrlConfig('http://config.json', reader=reader)
        self.assertEqual(reader, config.reader)

    def test_load_with_url_extension(self):
        class Config(UrlConfig):
            def _open_url(self, url):
                content_type = None
                stream = BytesIO()
                stream.write(
                    b'''{
                        "key_str": "value"
                    }''')
                stream.seek(0, 0)
                return content_type, stream

        config = Config('http://example.com/config.json')
        config.load()

    def test_load_with_url_extension_and_invalid_content_type(self):
        class Config(UrlConfig):
            def _open_url(self, url):
                content_type = 'application/unknown'
                stream = BytesIO()
                stream.write(
                    b'''{
                        "key_str": "value"
                    }''')
                stream.seek(0, 0)
                return content_type, stream

        config = Config('http://example.com/config.json')
        config.load()

        self.assertEqual('value', config['key_str'])

    def test_load_without_url_extension_and_no_content_type(self):
        class Config(UrlConfig):
            def _open_url(self, url):
                content_type = None
                stream = BytesIO()
                stream.write(
                    b'''{
                        "key_str": "value"
                    }''')
                stream.seek(0, 0)
                return content_type, stream

        config = Config('http://example.com/config')

        with self.assertRaises(ConfigError):
            config.load()

    def test_load_without_url_extension_and_content_type_with_encoding(self):
        class Config(UrlConfig):
            def _open_url(self, url):
                content_type = 'application/json;charset=utf-8'
                stream = BytesIO()
                stream.write(
                    b'''{
                        "key_str": "value"
                    }''')
                stream.seek(0, 0)
                return content_type, stream

        config = Config('http://example.com/config')
        config.load()

        self.assertEqual('value', config['key_str'])

    def test_load_without_url_extension_and_invalid_content_type(self):
        class Config(UrlConfig):
            def _open_url(self, url):
                content_type = 'application/unknown'
                stream = BytesIO()
                stream.write(
                    b'''{
                        "key_str": "value"
                    }''')
                stream.seek(0, 0)
                return content_type, stream

        config = Config('http://example.com/config')

        with self.assertRaises(ConfigError):
            config.load()

    def test_load_without_url_extension_and_custom_reader(self):
        class Config(UrlConfig):
            def _open_url(self, url):
                content_type = None
                stream = BytesIO()
                stream.write(
                    b'''{
                        "key_str": "value"
                    }''')
                stream.seek(0, 0)
                return content_type, stream

        config = Config('http://example.com/config', reader=JsonReader())
        config.load()

    def test_load_without_url_extension_and_dotted_content_type(self):
        class Config(UrlConfig):
            def _open_url(self, url):
                content_type = 'application/vnd.json'
                stream = BytesIO()
                stream.write(
                    b'''{
                        "key_str": "value"
                    }''')
                stream.seek(0, 0)
                return content_type, stream

        config = Config('http://example.com/config')
        config.load()

        self.assertEqual('value', config['key_str'])

    def test_load_without_url_extension_and_dashed_content_type(self):
        class Config(UrlConfig):
            def _open_url(self, url):
                content_type = 'application/vnd-json'
                stream = BytesIO()
                stream.write(
                    b'''{
                        "key_str": "value"
                    }''')
                stream.seek(0, 0)
                return content_type, stream

        config = Config('http://example.com/config')
        config.load()

        self.assertEqual('value', config['key_str'])

    def test_load_without_url_extension_and_invalid_charset(self):
        class Config(UrlConfig):
            def _open_url(self, url):
                content_type = 'application/json;other-key;charset=unknowm'
                stream = BytesIO()
                stream.write(
                    b'''{
                        "key_str": "value"
                    }''')
                stream.seek(0, 0)
                return content_type, stream

        config = Config('http://example.com/config')

        with self.assertRaises(LookupError):
            config.load()

    def test_load_with_reader_case_sensitive(self):
        class Config(UrlConfig):
            def _open_url(self, url):
                stream = BytesIO()
                stream.write(b'''{"Key": "value"}''')
                stream.seek(0, 0)
                return 'application/json', stream

        class Reader(abc.Reader):
            def read(self, stream):
                import json
                return json.load(stream)

        config = Config('http://test.com/config', reader=Reader())
        config.load()

        self.assertEqual('value', config['KEY'])

    def test_load_real_url(self):
        config = UrlConfig('http://date.jsontest.com/')
        config.load()
        self.assertIsNotNone(config['time'])

    def _create_base_config(self, load_data=False):
        class Config(UrlConfig):
            def _open_url(self, url):
                if url == 'http://example.com/config.json':
                    content_type = 'application/json'
                    stream = BytesIO()
                    stream.write(
                        b'''{
                            "key_str": "value",
                            "key_int": 1,
                            "key_int_as_str": "1",
                            "key_dict_as_str": "item_key=value",
                            "key_list_as_str": "item1,item2",
                            "key_interpolated": "{key_str}",
                            "key_overridden": "value not overridden",
                            "key_parent": {"key_child": "child"},
                            "@next": "http://example.com/config.next.json"
                        }''')
                    stream.seek(0, 0)
                    return content_type, stream

                if url == 'http://example.com/config.next.json':
                    content_type = 'application/json'
                    stream = BytesIO()
                    stream.write(
                        b'''{
                            "key_new": "new value",
                            "key_overridden": "value overridden"
                        }''')
                    stream.seek(0, 0)
                    return content_type, stream

                raise Exception('Invalid url ' + url)

        config = Config('http://example.com/config.json')

        if load_data:
            config.load()

        return config

    def _create_config_with_invalid_next(self):
        class Config(UrlConfig):
            def _open_url(self, url):
                content_type = 'application/json'
                stream = BytesIO()
                stream.write(
                    b'''{
                        "@next": 123
                    }''')
                stream.seek(0, 0)
                return content_type, stream

        return Config('http://example.com/config.json')
