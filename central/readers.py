"""
Reader implementations.
"""

import json

from . import abc
from .compat import ConfigParser, PY2, string_types
from .exceptions import LibraryRequiredError
from .structures import IgnoreCaseDict

try:
    import yaml
    import yaml.constructor
except:
    yaml = None

try:
    import toml
except:
    toml = None


__all__ = [
    'add_reader',
    'get_reader',
    'remove_reader',
    'IniReader',
    'JsonReader',
    'YamlReader',
]


__readers = {}


def add_reader(name, reader_cls):
    """
    Add a reader class.
    :param str name: The name of the reader.
    :param reader_cls: The reader class.
    """
    if name is None or not isinstance(name, string_types):
        raise TypeError('name must be a str')

    if reader_cls is None:
        raise ValueError('render_cls cannot be None')

    __readers[name] = reader_cls


def get_reader(name):
    """
    Get a reader by name.
    :param str name: The name of the reader.
    :return: The reader class found, otherwise None.
    """
    if name is None or not isinstance(name, string_types):
        raise TypeError('name must be a str')

    return __readers.get(name)


def remove_reader(name):
    """
    Remove a reader by name.
    :param str name: The name of the reader.
    :return: The reader class removed, None if not found.
    """
    if name is None or not isinstance(name, string_types):
        raise TypeError('name must be a str')

    return __readers.pop(name, None)


class IniReader(abc.Reader):
    """
    A reader for ini content.

    Example usage:

    .. code-block:: python

        from central.readers import IniReader

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

        if PY2:
            parser.readfp(stream)
        else:
            parser.read_file(stream)

        data = IgnoreCaseDict()

        for section in parser.sections():
            data_section = data[section] = IgnoreCaseDict()

            for option in parser.options(section):
                data_section[option] = parser.get(section, option, raw=True)

        return data


class JsonReader(abc.Reader):
    """
    A reader for json content.

    Example usage:

    .. code-block:: python

        from central.readers import JsonReader

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

        return json.load(stream, object_pairs_hook=IgnoreCaseDict)


class TomlReader(abc.Reader):
    """
    A reader for toml content.

    The library toml must be installed.

    Example usage:

    .. code-block:: python

        from central.readers import TomlReader

        reader = TomlReader()

        with open('config.toml') as f:
            data = reader.read(f)

    """

    def __init__(self):
        if not toml:
            raise LibraryRequiredError('toml', 'https://pypi.python.org/pypi/toml')

    def read(self, stream):
        """
        Read the given stream and returns it as a dict.
        :param stream: The stream to read the configuration from.
        :return dict: The configuration read from the stream.
        """
        if stream is None:
            raise ValueError('stream cannot be None')

        return toml.load(stream, _dict=IgnoreCaseDict)


class YamlReader(abc.Reader):
    """
    A reader for yaml content.

    The library PyYAML must be installed.

    Example usage:

    .. code-block:: python

        from central.readers import YamlReader

        reader = YamlReader()

        with open('config.yaml') as f:
            data = reader.read(f)

    """

    def __init__(self):
        if not yaml:
            raise LibraryRequiredError('PyYAML', 'https://pypi.python.org/pypi/PyYAML')

    def read(self, stream):
        """
        Read the given stream and returns it as a dict.
        :param stream: The stream to read the configuration from.
        :return dict: The configuration read from the stream.
        """
        if stream is None:
            raise ValueError('stream cannot be None')

        return yaml.load(stream, Loader=self._get_loader())

    def _get_loader(self):
        """
        Get a loader that uses an IgnoreCaseDict for
        complex objects.
        :return yaml.Loader: The loader object.
        """
        # this class was copied from
        # https://github.com/fmenabe/python-yamlordereddictloader/blob/master/yamlordereddictloader.py
        # and adapted to use IgnoreCaseDict

        class Loader(yaml.Loader):
            def __init__(self, *args, **kwargs):
                yaml.Loader.__init__(self, *args, **kwargs)
                self.add_constructor(
                    'tag:yaml.org,2002:map', type(self).construct_yaml_map)
                self.add_constructor(
                    'tag:yaml.org,2002:omap', type(self).construct_yaml_map)

            def construct_yaml_map(self, node):
                data = IgnoreCaseDict()
                yield data
                value = self.construct_mapping(node)
                data.update(value)

            def construct_mapping(self, node, deep=False):
                if isinstance(node, yaml.MappingNode):
                    self.flatten_mapping(node)
                else:
                    raise yaml.constructor.ConstructorError(
                        None, None, 'expected a mapping node, but found %s' % node.id, node.start_mark)

                mapping = IgnoreCaseDict()
                for key_node, value_node in node.value:
                    key = self.construct_object(key_node, deep=deep)
                    try:
                        hash(key)
                    except TypeError as err:
                        raise yaml.constructor.ConstructorError(
                            'while constructing a mapping', node.start_mark,
                            'found unacceptable key (%s)' % err, key_node.start_mark)
                    value = self.construct_object(value_node, deep=deep)
                    mapping[key] = value

                return mapping

        return Loader


add_reader('ini', IniReader)
add_reader('json', JsonReader)
add_reader('toml', TomlReader)
add_reader('yaml', YamlReader)
