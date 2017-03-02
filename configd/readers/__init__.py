from . import ini, json, yaml


__readers = {
    'ini': ini.IniReader,
    'json': json.JsonReader,
    'yaml': yaml.YamlReader,
}


def add_reader(name, reader_cls):
    """
    Add a reader class.
    :param str name: The name of the reader.
    :param reader_cls: The reader class.
    """
    __readers[name] = reader_cls


def get_reader(name):
    """
    Get a reader by name.
    :param str name: The name of the reader.
    :return: The reader class found, otherwise None.
    """
    return __readers.get(name)


def remove_reader(name):
    """
    Remove a reader by name.
    :param str name: The name of the reader.
    :return: The reader class removed, None if not found.
    """
    return __readers.pop(name, None)
