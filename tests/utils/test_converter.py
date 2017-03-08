from __future__ import absolute_import

from configd.utils import converter
from datetime import date, datetime, time
from unittest import TestCase


class TestConverter(TestCase):
    def test_to_bool_with_true_values(self):
        for value in converter.TRUE_VALUES:
            self.assertEqual(True, converter.to_bool(value))

    def test_to_bool_with_false_values(self):
        for value in converter.FALSE_VALUES:
            self.assertEqual(False, converter.to_bool(value))

    def test_to_bool_with_dict(self):
        with self.assertRaises(ValueError):
            converter.to_bool({})

    def test_to_float_with_str_value(self):
        self.assertEqual(1.0, converter.to_float('1'))

    def test_to_float_with_int_value(self):
        self.assertEqual(1.0, converter.to_float(1))

    def test_to_float_with_dict_value(self):
        with self.assertRaises(TypeError):
            converter.to_float({})

    def test_to_int_with_str_value(self):
        self.assertEqual(1, converter.to_int('1'))

    def test_to_int_with_float_value(self):
        self.assertEqual(1, converter.to_int(1.0))

    def test_to_int_with_dict_value(self):
        with self.assertRaises(TypeError):
            converter.to_int({})

    def test_to_str_with_int_value(self):
        self.assertEqual('1', converter.to_str(1))

    def test_to_str_with_float_value(self):
        self.assertEqual('1.0', converter.to_str(1.0))

    def test_to_str_with_dict_value(self):
        self.assertEqual('{}', converter.to_str({}))

    def test_to_list_with_list_value(self):
        self.assertEqual([1], converter.to_list([1]))

    def test_to_list_with_str_value(self):
        self.assertEqual(['1', '2', '3'], converter.to_list('1,2,3'))

    def test_to_list_with_int_value(self):
        with self.assertRaises(TypeError):
            converter.to_list(1)

    def test_to_dict_with_dict_value(self):
        self.assertEqual({'key': 1}, converter.to_dict({'key': 1}))

    def test_to_dict_with_str_value(self):
        self.assertEqual({'key1': '1', 'key2': '2'}, converter.to_dict('key1=1;key2=2'))

    def test_to_dict_with_int_value(self):
        with self.assertRaises(TypeError):
            converter.to_dict(1)

    def test_to_date_with_date_value(self):
        d = date(2017, 3, 8)
        self.assertEqual(d, converter.to_date(d))

    def test_to_date_with_datetime_value(self):
        d = datetime(2017, 3, 8, 14, 42, 30)
        self.assertEqual(d.date(), converter.to_date(d))

    def test_to_date_with_int_value(self):
        with self.assertRaises(TypeError):
            converter.to_date(1)

    def test_to_date_with_str_value(self):
        with self.assertRaises(ValueError):
            converter.to_date('some value')

    def test_to_date_with_iso_str_value(self):
        expected = date(2017, 3, 8)
        s = expected.isoformat()
        self.assertEqual(expected, converter.to_date(s))

    def test_to_datetime_with_date_value(self):
        d = datetime.now().date()
        expected = datetime(d.year, d.month, d.day)
        self.assertEqual(expected, converter.to_datetime(d))

    def test_to_datetime_with_datetime_value(self):
        d = datetime.now()
        self.assertEqual(d, converter.to_datetime(d))

    def test_to_datetime_with_int_value(self):
        with self.assertRaises(TypeError):
            converter.to_datetime(1)

    def test_to_datetime_with_str_value(self):
        with self.assertRaises(ValueError):
            converter.to_datetime('some value')

    def test_to_datetime_with_iso_str_value(self):
        expected = datetime(2017, 3, 8, 12, 40, 30)
        s = expected.isoformat()
        self.assertEqual(expected, converter.to_datetime(s))

    def test_to_time_with_time_value(self):
        expected = time(12, 40, 30)
        self.assertEqual(expected, converter.to_time(expected))

    def test_to_time_with_datetime_value(self):
        d = datetime(2017, 3, 8, 12, 40, 30)
        expected = time(12, 40, 30)
        self.assertEqual(expected, converter.to_time(d))

    def test_to_time_with_int_value(self):
        with self.assertRaises(TypeError):
            converter.to_time(1)

    def test_to_time_with_str_value(self):
        with self.assertRaises(ValueError):
            converter.to_time('some value')

    def test_to_time_with_iso_str_value(self):
        expected = time(12, 40, 30)
        s = expected.isoformat()
        self.assertEqual(expected, converter.to_time(s))

        expected = time(12, 40, 30, 800)
        s = expected.isoformat()
        self.assertEqual(expected, converter.to_time(s))
