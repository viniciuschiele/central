class EventHandler(object):
    """
    A simple event handling class, which manages callbacks to be executed.

    :param before_add_func: The func called before adding a new callback.
    :param after_remove_func: The func called after removing a callback.
    """
    def __init__(self, before_add_func=None, after_remove_func=None):
        self._callbacks = []
        self._before_add_func = before_add_func
        self._after_remove_func = after_remove_func

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

    def __setitem__(self, index, value):
        """
        Set a callback by index.
        :param int index: The index of the callback
        :param value: The callback.
        """
        if not callable(value):
            raise TypeError("callback must be callable")
        self._callbacks[index] = value

    def __delitem__(self, index):
        """
        Delete a callback by index.
        :param index: The index of the callback.
        """
        del self._callbacks[index]

    def add(self, callback):
        """
        Add a callback to the EventHandler.
        :param callback: The callback to be added.
        """
        if not callable(callback):
            raise TypeError("callback must be callable")

        if self._before_add_func:
            self._before_add_func()

        self._callbacks.append(callback)

    def remove(self, callback):
        """
        Remove a callback from the EventHandler.
        :param callback: The callback to be added.
        """
        self._callbacks.remove(callback)

        if self._after_remove_func:
            self._after_remove_func()
