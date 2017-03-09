from __future__ import absolute_import

from configd.config.s3 import S3Config
from configd.exceptions import ConfigError
from configd.readers import JsonReader
from io import BytesIO
from unittest import TestCase
from .mixins import BaseDataConfigMixin, NextMixin


class TestS3Config(TestCase, BaseDataConfigMixin, NextMixin):
    def setUp(self):
        class S3Resource(object):
            pass
        self.s3 = S3Resource()

    def test_init_client_with_none_value(self):
        with self.assertRaises(TypeError):
            S3Config(client=None, bucket_name='bucket name', filename='config.json')

    def test_init_bucket_name_with_none_value(self):
        with self.assertRaises(TypeError):
            S3Config(client=self.s3, bucket_name=None, filename='config.json')

    def test_init_bucket_name_with_int_value(self):
        with self.assertRaises(TypeError):
            S3Config(client=self.s3, bucket_name=123, filename='config.json')

    def test_init_bucket_name_with_str_value(self):
        config = S3Config(client=self.s3, bucket_name='bucket name', filename='config.json')
        self.assertEqual('bucket name', config.bucket_name)

    def test_init_filename_with_none_value(self):
        with self.assertRaises(TypeError):
            S3Config(client=self.s3, bucket_name='bucket name', filename=None)

    def test_init_filename_with_int_value(self):
        with self.assertRaises(TypeError):
            S3Config(client=self.s3, bucket_name='bucket name', filename=123)

    def test_init_filename_with_str_value(self):
        config = S3Config(client=self.s3, bucket_name='bucket name', filename='config.json')
        self.assertEqual('config.json', config.filename)

    def test_get_reader_with_default_value(self):
        config = S3Config(client=self.s3, bucket_name='bucket name', filename='config.json')
        self.assertIsNone(config.reader)

    def test_init_reader_with_str_value(self):
        with self.assertRaises(TypeError):
            S3Config(client=self.s3, bucket_name='bucket name', filename='config.json', reader='non raeader')

    def test_init_reader_with_reader_value(self):
        reader = JsonReader()
        config = S3Config(client=self.s3, bucket_name='bucket name', filename='config.json', reader=reader)
        self.assertEqual(reader, config.reader)

    def test_load_with_unknown_file_extension(self):
        class Config(S3Config):
            def _read_file(self, filename):
                return BytesIO()

        config = Config(client=self.s3, bucket_name='bucket name', filename='config.unk')
        with self.assertRaises(ConfigError):
            config.load()

    def test_load_with_file_not_found(self):
        class Config(S3Config):
            def _read_file(self, filename):
                raise FileNotFoundError()

        config = Config(client=self.s3, bucket_name='bucket name', filename='not_found')
        with self.assertRaises(ConfigError):
            config.load()

    def test_load_with_custom_reader(self):
        class Config(S3Config):
            def _read_file(self, filename):
                stream = BytesIO()
                stream.write(b'{"key": "value"}')
                stream.seek(0, 0)
                return stream

        config = Config(client=self.s3, bucket_name='bucket name', filename='./config', reader=JsonReader())
        config.load()

        self.assertEqual('value', config.get('key'))

    def test_load_without_file_extension(self):
        config = S3Config(client=self.s3, bucket_name='bucket name', filename='./config')
        with self.assertRaises(ConfigError):
            config.load()

    def _create_base_config(self, load_data=False):
        class Config(S3Config):
            def _read_file(self, filename):
                if filename == './config.json':
                    stream = BytesIO()
                    stream.write(b'''
                    {
                      "key_str": "value",
                      "key_int": 1,
                      "key_int_as_str": "1",
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

        config = Config(client=self.s3, bucket_name='bucket name', filename='./config.json')

        if load_data:
            config.load()

        return config

    def _create_config_with_invalid_next(self):
        class Config(S3Config):
            def _read_file(self, filename):
                stream = BytesIO()
                stream.write(b'''
                {
                  "@next": 123
                }
                ''')
                stream.seek(0, 0)
                return stream

        return Config(client=self.s3, bucket_name='bucket name', filename='./config.json')
