"""
SQLAlchemy config implementation.
"""

from .core import BaseDataConfig
from ..compat import string_types
from ..exceptions import LibraryRequiredError
from ..structures import IgnoreCaseDict


try:
    import sqlalchemy
except:
    sqlalchemy = None


__all__ = [
    'SQLAlchemyConfig',
]


class SQLAlchemyConfig(BaseDataConfig):
    """
    A SQLAlchemy configuration based on `BaseDataConfig`.

    The library SQLAlchemy must be installed.

    Example usage:

    .. code-block:: python

        from central.config.database import SQLAlchemyConfig
        from sqlalchemy import create_engine

        engine = create_engine('postgresql://scott:tiger@localhost/test')

        config = SQLAlchemyConfig(engine, 'select key, value from configurations')
        config.load()

        timeout = config.get('timeout')

    :param engine: The SQLAlchemy engine to connect to the database.
    :param str query: The SQL query to obtain properties stored in an RDBMS.
    :param str key_column_name: The column containing the keys.
    :param str value_column_name: The column containing the values.
    """
    def __init__(self, engine, query, key_column_name='key', value_column_name='value'):
        if sqlalchemy is None:
            raise LibraryRequiredError('SQLAlchemy', 'https://pypi.python.org/pypi/SQLAlchemy')

        super(SQLAlchemyConfig, self).__init__()

        if engine is None:
            raise TypeError('engine cannot be None')

        if not isinstance(query, string_types):
            raise TypeError('query must be a str')

        if not isinstance(key_column_name, string_types):
            raise TypeError('key_column_name must be a str')

        if not isinstance(value_column_name, string_types):
            raise TypeError('value_column_name must be a str')

        self._engine = engine
        self._query = query
        self._key_column_name = key_column_name
        self._value_column_name = value_column_name

    @property
    def engine(self):
        """
        Get the SQLAlchemy engine to connect to the database.
        :return: The SQLAlchemy engine to connect to the database.
        """
        return self._engine

    @property
    def query(self):
        """
        Get the SQL query to obtain properties stored in an RDBMS.
        :return str: The SQL query to obtain properties stored in an RDBMS.
        """
        return self._query

    @property
    def key_column_name(self):
        """
        Get the column containing the keys.
        :return str: The column containing the keys.
        """
        return self._key_column_name

    @property
    def value_column_name(self):
        """
        Get the column containing the values.
        :return str: The column containing the values.
        """
        return self._value_column_name

    def load(self):
        """
        Load the configuration stored in the database.
        """
        result = self._engine.execute(self._query)

        try:
            data = IgnoreCaseDict()

            for row in result:
                key = row[self._key_column_name]
                value = row[self._value_column_name]

                data[key] = value

            self._data = data
        finally:
            result.close()
