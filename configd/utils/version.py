from .event import EventHandler


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
        return 'Version(%s)' % self._number
