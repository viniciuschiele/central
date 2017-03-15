"""
Data structure implementations.
"""

from collections import Mapping, MutableMapping, KeysView, ItemsView, ValuesView


class IgnoreCaseDict(dict):
    """
    A case insensitive dict that preserves the original keys.
    >>> d = IgnoreCaseDict()
    >>> d['Foo'] = 5
    >>> d['foo'] == d['FOO'] == d['Foo'] == 5
    True
    >>> set(d.keys())
    {'Foo'}
    """
    __slots__ = ()

    __marker = object()

    def __init__(self, seq=None, **kwargs):
        super(IgnoreCaseDict, self).__init__()

        if seq:
            self.update(seq)

        if kwargs:
            self.update(kwargs)

    def copy(self):
        return self.__class__(self)

    def get(self, key, default=__marker):
        try:
            pair = super(IgnoreCaseDict, self).get(key.lower(), self.__marker)
        except AttributeError:
            raise TypeError('key must be a str')

        if pair is not self.__marker:
            return pair[1]

        if default is self.__marker:
            return None

        return default

    def keys(self):
        return KeysView(self)

    def values(self):
        return ValuesView(self)

    def items(self):
        return ItemsView(self)

    def pop(self, key, default=__marker):
        try:
            pair = super(IgnoreCaseDict, self).pop(key.lower(), self.__marker)
        except AttributeError:
            raise TypeError('key must be a str')

        if pair is not self.__marker:
            return pair[1]

        if default is self.__marker:
            raise KeyError(key)

        return default

    def popitem(self):
        _, pair = super(IgnoreCaseDict, self).popitem()
        return pair[0], pair[1]

    update = __update = MutableMapping.update

    __copy__ = copy

    def __contains__(self, key):
        try:
            return super(IgnoreCaseDict, self).__contains__(key.lower())
        except AttributeError:
            raise TypeError('key must be a str')

    def __delitem__(self, key):
        try:
            super(IgnoreCaseDict, self).__delitem__(key.lower())
        except AttributeError:
            raise TypeError('key must be a str')

    def __getitem__(self, key):
        try:
            return super(IgnoreCaseDict, self).__getitem__(key.lower())[1]
        except AttributeError:
            raise TypeError('key must be a str')

    def __setitem__(self, key, value):
        try:
            super(IgnoreCaseDict, self).__setitem__(key.lower(), (key, value))
        except AttributeError:
            raise TypeError('key must be a str')

    def __iter__(self):
        for pair in super(IgnoreCaseDict, self).values():
            yield pair[0]

    def __eq__(self, other):
        if not isinstance(other, Mapping):
            return NotImplemented
        return dict(self.items()) == dict(other.items())

    def __repr__(self):
        s = '{'

        for key, value in self.items():
            if not s.endswith('{'):
                s += ', '
            s += repr(key) + ': ' + repr(value)

        s += '}'

        return s
