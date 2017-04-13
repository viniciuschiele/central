from __future__ import absolute_import

from central.config.url import UrlConfig
from central import abc
from central.exceptions import ConfigError
from central.readers import JsonReader
from io import BytesIO
from unittest import TestCase
from .mixins import BaseDataConfigMixin, NextMixin


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

        with self.assertRaises(ConfigError):
            config.load()

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
                            "key_dict": {"key_str": "value"},
                            "key_dict_as_str": "item_key=value",
                            "key_list_as_str": "item1,item2",
                            "key_interpolated": "${key_str}",
                            "key_ignore_case": "value",
                            "key_IGNORE_case": "value1",
                            "key_delimited": {"key_str": "value"},
                            "key_overridden": "value not overridden",
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
