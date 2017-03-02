"""
An ini reader.
"""

from configparser import ConfigParser
from .. import abc


__all__ = [
    'IniReader'
]


class IniReader(abc.Reader):
    """
    A reader for ini content.

    Example usage:

    .. code-block:: python

        from configd.readers import IniReader

        reader = IniReader()

        with open('config.ini') as f:
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

        parser = ConfigParser()
        parser.read_file(stream)

        data = {}

        for section in parser.sections():
            data_section = data[section] = {}

            for option in parser.options(section):
                data_section[option] = parser.get(section, option, raw=True)

        return data
