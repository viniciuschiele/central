from __future__ import absolute_import

from central.config.sqlalchemy import SQLAlchemyConfig
from central.exceptions import LibraryRequiredError
from sqlalchemy import create_engine
from unittest import TestCase
from .mixins import BaseDataConfigMixin


class TestSQLAlchemyConfig(TestCase, BaseDataConfigMixin):
    def setUp(self):
        self.engine = create_engine('sqlite:///:memory:')
        self.engine.execute('CREATE TABLE configurations (key TEXT PRIMARY KEY NOT NULL, value TEXT NOT NULL)')

    def test_sqlalchemy_not_installed(self):
        from central.config import sqlalchemy
        sqlalchemy_tmp = sqlalchemy.sqlalchemy
        sqlalchemy.sqlalchemy = None

        with self.assertRaises(LibraryRequiredError):
            SQLAlchemyConfig(self.engine, 'select * from config')

        sqlalchemy.sqlalchemy = sqlalchemy_tmp

    def test_init_engine_with_none_value(self):
        with self.assertRaises(TypeError):
            SQLAlchemyConfig(engine=None, query='select * from config')

    def test_init_engine_with_engine_value(self):
        config = SQLAlchemyConfig(engine=self.engine, query='select * from config')
        self.assertEqual(self.engine, config.engine)

    def test_init_query_with_none_value(self):
        with self.assertRaises(TypeError):
            SQLAlchemyConfig(engine=self.engine, query=None)

    def test_init_query_with_int_value(self):
        with self.assertRaises(TypeError):
            SQLAlchemyConfig(engine=self.engine, query=123)

    def test_init_query_with_str_value(self):
        config = SQLAlchemyConfig(engine=self.engine, query='select * from config')
        self.assertEqual('select * from config', config.query)

    def test_init_key_column_name_with_int_value(self):
        with self.assertRaises(TypeError):
            SQLAlchemyConfig(engine=self.engine, query='select * from config', key_column_name=123)

    def test_init_key_column_name_with_str_value(self):
        config = SQLAlchemyConfig(engine=self.engine, query='select * from config', key_column_name='property_key')
        self.assertEqual('property_key', config.key_column_name)

    def test_get_key_column_name_with_default_value(self):
        config = SQLAlchemyConfig(engine=self.engine, query='select * from config')
        self.assertEqual('key', config.key_column_name)

    def test_init_value_column_name_with_int_value(self):
        with self.assertRaises(TypeError):
            SQLAlchemyConfig(engine=self.engine, query='select * from config', value_column_name=123)

    def test_init_value_column_name_with_str_value(self):
        config = SQLAlchemyConfig(engine=self.engine, query='select * from config', value_column_name='property_value')
        self.assertEqual('property_value', config.value_column_name)

    def test_get_value_column_name_with_default_value(self):
        config = SQLAlchemyConfig(engine=self.engine, query='select * from config')
        self.assertEqual('value', config.value_column_name)

    def _create_base_config(self, load_data=False):
        engine = create_engine('sqlite:///:memory:')
        engine.execute('CREATE TABLE configurations (key TEXT PRIMARY KEY NOT NULL, value TEXT NOT NULL)')

        engine.execute('INSERT INTO configurations VALUES ("key_str",  "value")')
        engine.execute('INSERT INTO configurations VALUES ("key_int",  "1")')
        engine.execute('INSERT INTO configurations VALUES ("key_int_as_str",  "1")')
        engine.execute('INSERT INTO configurations VALUES ("key_dict",  "key_str=value")')
        engine.execute('INSERT INTO configurations VALUES ("key_dict_as_str",  "item_key=value")')
        engine.execute('INSERT INTO configurations VALUES ("key_list_as_str",  "item1,item2")')
        engine.execute('INSERT INTO configurations VALUES ("key_interpolated",  "${key_str}")')
        engine.execute('INSERT INTO configurations VALUES ("key_ignore_case",  "value")')
        engine.execute('INSERT INTO configurations VALUES ("key_IGNORE_case",  "value1")')
        engine.execute('INSERT INTO configurations VALUES ("key_delimited.key_str",  "value")')

        config = SQLAlchemyConfig(engine, 'select * from configurations')

        if load_data:
            config.load()

        return config
