import os


def get_file_ext(filename):
    """
    Get the extension from the given filename.
    :param str filename: The filename.
    :return str: The extension.
    """
    return os.path.splitext(filename)[1].strip('.')
