"""
DynamoDB config implementation.
"""

from ..compat import string_types
from ..exceptions import LibraryRequiredError
from ..structures import IgnoreCaseDict
from .core import BaseDataConfig

try:
    import boto3
    from boto3.dynamodb.conditions import Key
except:
    boto3 = None


__all__ = [
    'DynamoDBConfig',
]


class DynamoDBConfig(BaseDataConfig):
    """
    A DynamoDB configuration based on `BaseDataConfig`.

    The library boto3 must be installed.

    Example usage:

    .. code-block:: python

        import boto3

        from central.config.dynamodb import DynamoDBConfig

        dynamodb = boto3.resource('dynamodb')

        config = DynamoDBConfig(dynamodb, 'configurations')
        config.load()

        value = config.get('key')

    :param client: The boto S3 resource.
    :param str table_name: The DynamoDB table name.
    :param str context_attribute: The context attribute name.
        this is the primary key attribute when you are using primary key and sort key.
    :param str context_value: The value to filter in the context attribute.
        If None, no filter is applied.
    :param str key_attribute: The key attribute name.
    :param str value_attribute: The value attribute name.
    """
    def __init__(self, client, table_name,
                 context_attribute='context', context_value=None,
                 key_attribute='key', value_attribute='value'):
        if boto3 is None:
            raise LibraryRequiredError('boto3', 'https://pypi.python.org/pypi/boto3')

        super(DynamoDBConfig, self).__init__()

        if client is None:
            raise TypeError('client cannot be None')

        if not isinstance(table_name, string_types):
            raise TypeError('table_name must be a str')

        if not isinstance(context_attribute, string_types):
            raise TypeError('context_attribute must be a str')

        if context_value is not None and not isinstance(context_value, string_types):
            raise TypeError('context_value must be a str')

        if not isinstance(key_attribute, string_types):
            raise TypeError('key_attribute must be a str')

        if not isinstance(value_attribute, string_types):
            raise TypeError('value_attribute must be a str')

        self._client = client
        self._table_name = table_name
        self._context_attribute = context_attribute
        self._context_value = context_value
        self._key_attribute = key_attribute
        self._value_attribute = value_attribute

    @property
    def table_name(self):
        """
        Get the DynamoDB table name.
        :return str: The table name.
        """
        return self._table_name

    @property
    def context_attribute(self):
        """
        Get the context attribute name.
        This is the primary key attribute when you are using primary key and sort key.
        :return str: The context attribute name.
        """
        return self._context_attribute

    @property
    def context_value(self):
        """
        Get the value to filter in the context attribute.
        :return str: The value to filter in the context attribute.
        """
        return self._context_value

    @property
    def key_attribute(self):
        """
        Get the key attribute name.
        :return str: The key attribute name.
        """
        return self._key_attribute

    @property
    def value_attribute(self):
        """
        Get the value attribute name.
        :return str: The value attribute name.
        """
        return self._value_attribute

    def _read(self):
        """
        Read the configuration from DynamoDB.
        :return IgnoreCaseDict: The configuration as a dict.
        """
        data = IgnoreCaseDict()

        table = self._client.Table(self._table_name)

        last_evaluated_key = None

        while True:
            if last_evaluated_key is None:
                kwargs = {}
            else:
                kwargs = {'ExclusiveStartKey': last_evaluated_key}

            if self._context_value is None:
                response = table.scan(**kwargs)
            else:
                key_exp = Key(self._context_attribute).eq(self._context_value)
                response = table.query(KeyConditionExpression=key_exp, **kwargs)

            for item in response['Items']:
                key = item[self._key_attribute]
                value = item[self._value_attribute]

                data[key] = value

            if 'LastEvaluatedKey' not in response:
                break

            last_evaluated_key = response['LastEvaluatedKey']

        return data
