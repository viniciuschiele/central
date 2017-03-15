"""
Data structure implementations.
"""

from collections import Mapping, MutableMapping, KeysView, ItemsView, ValuesView
from .compat import string_types


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
        pair = super(IgnoreCaseDict, self).get(self._lower(key), self.__marker)

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
        pair = super(IgnoreCaseDict, self).pop(self._lower(key), self.__marker)

        if pair is not self.__marker:
            return pair[1]

        if default is self.__marker:
            raise KeyError(key)

        return default

    def popitem(self):
        _, pair = super(IgnoreCaseDict, self).popitem()
        return pair[0], pair[1]

    update = __update = MutableMapping.update

    def _lower(self, key):
        if isinstance(key, string_types):
            return key.lower()

        return key

    __copy__ = copy

    def __contains__(self, key):
        return super(IgnoreCaseDict, self).__contains__(self._lower(key))

    def __delitem__(self, key):
        super(IgnoreCaseDict, self).__delitem__(self._lower(key))

    def __getitem__(self, key):
        return super(IgnoreCaseDict, self).__getitem__(self._lower(key))[1]

    def __setitem__(self, key, value):
        super(IgnoreCaseDict, self).__setitem__(self._lower(key), (key, value))

    def __iter__(self):
        for pair in super(IgnoreCaseDict, self).values():
            yield pair[0]

    def __eq__(self, other):
        if not isinstance(other, Mapping):
            return NotImplemented
        return dict(self.items()) == dict(other.items())

    def __repr__(self):
        if not self:
            return '%s()' % (self.__class__.__name__,)
        return '%s(%r)' % (self.__class__.__name__, list(self.items()))
