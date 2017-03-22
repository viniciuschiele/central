"""
Utility module
"""

import os

from collections import Mapping, MutableMapping
from .structures import IgnoreCaseDict


def get_file_ext(filename):
    """
    Get the extension from the given filename.
    :param str filename: The filename.
    :return str: The extension.
    """
    return os.path.splitext(filename)[1].strip('.')


def make_ignore_case(data):
    """
    Convert the given `Mapping` into an `IgnoreCaseDict`.
    :param Mapping data: The object to be converted.
    :return IgnoreCaseDict: The object converted to IgnoreCaseDict.
    """
    if isinstance(data, IgnoreCaseDict):
        return data

    d = IgnoreCaseDict()

    for key in data:
        value = data.get(key)

        if isinstance(value, Mapping):
            value = make_ignore_case(value)

        d[key] = value

    return d


def merge_dict(target, *sources):
    """
    Merge the given list of `Mapping` objects into `target` object.
    :param MutableMapping target: The mapping to receive the merge.
    :param tuple sources: The list of `mapping` objects to be merged.
    """
    for source in sources:
        if not isinstance(target, MutableMapping):
            raise TypeError('target must be a dict')

        if not isinstance(source, Mapping):
            raise TypeError('data must be a dict')

        for key in source:
            target_value = target.get(key)
            source_value = source[key]

            if target_value is None or source_value is None:
                target[key] = source_value

            elif isinstance(target_value, Mapping) and isinstance(source_value, Mapping):
                merge_dict(target_value, source_value)

            else:
                target[key] = source_value


class EventHandler(object):
    """
    A simple event handling class, which manages callbacks to be executed.

    :param after_add_func: The func called after adding a new callback.
    :param after_remove_func: The func called after removing a callback.
    """
    def __init__(self, after_add_func=None, after_remove_func=None):
        if after_add_func and not callable(after_add_func):
            raise TypeError('after_add_func must be callable object')

        if after_remove_func and not callable(after_remove_func):
            raise TypeError('after_remove_func must be callable object')

        self._after_add_func = after_add_func
        self._after_remove_func = after_remove_func
        self._callbacks = []

    def __call__(self, *args):
        """
        Execute all callbacks.

        Execute all connected callbacks in the order of addition,
        passing the sender of the EventHandler as first argument and the
        optional args as second, third, ... argument to them.
        """
        return [callback(*args) for callback in self._callbacks]

    def __len__(self):
        """
        Get the amount of callbacks connected to the EventHandler.
        """
        return len(self._callbacks)

    def __getitem__(self, index):
        """
        Get a callback by index.
        :param int index: The index of the callback.
        :return: The callback found.
        """
        return self._callbacks[index]

    def add(self, callback):
        """
        Add a callback to the EventHandler.
        :param callback: The callback to be added.
        """
        if not callable(callback):
            raise TypeError("callback must be callable")

        self._callbacks.append(callback)

        if self._after_add_func:
            self._after_add_func()

    def remove(self, callback):
        """
        Remove a callback from the EventHandler.
        :param callback: The callback to be added.
        """
        if not callable(callback):
            raise TypeError("callback must be callable")

        self._callbacks.remove(callback)

        if self._after_remove_func:
            self._after_remove_func()


class Version(object):
    """
    A simple class to manage incremental version of data.

    :param int number: The initial version number.
    """
    def __init__(self, number=0):
        self._number = number
        self._changed = EventHandler()

    @property
    def changed(self):
        """
        Get the changed event handler.
        :return EventHandler: The changed event handler.
        """
        return self._changed

    @property
    def number(self):
        """
        Get the version number.
        :return int: The version number.
        """
        return self._number

    @number.setter
    def number(self, value):
        """
        Set the version number.
        :param int value: The version number.
        """
        self._number = value
        self._changed()

    def __str__(self):
        """
        Get the version number as string.
        :return str: The version number as string.
        """
        return str(self._number)

    def __repr__(self):
        """
        Get a friendly version number.
        :return str: The friendly string number.
        """
        return 'Version(%s)' % str(self._number)
