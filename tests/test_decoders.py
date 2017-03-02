from configd.decoders import DefaultDecoder
from configd.exceptions import DecoderError
from unittest import TestCase


class TestDefaultDecoder(TestCase):
    def test_decode_with_none_as_value(self):
        decoder = DefaultDecoder()
        self.assertRaises(ValueError, decoder.decode, None, str)
        self.assertRaises(ValueError, decoder.decode, 'aa', None)

    def test_decode_with_invalid_cast(self):
        decoder = DefaultDecoder()
        self.assertRaises(DecoderError, decoder.decode, 'aa', 'invalid_cast')

    def test_decode_with_non_possible_cast(self):
        decoder = DefaultDecoder()
        self.assertRaises(DecoderError, decoder.decode, 'aa', int)

    def test_decode_with_valid_parameters(self):
        decoder = DefaultDecoder()
        self.assertEqual(1, decoder.decode('1', int))
