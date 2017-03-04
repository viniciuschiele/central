from configd.exceptions import LibraryRequiredError
from configd.readers.ini import IniReader
from configd.readers.json import JsonReader
from configd.readers.yaml import YamlReader
from io import StringIO
from unittest import TestCase


class ReaderMixin(object):
    def test_read_with_none_as_stream(self):
        with self.assertRaises(ValueError):
            self.reader.read(None)

    def test_read_valid_stream(self):
        stream = StringIO()
        stream.write(self.data)
        stream.seek(0, 0)

        data = self.reader.read(stream)
        self.assertEqual(data, {'database': {'host': 'localhost', 'port': '1234'}})


class TestIniReader(TestCase, ReaderMixin):
    def setUp(self):
        self.reader = IniReader()
        self.data = '[database]\nhost=localhost\nport=1234\n'


class TestJsonReader(TestCase, ReaderMixin):
    def setUp(self):
        self.reader = JsonReader()
        self.data = '{"database": {"host": "localhost", "port": "1234"}}'


class TestYamlReader(TestCase, ReaderMixin):
    def setUp(self):
        self.reader = YamlReader()
        self.data = 'database:\n  host: localhost\n  port: "1234"\n'

    def test_pyyaml_not_installed(self):
        from configd.readers import yaml
        yaml_tmp = yaml.yaml
        yaml.yaml = None

        with self.assertRaises(LibraryRequiredError):
            YamlReader()

        yaml.yaml = yaml_tmp