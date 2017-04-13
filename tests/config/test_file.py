from __future__ import absolute_import

from central.config.file import FileConfig
from central import abc
from central.exceptions import ConfigError
from central.readers import JsonReader
from io import BytesIO
from unittest import TestCase
from .mixins import BaseDataConfigMixin, NextMixin


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

    def test_load_with_unknown_file_extension(self):
        class Config(FileConfig):
            def _find_file(self, filename):
                return filename

            def _open_file(self, filename):
                return BytesIO()

        config = Config('./config.unk')
        with self.assertRaises(ConfigError):
            config.load()

    def test_load_with_file_not_found(self):
        config = FileConfig('not_found')
        with self.assertRaises(FileNotFoundError):
            config.load()

    def test_load_without_file_extension(self):
        class Config(FileConfig):
            def _find_file(self, filename):
                return filename

        config = Config('./config')
        with self.assertRaises(ConfigError):
            config.load()

    def test_load_without_file_extension_and_custom_reader(self):
        class Config(FileConfig):
            def _find_file(self, filename):
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
            def _find_file(self, filename):
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

        with self.assertRaises(ConfigError):
            config.load()

    def _create_base_config(self, load_data=False):
        class Config(FileConfig):
            def _find_file(self, filename):
                return filename

            def _open_file(self, filename):
                if filename == './config.json':
                    stream = BytesIO()
                    stream.write(b'''
                    {
                      "key_str": "value",
                      "key_int": 1,
                      "key_int_as_str": "1",
                      "key_dict": {"key_str": "value"},
                      "key_dict_as_str": "item_key=value",
                      "key_list_as_str": "item1,item2",
                      "key_interpolated": "${key_str}",
                      "key_ignore_case": "value",
                      "key_IGNORE_case": "value1",
                      "key_delimited": {"key_str": "value"},
                      "key_overridden": "value not overridden",
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
            def _find_file(self, filename):
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
