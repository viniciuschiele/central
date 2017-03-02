"""
Decoder implementations.
"""

from datetime import date, datetime, time
from . import abc
from .exceptions import DecoderError
from .utils import converter


__all__ = [
    'DefaultDecoder'
]


class DefaultDecoder(abc.Decoder):
    """
    Default decoder implementation that decodes values to arbitrary types,
    it handles most of common Python data types.

    Example usage:

    .. code-block:: python

        import datetime
        from configd.decoders import DefaultDecoder

        decoder = DefaultDecoder()
        dt = decoder.decode('2017-01-01', cast=datetime.date)

        print(dt.year)
        print(dt.month)
        print(dt.day)

    """

    converters = {
        bool: converter.to_bool,
        float: converter.to_float,
        int: converter.to_int,
        str: converter.to_str,
        list: converter.to_list,
        dict: converter.to_dict,
        date: converter.to_date,
        datetime: converter.to_datetime,
        time: converter.to_time,
    }

    def decode(self, o, cast):
        """
        Decode the given value to the given data type.
        :param o: The value to be decoded, it cannot be None.
        :param cast: The format to be decoded.
        :return: The value decoded.
        """
        if o is None:
            raise ValueError('o cannot be None')

        if cast is None:
            raise ValueError('cast cannot be None')

        conv = self.converters.get(cast)

        if conv is None:
            raise DecoderError('Type %s not supported' % str(cast))

        try:
            return conv(o)
        except Exception as e:
            raise DecoderError('Error decoding %s to %s' % (str(o), str(cast)), str(e))
