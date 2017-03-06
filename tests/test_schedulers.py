from __future__ import absolute_import

from configd.exceptions import SchedulerError
from configd.schedulers import FixedIntervalScheduler
from unittest import TestCase


class TestFixedIntervalScheduler(TestCase):
    def test_default_interval(self):
        scheduler = FixedIntervalScheduler()
        self.assertEqual(60000, scheduler.interval)

    def test_interval_as_float(self):
        self.assertRaises(TypeError, FixedIntervalScheduler, interval=1.1)

    def test_interval_less_than_1(self):
        self.assertRaises(ValueError, FixedIntervalScheduler, interval=0)

    def test_schedule_with_none_as_func(self):
        scheduler = FixedIntervalScheduler()
        self.assertRaises(TypeError, scheduler.schedule, func=None)

    def test_schedule_with_non_callable_as_func(self):
        scheduler = FixedIntervalScheduler()
        self.assertRaises(TypeError, scheduler.schedule, func='non callable')

    def test_schedule_with_closed_scheduler(self):
        def dummy():
            pass

        scheduler = FixedIntervalScheduler()
        scheduler.close()

        with self.assertRaises(SchedulerError):
            scheduler.schedule(dummy)

    def test_schedule_with_valid_func(self):
        from threading import Event
        ev = Event()

        scheduler = FixedIntervalScheduler(interval=1)
        scheduler.schedule(lambda: ev.set())

        self.assertTrue(ev.wait(0.5))  # wait half second

    def test_schedule_with_func_raising_error(self):
        import time

        counter = []

        def func():
            counter.append(1)
            raise Exception(str(len(counter)))

        scheduler = FixedIntervalScheduler(interval=10)
        scheduler.schedule(func)

        time.sleep(0.1)

        self.assertGreater(len(counter), 1)

    def test_schedule_with_close_afterwards(self):
        import time

        counter = []

        def func():
            counter.append(1)

        scheduler = FixedIntervalScheduler(interval=10)
        scheduler.schedule(func)

        time.sleep(0.01)

        scheduler.close()

        time.sleep(0.01)

        previous = len(counter)

        time.sleep(0.01)

        self.assertEqual(previous, len(counter))

    def test_close_multiple_times(self):
        scheduler = FixedIntervalScheduler()
        scheduler.close()
        scheduler.close()
