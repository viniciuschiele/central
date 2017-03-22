"""
MongoDB config implementation.
"""

from collections import Mapping
from ..compat import string_types, text_type
from ..exceptions import LibraryRequiredError
from ..structures import IgnoreCaseDict
from ..utils import make_ignore_case
from .core import BaseDataConfig

try:
    from pymongo import MongoClient
    from pymongo.collection import Collection
except:
    MongoClient = None


__all__ = [
    'MongoDBConfig',
]


class MongoDBConfig(BaseDataConfig):
    """
    A MongoDB configuration based on `BaseDataConfig`.

    The library pymongo must be installed.

    Example usage:

    .. code-block:: python

        from pymongo import MongoClient

        from central.config.mongodb import MongoDBConfig

        client = MongoClient()
        collection = client.mydatabase.configs

        config = MongoDBConfig(collection)
        config.load()

        value = config.get('database.host')

    :param Collection collection: The MongoDB collection to query the configuration.
    :param Mapping query: The query to obtain properties stored in MongoDB.
    :param str key_attribute: The attribute containing the keys.
    :param str value_attribute: The attribute containing the values.
    """
    def __init__(self, collection, query=None, key_attribute='key', value_attribute='value'):
        if MongoClient is None:
            raise LibraryRequiredError('pymongo', 'https://pypi.python.org/pypi/pymongo')

        super(MongoDBConfig, self).__init__()

        if isinstance(collection, Collection):
            raise TypeError('collection must be a pymongo.collection.Collection')

        if query is not None and isinstance(query, Mapping):
            raise TypeError('collection must be a dict')

        if not isinstance(key_attribute, string_types):
            raise TypeError('key_attribute must be a str')

        if not isinstance(value_attribute, string_types):
            raise TypeError('value_attribute must be a str')

        self._collection = collection
        self._query = query
        self._key_attribute = key_attribute
        self._value_attribute = value_attribute

    @property
    def collection(self):
        """
        Get the MongoDB collection to query the configuration.
        :return Collection: The MongoDB collection.
        """
        return self._collection

    @property
    def query(self):
        """
        Get the query to obtain properties stored in MongoDB.
        :return Mapping: The query to obtain properties stored in MongoDB.
        """
        return self._query

    @property
    def key_attribute(self):
        """
        Get the attribute containing the keys.
        :return str: The attribute containing the keys.
        """
        return self._key_attribute

    @property
    def value_attribute(self):
        """
        Get the attribute containing the values.
        :return str: The attribute containing the values.
        """
        return self._value_attribute

    def load(self):
        """
        Load the configuration stored in the MongoDB.
        :return IgnoreCaseDict: The configuration as a dict.
        """
        result = self._collection.find(self._query)

        data = IgnoreCaseDict()

        for item in result:
            key = text_type(item[self._key_attribute])
            value = item[self._value_attribute]

            if isinstance(value, Mapping):
                value = make_ignore_case(value)

            data[key] = value

        return data
