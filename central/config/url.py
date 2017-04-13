import codecs

from .. import abc
from ..compat import string_types, urlopen
from ..exceptions import ConfigError
from ..interpolation import ChainLookup, EnvironmentLookup
from ..readers import get_reader
from ..structures import IgnoreCaseDict
from ..utils import merge_dict
from .core import BaseDataConfig


class UrlConfig(BaseDataConfig):
    """
    A config implementation that loads the configuration
    from an url.
    
    Example usage:

    .. code-block:: python

        from central.config import UrlConfig

        config = UrlConfig('http://date.jsontest.com/')
        config.load()

        value = config.get('time')

    :param str url: The url to be read.
    :param abc.Reader reader: The reader used to read the response from url as a dict,
        if None a reader based on the content type of the response is going to be used.
    """
    def __init__(self, url, reader=None):
        super(UrlConfig, self).__init__()

        if not isinstance(url, string_types):
            raise TypeError('url must be a str')

        if reader is not None and not isinstance(reader, abc.Reader):
            raise TypeError('reader must be an abc.Reader')

        self._url = url
        self._reader = reader

    @property
    def url(self):
        """
        Get the url.
        :return str: The url.
        """
        return self._url

    @property
    def reader(self):
        """
        Get the reader.
        :return abc.Reader: The reader.
        """
        return self._reader

    def load(self):
        """
        Load the configuration from a url.
        Recursively load any url referenced by an @next property in the response.

        This method does not trigger the updated event.
        """
        to_merge = []
        url = self.url

        # create a chain lookup to resolve any variable left
        # using environment variable.
        lookup = ChainLookup(EnvironmentLookup(), self._lookup)

        while url:
            # resolve variables.
            url = self._interpolator.resolve(url, lookup)

            content_type, stream = self._open_url(url)

            try:
                reader = self._reader or self._get_reader(url, content_type)

                encoding = self._get_encoding(content_type)

                text_reader_cls = codecs.getreader(encoding)

                with text_reader_cls(stream) as text_reader:
                    data = reader.read(text_reader)
            finally:
                stream.close()

            if not isinstance(data, IgnoreCaseDict):
                raise ConfigError('reader must return an IgnoreCaseDict object')

            url = data.pop('@next', None)

            to_merge.append(data)

            if url and not isinstance(url, string_types):
                raise ConfigError('@next must be a str')

        data = to_merge[0]

        if len(to_merge) > 1:
            merge_dict(data, *to_merge[1:])

        self._data = data

    def _get_reader(self, url, content_type):
        """
        Get an appropriated reader based on the url and the content type,
        if not found an `ConfigError` is raised.
        :param str url: The url used to guess the appropriated reader.
        :param str content_type: The content type used to guess the appropriated reader.
        :return abc.Reader: A reader.
        """
        names = []

        if content_type:
            # it handles those formats for content type.
            # text/vnd.yaml
            # text/yaml
            # text/x-yaml

            if ';' in content_type:
                content_type = content_type.split(';')[0]

            if '.' in content_type:
                names.append(content_type.split('.')[-1])
            elif '-' in content_type:
                names.append(content_type.split('-')[-1])
            elif '/' in content_type:
                names.append(content_type.split('/')[-1])

        # it handles a url with file extension.
        # http://example.com/config.json
        path = url.strip().rstrip('/')

        i = path.rfind('/')

        if i > 10:  # > http:// https://
            path = path[i:]

            if '.' in path:
                names.append(path.split('.')[-1])

        for name in names:
            reader_cls = get_reader(name)
            if reader_cls:
                return reader_cls()

        raise ConfigError('Response from %s provided content type %s which is not supported' % (url, content_type))

    def _get_encoding(self, content_type, default='utf-8'):
        """
        Get the encoding from the given content type.
        :param str content_type: The content type from the response.
        :param str default: The default content type.
        :return str: The encoding.
        """
        if not content_type:
            return default

        # e.g: application/json;charset=iso-8859-x

        pairs = content_type.split(';')

        # skip the mime type
        for pair in pairs[1:]:
            kv = pair.split('=')
            if len(kv) != 2:
                continue

            key = kv[0].strip()
            value = kv[1].strip()

            if key == 'charset' and value:
                return value

        return default

    def _open_url(self, url):
        """
        Open the given url and returns its content type and the stream to read it.
        :param url: The url to be opened.
        :return tuple: The content type and the stream to read from.
        """
        response = urlopen(url)
        content_type = response.headers.get('content-type')
        return content_type, response
