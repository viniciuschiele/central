"""
Data structure implementations.
"""

from collections import MutableMapping


class IgnoreCaseDict(MutableMapping):
    """
    A case insensitive dict that preserves the original keys.
    >>> d = IgnoreCaseDict()
    >>> d['Foo'] = 5
    >>> d['foo'] == d['FOO'] == d['Foo'] == 5
    True
    >>> set(d.keys())
    {'Foo'}
    """

    __marker = object()

    def __init__(self, seq=None, **kwargs):
        self._store = {}

        if seq:
            self.update(seq)

        if kwargs:
            self.update(kwargs)

    def clear(self):
        self._store.clear()

    def copy(self):
        return self.__class__(self)

    def get(self, key, default=__marker):
        try:
            pair = self._store.get(key.lower(), self.__marker)
        except AttributeError:
            raise TypeError('key must be a str')

        if pair is not self.__marker:
            return pair[1]

        if default is self.__marker:
            return None

        return default

    def pop(self, key, default=__marker):
        try:
            pair = self._store.pop(key.lower(), self.__marker)
        except AttributeError:
            raise TypeError('key must be a str')

        if pair is not self.__marker:
            return pair[1]

        if default is self.__marker:
            raise KeyError(key)

        return default

    def popitem(self):
        _, pair = self._store.popitem()
        return pair[0], pair[1]

    __copy__ = copy

    def __contains__(self, key):
        try:
            return key.lower() in self._store
        except AttributeError:
            raise TypeError('key must be a str')

    def __delitem__(self, key):
        try:
            del self._store[key.lower()]
        except AttributeError:
            raise TypeError('key must be a str')

    def __getitem__(self, key):
        try:
            return self._store[key.lower()][1]
        except AttributeError:
            raise TypeError('key must be a str')

    def __setitem__(self, key, value):
        try:
            self._store[key.lower()] = (key, value)
        except AttributeError:
            raise TypeError('key must be a str')

    def __iter__(self):
        for pair in self._store.values():
            yield pair[0]

    def __len__(self):
        return len(self._store)

    def __repr__(self):
        s = '{'

        for key, value in self.items():
            if not s.endswith('{'):
                s += ', '
            s += repr(key) + ': ' + repr(value)

        s += '}'

        return s
