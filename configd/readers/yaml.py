"""
An yaml reader.
"""

from .. import abc
from ..exceptions import LibraryRequiredError


try:
    import yaml
except:
    yaml = None


__all__ = [
    'YamlReader'
]


MSG_NO_YAML = """
You need to install the library PyYAML to use the YamlReader. See https://pypi.python.org/pypi/PyYAML
"""


class YamlReader(abc.Reader):
    """
    A reader for yaml content.

    The library PyYAML must be installed.

    Example usage:

    .. code-block:: python

        from configd.readers import YamlReader

        reader = YamlReader()

        with open('config.yaml') as f:
            data = reader.read(f)

    """

    def __init__(self):
        if not yaml:
            raise LibraryRequiredError(MSG_NO_YAML)

    def read(self, stream):
        """
        Read the given stream and returns it as a dict.
        :param stream: The stream to read the configuration from.
        :return dict: The configuration read from the stream.
        """
        if stream is None:
            raise ValueError('stream cannot be None')

        return yaml.load(stream)
