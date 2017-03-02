"""
A json reader.
"""

import json

from .. import abc


__all__ = [
    'JsonReader'
]


class JsonReader(abc.Reader):
    """
    A reader for json content.

    Example usage:

    .. code-block:: python

        from configd.readers import JsonReader

        reader = JsonReader()

        with open('config.json') as f:
            data = reader.read(f)

    """

    def read(self, stream):
        """
        Read the given stream and returns it as a dict.
        :param stream: The stream to read the configuration from.
        :return dict: The configuration read from the stream.
        """
        if stream is None:
            raise ValueError('stream cannot be None')

        return json.load(stream)
