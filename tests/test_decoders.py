from __future__ import absolute_import

from central.decoders import Decoder
from central.exceptions import DecoderError
from datetime import date, datetime, time
from unittest import TestCase


class TestDecoder(TestCase):
    def test_get_instance(self):
        self.assertEqual(Decoder, type(Decoder.instance()))
        self.assertEqual(Decoder.instance(), Decoder.instance())

    def test_get_converters(self):
        self.assertEqual(dict, type(Decoder().converters))

    def test_decode_with_none_as_value(self):
        decoder = Decoder()
        self.assertRaises(ValueError, decoder.decode, None, str)
        self.assertRaises(ValueError, decoder.decode, 'aa', None)

    def test_decode_with_invalid_cast(self):
        decoder = Decoder()
        self.assertRaises(DecoderError, decoder.decode, 'aa', 'invalid_cast')

    def test_decode_with_non_possible_cast(self):
        decoder = Decoder()
        with self.assertRaises(DecoderError):
            decoder.decode('aa', int)

    def test_decode_bool_with_bool_value(self):
        self.assertEqual(True, Decoder().decode(True, bool))

    def test_decode_bool_with_true_values(self):
        for value in Decoder.true_values:
            self.assertEqual(True, Decoder().decode(value, bool))

    def test_decode_bool_with_false_values(self):
        for value in Decoder.false_values:
            self.assertEqual(False, Decoder().decode(value, bool))

    def test_decode_bool_with_dict_value(self):
        with self.assertRaises(DecoderError):
            Decoder().decode({}, bool)

    def test_decode_float_with_str_value(self):
        self.assertEqual(1.0, Decoder().decode('1', float))

    def test_decode_float_with_int_value(self):
        self.assertEqual(1.0, Decoder().decode(1, float))

    def test_decode_float_with_dict_value(self):
        with self.assertRaises(DecoderError):
            Decoder().decode({}, float)

    def test_decode_int_with_str_value(self):
        self.assertEqual(1, Decoder().decode('1', int))

    def test_decode_int_with_float_value(self):
        self.assertEqual(1, Decoder().decode(1.0, float))

    def test_decode_int_with_dict_value(self):
        with self.assertRaises(DecoderError):
            Decoder().decode({}, int)

    def test_decode_str_with_int_value(self):
        self.assertEqual('1', Decoder().decode(1, str))

    def test_decode_str_with_float_value(self):
        self.assertEqual('1.0', Decoder().decode(1.0, str))

    def test_decode_str_with_dict_value(self):
        self.assertEqual('{}', Decoder().decode({}, str))

    def test_decode_list_with_list_value(self):
        self.assertEqual([1], Decoder().decode([1], list))

    def test_decode_list_with_tuple_value(self):
        self.assertEqual([1], Decoder().decode((1,), list))

    def test_decode_list_with_str_value(self):
        self.assertEqual(['1', '2', '3'], Decoder().decode('1,2,3', list))

    def test_decode_list_with_int_value(self):
        with self.assertRaises(DecoderError):
            Decoder().decode(1, list)

    def test_decode_dict_with_dict_value(self):
        self.assertEqual({'key': 1}, Decoder().decode({'key': 1}, dict))

    def test_decode_dict_with_str_value(self):
        self.assertEqual({'key1': '1', 'key2': '2'}, Decoder().decode('key1=1;key2=2', dict))

    def test_decode_dict_with_int_value(self):
        with self.assertRaises(DecoderError):
            Decoder().decode(1, dict)

    def test_decode_date_with_date_value(self):
        d = date(2017, 3, 8)
        self.assertEqual(d, Decoder().decode(d, date))

    def test_decode_date_with_datetime_value(self):
        d = datetime(2017, 3, 8, 14, 42, 30)
        self.assertEqual(d.date(), Decoder().decode(d, date))

    def test_decode_date_with_int_value(self):
        with self.assertRaises(DecoderError):
            Decoder().decode(1, date)

    def test_decode_date_with_str_value(self):
        with self.assertRaises(DecoderError):
            Decoder().decode('some value', date)

    def test_decode_date_with_iso_str_value(self):
        expected = date(2017, 3, 8)
        s = expected.isoformat()
        self.assertEqual(expected, Decoder().decode(s, date))

    def test_decode_datetime_with_date_value(self):
        d = datetime.now().date()
        expected = datetime(d.year, d.month, d.day)
        self.assertEqual(expected, Decoder().decode(d, datetime))

    def test_decode_datetime_with_datetime_value(self):
        d = datetime.now()
        self.assertEqual(d, Decoder().decode(d, datetime))

    def test_decode_datetime_with_int_value(self):
        with self.assertRaises(DecoderError):
            Decoder().decode(1, datetime)

    def test_decode_datetime_with_str_value(self):
        with self.assertRaises(DecoderError):
            Decoder().decode('some value', datetime)

    def test_decode_datetime_with_iso_str_value(self):
        expected = datetime(2017, 3, 8, 12, 40, 30)
        s = expected.isoformat()
        self.assertEqual(expected, Decoder().decode(s, datetime))

    def test_decode_time_with_time_value(self):
        expected = time(12, 40, 30)
        self.assertEqual(expected, Decoder().decode(expected, time))

    def test_decode_time_with_datetime_value(self):
        d = datetime(2017, 3, 8, 12, 40, 30)
        expected = time(12, 40, 30)
        self.assertEqual(expected, Decoder().decode(d, time))

    def test_decode_time_with_int_value(self):
        with self.assertRaises(DecoderError):
            Decoder().decode(1, time)

    def test_decode_time_with_str_value(self):
        with self.assertRaises(DecoderError):
            Decoder().decode('some value', time)

    def test_decode_time_with_iso_str_value(self):
        expected = time(12, 40, 30)
        s = expected.isoformat()
        self.assertEqual(expected, Decoder().decode(s, time))

        expected = time(12, 40, 30, 800)
        s = expected.isoformat()
        self.assertEqual(expected, Decoder().decode(s, time))
