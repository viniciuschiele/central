"""
Backward compatibility module.
"""

import sys

PY2 = int(sys.version_info[0]) == 2


if PY2:
    import urllib2
    urlopen = urllib2.urlopen

    from ConfigParser import ConfigParser
    ConfigParser = ConfigParser

    binary_type = str
    string_types = (str, unicode)
    text_type = unicode

    FileNotFoundError = OSError
else:
    import urllib.request
    urlopen = urllib.request.urlopen

    from configparser import ConfigParser
    ConfigParser = ConfigParser

    binary_type = bytes
    string_types = (str,)
    text_type = str

    FileNotFoundError = FileNotFoundError
