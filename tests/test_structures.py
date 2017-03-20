from __future__ import absolute_import

from central.structures import IgnoreCaseDict
from unittest import TestCase


class TestIgnoreCaseDict(TestCase):
    def test_init_with_kwargs(self):
        d = IgnoreCaseDict(key='value')
        self.assertEqual('value', d['key'])

    def test_copy(self):
        d = IgnoreCaseDict(key='value')
        d2 = d.copy()

        self.assertEqual('value', d2['key'])
        self.assertIsInstance(d2, IgnoreCaseDict)
        self.assertNotEqual(id(d), id(2))

    def test_keys(self):
        d = IgnoreCaseDict()
        d['key1'] = 'value1'
        d['key2'] = 'value2'

        self.assertEqual({'key1', 'key2'}, set(d.keys()))

    def test_items(self):
        d = IgnoreCaseDict()
        d['key1'] = 'value1'
        d['key2'] = 'value2'

        self.assertEqual({'key1': 'value1', 'key2': 'value2'}, dict(d.items()))

    def test_values(self):
        d = IgnoreCaseDict()
        d['key1'] = 'value1'
        d['key2'] = 'value2'

        self.assertEqual({'value1', 'value2'}, set(d.values()))

    def test_preserved_original_keys(self):
        d = IgnoreCaseDict()
        d['Key'] = 'value'

        self.assertEqual({'Key'}, set(d.keys()))

    def test_contains_with_non_str_key(self):
        d = IgnoreCaseDict()

        with self.assertRaises(TypeError):
            1 in d

    def test_contains_with_case_insensitive_key(self):
        d = IgnoreCaseDict()
        d['Key'] = 'value'

        self.assertTrue('KEY' in d)

    def test_delete_with_existent_key(self):
        d = IgnoreCaseDict()
        d['key'] = 'value'
        del d['key']

        self.assertIsNone(d.get('key'))

    def test_delete_with_nonexistent_key(self):
        d = IgnoreCaseDict()

        with self.assertRaises(KeyError):
            del d['key']

    def test_delete_with_non_str_key(self):
        d = IgnoreCaseDict()

        with self.assertRaises(TypeError):
            del d[123]

    def test_get_with_case_insensitive_key(self):
        d = IgnoreCaseDict()
        d['Key'] = 'value'

        self.assertEqual('value', d.get('KEY'))

    def test_get_with_non_str_key(self):
        d = IgnoreCaseDict()
        with self.assertRaises(TypeError):
            d.get(1)

        with self.assertRaises(TypeError):
            d[1]

    def test_get_default_value(self):
        d = IgnoreCaseDict()
        self.assertEqual('value', d.get('key', default='value'))

    def test_set_with_non_str_key(self):
        d = IgnoreCaseDict()
        with self.assertRaises(TypeError):
            d[1] = 'value'

    def test_pop_with_nonexistent_key(self):
        d = IgnoreCaseDict()
        with self.assertRaises(KeyError):
            d.pop('not_found')

    def test_pop_with_non_str_key(self):
        d = IgnoreCaseDict()
        with self.assertRaises(TypeError):
            d.pop(1)

    def test_pop_with_default(self):
        d = IgnoreCaseDict()
        self.assertEqual('value', d.pop('not_found', default='value'))

    def test_popitem_with_keys(self):
        d = IgnoreCaseDict()
        d['Key'] = 'value'

        k, v = d.popitem()

        self.assertEqual('Key', k)
        self.assertEqual('value', v)

    def test_equal_with_dict(self):
        d = IgnoreCaseDict(key='value')
        self.assertEqual({'key': 'value'}, d)

    def test_equal_with_None(self):
        d = IgnoreCaseDict()
        self.assertEqual(False, d == None)

    def test_repr(self):
        d = IgnoreCaseDict(key='value')
        self.assertEqual("{'key': 'value'}", repr(d))
