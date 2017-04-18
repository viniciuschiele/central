import codecs
import os

from .. import abc
from ..compat import string_types, FileNotFoundError
from ..exceptions import ConfigError
from ..interpolation import ChainLookup, EnvironmentLookup
from ..readers import get_reader
from ..structures import IgnoreCaseDict
from ..utils import get_file_ext, merge_dict
from .core import BaseDataConfig


class FileConfig(BaseDataConfig):
    """
    A config implementation that loads the configuration
    from a file.

    Example usage:

    .. code-block:: python

        from central.config import FileConfig

        config = FileConfig('config.json')
        config.load()

        value = config.get('key')

    :param str filename: The filename to be read.
    :param abc.Reader reader: The reader used to read the file content as a dict,
        if None a reader based on the filename is going to be used.
    """

    def __init__(self, filename, reader=None):
        super(FileConfig, self).__init__()
        if not isinstance(filename, string_types):
            raise TypeError('filename must be a str')

        if reader is not None and not isinstance(reader, abc.Reader):
            raise TypeError('reader must be an abc.Reader')

        self._filename = filename
        self._reader = reader

    @property
    def filename(self):
        """
        Get the filename.
        :return str: The filename.
        """
        return self._filename

    @property
    def reader(self):
        """
        Get the reader.
        :return abc.Reader: The reader.
        """
        return self._reader

    def load(self):
        """
        Load the configuration from a file.
        Recursively load any filename referenced by an @next property in the configuration.

        This method does not trigger the updated event.
        """
        to_merge = []
        filename = self.filename

        while filename:
            file = self._find_file(filename)

            if file is None:
                raise FileNotFoundError('File %s not found' % filename)

            data = self._read_file(file)

            if not isinstance(data, IgnoreCaseDict):
                raise ConfigError('reader must return an IgnoreCaseDict object')

            filename = data.pop('@next', None)

            if filename is not None and not isinstance(filename, string_types):
                raise ConfigError('@next must be a str')

            to_merge.append(data)

        data = to_merge[0]

        if len(to_merge) > 1:
            merge_dict(data, *to_merge[1:])

        self._data = data

    def _get_reader(self, filename):
        """
        Get an appropriated reader based on the filename,
        if not found an `ConfigError` is raised.
        :param str filename: The filename used to guess the appropriated reader.
        :return abc.Reader: A reader.
        """
        extension = get_file_ext(filename)

        if not extension:
            raise ConfigError('File %s is not supported' % filename)

        reader_cls = get_reader(extension)

        if reader_cls is None:
            raise ConfigError('File %s is not supported' % filename)

        return reader_cls()

    def _find_file(self, filename):
        """
        Find the given file in the file system.
        :param str filename: The filename to be found.
        :return: The filename if found, otherwise None.
        """
        # create a chain lookup to resolve any variable left
        # using environment variable.
        lookup = ChainLookup(EnvironmentLookup(), self._lookup)

        # resolve variables.
        filename = self._interpolator.resolve(filename, lookup)

        if os.path.exists(filename):
            return filename

        return None

    def _read_file(self, filename):
        """
        Read the content of the file.
        :param str filename: The filename to be read.
        :return IgnoreCaseDict: The data read from the file.
        """
        reader = self._reader or self._get_reader(filename)

        with self._open_file(filename) as stream:
            text_reader_cls = codecs.getreader('utf-8')

            with text_reader_cls(stream) as text_reader:
                return reader.read(text_reader)

    def _open_file(self, filename):
        """
        Open a stream for the given filename.
        :param str filename: The filename to be read.
        :return: The stream to read the file content.
        """
        return open(filename, mode='rb')
