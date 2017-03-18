"""
Scheduler implementations.
"""

import logging

from numbers import Number
from threading import Event, Thread
from . import abc
from .compat import text_type
from .exceptions import SchedulerError


__all__ = [
    'FixedIntervalScheduler',
]


logger = logging.getLogger(__name__)


class FixedIntervalScheduler(abc.Scheduler):
    """
    A scheduler implementation for scheduling execution
    at a fixed interval in seconds.

    Example usage:

    .. code-block:: python

        from central.schedulers import FixedIntervalScheduler

        scheduler = FixedIntervalScheduler(interval=2)

        scheduler.schedule(lambda: print('hit'))

    :param Number interval: The interval in seconds between executions.
    """

    def __init__(self, interval=10):
        if interval is None or not isinstance(interval, Number):
            raise TypeError('interval must be a number')

        if not (interval > 0):
            raise ValueError('interval must be greater than 0')

        self._interval = interval
        self._closed = Event()

    @property
    def interval(self):
        """
        Get the interval.
        :return int: The interval in seconds.
        """
        return self._interval

    def schedule(self, func):
        """
        Schedule a given func to be executed between the interval.
        :param func: The function to be executed.
        """
        if self._closed.is_set():
            raise SchedulerError('Scheduler is closed')

        if func is None or not callable(func):
            raise TypeError('func must be a callable object.')

        thread = Thread(target=self._process, args=(func,), name='FixedIntervalScheduler')
        thread.daemon = True
        thread.start()

    def _process(self, func):
        """
        Keep calling the given func while scheduler is not closed.
        :param func: The func to be called.
        """
        while not self._closed.is_set():
            if self._closed.wait(self._interval):
                break

            try:
                func()
            except:
                logger.warning('Scheduled action %s failed' % text_type(func), exc_info=True)

    def close(self):
        """
        Stop any scheduled execution.
        The scheduler cannot be used again.
        """
        self._closed.set()
