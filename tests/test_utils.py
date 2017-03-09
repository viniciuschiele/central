from __future__ import absolute_import

from configd.utils import EventHandler, Transformer, Version
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


class TestTransformer(TestCase):
    def test_transform_with_non_dict(self):
        transformer = Transformer()

        with self.assertRaises(TypeError):
            transformer.transform('non dict', {})

        with self.assertRaises(TypeError):
            transformer.transform({}, 'non dict')

    def test_transform_default(self):
        base = {
            'parent': {
                'child': {
                    'key': 'value'
                },
                'child2': {
                    'key': 'value 2'
                }
            }
        }

        data = {
            'parent':
                {
                    'child': {
                        'key': 'value 2',
                        'key2': 'value 3'
                    }
                }
        }

        expected = {
            'parent': {
                'child': {
                    'key': 'value 2',
                    'key2': 'value 3'
                },
                'child2': {
                    'key': 'value 2'
                }
            }
        }

        Transformer().transform(base, data)

        self.assertEqual(base, expected)

    def test_transform_merge(self):
        base = {
            'parent': {
                'child': {
                    'key': 'value'
                },
                'child2': {
                    'key': 'value 2'
                }
            }
        }

        data = {
            'parent':
                {
                    'child': {
                        '@transform': 'merge',
                        'key': 'value 2',
                        'key2': 'value 3'
                    }
                }
        }

        expected = {
            'parent': {
                'child': {
                    'key': 'value 2',
                    'key2': 'value 3'
                },
                'child2': {
                    'key': 'value 2'
                }
            }
        }

        Transformer().transform(base, data)

        self.assertEqual(base, expected)

    def test_transform_replace(self):
        base = {
            'parent': {
                'child': {
                    'key': 'value'
                },
                'child2': {
                    'key': 'value 2'
                }
            }
        }

        data = {
            'parent':
                {
                    'child': {
                        '@transform': 'replace',
                        'key2': 'value 2'
                    }
                }
        }

        expected = {
            'parent': {
                'child': {
                    'key2': 'value 2'
                },
                'child2': {
                    'key': 'value 2'
                }
            }
        }

        Transformer().transform(base, data)

        self.assertEqual(base, expected)

    def test_transform_remove(self):
        base = {
            'parent': {
                'child': {
                    'key': 'value'
                },
                'child2': {
                    'key': 'value 2'
                }
            }
        }

        data = {
            'parent':
                {
                    'child': {
                        '@transform': 'remove',
                    }
                }
        }

        expected = {
            'parent': {
                'child2': {
                    'key': 'value 2'
                }
            }
        }

        Transformer().transform(base, data)

        self.assertEqual(base, expected)

    def test_transform_invalid(self):
        base = {
            'parent': {
                'child': {
                    'key': 'value'
                },
                'child2': {
                    'key': 'value 2'
                }
            }
        }

        data = {
            'parent':
                {
                    'child': {
                        '@transform': 'unknown',
                    }
                }
        }

        with self.assertRaises(ValueError):
            Transformer().transform(base, data)

    def test_transform_missing_keys(self):
        base = {
            'key': 'value'
        }

        data = {
            'key2': 'value 2'
        }

        expected = {
            'key': 'value',
            'key2': 'value 2'
        }

        Transformer().transform(base, data)

        self.assertEqual(base, expected)


class TestVersion(TestCase):
    def test_get_changed_with_default_value(self):
        version = Version()
        self.assertEqual(EventHandler, type(version.changed))

    def test_get_number_with_default_value(self):
        version = Version()
        self.assertEqual(0, version.number)

    def test_set_number_with_int_value(self):
        version = Version()
        version.number = 2
        self.assertEqual(2, version.number)

    def test_str(self):
        version = Version()
        self.assertEqual('0', str(version))

    def test_repr(self):
        version = Version()
        self.assertEqual('Version(0)', repr(version))
