from __future__ import absolute_import

from configd.utils.event import EventHandler
from threading import Event
from unittest import TestCase


class TestEventHandler(TestCase):
    def test_init_after_add_func_with_func_value(self):
        def callback():
            pass
        EventHandler(after_add_func=callback)

    def test_init_after_add_func_with_str_value(self):
        with self.assertRaises(TypeError):
            EventHandler(after_add_func='non callable')

    def test_init_after_remove_func_with_func_value(self):
        def callback():
            pass
        EventHandler(after_add_func=callback)

    def test_init_after_remove_func_with_str_value(self):
        with self.assertRaises(TypeError):
            EventHandler(after_remove_func='non callable')

    def test_get(self):
        handler = EventHandler()

        def dummy():
            pass

        handler.add(dummy)
        self.assertEqual(dummy, handler[0])

    def test_len(self):
        handler = EventHandler()
        self.assertEqual(0, len(handler))

        def dummy():
            pass

        handler.add(dummy)
        self.assertEqual(1, len(handler))

    def test_add_with_callback_as_none(self):
        handler = EventHandler()

        with self.assertRaises(TypeError):
            handler.add(None)

    def test_add_with_callback_as_func(self):
        def dummy():
            pass

        handler = EventHandler()
        handler.add(dummy)

        self.assertEqual(1, len(handler))

    def test_remove_with_callback_as_none(self):
        handler = EventHandler()
        with self.assertRaises(TypeError):
            handler.remove(None)

    def test_remove_with_callback_as_func(self):
        def dummy():
            pass

        handler = EventHandler()
        handler.add(dummy)
        handler.remove(dummy)

        self.assertEqual(0, len(handler))

    def test_add_with_after_add_func(self):
        ev = Event()

        def callback():
            ev.set()

        handler = EventHandler(after_add_func=callback)
        handler.add(callback)

        self.assertTrue(ev.is_set())

    def test_add_with_after_remove_func(self):
        ev = Event()

        def callback():
            ev.set()

        handler = EventHandler(after_remove_func=callback)
        handler.add(callback)
        handler.remove(callback)

        self.assertTrue(ev.is_set())
