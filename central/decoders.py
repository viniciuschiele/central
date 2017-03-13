"""
Decoder implementations.
"""

from datetime import date, datetime, time
from . import abc
from .compat import PY2, string_types, text_type
from .exceptions import DecoderError


__all__ = [
    'Decoder'
]


class Decoder(abc.Decoder):
    """
    A decoder implementation that decodes most of common Python data types.

    Example usage:

    .. code-block:: python

        from central.decoders import Decoder
        from datetime import datetime

        decoder = Decoder.instance()
        dt = decoder.decode('2017-01-01', type=datetime)

        print(dt.year)
        print(dt.month)
        print(dt.day)

    """

    true_values = ['1', 't', 'true', 'y']
    false_values = ['0', 'f', 'false', 'n']
    list_delimiter = ','
    dict_delimiter = ';'

    def __init__(self):
        self._converters = {
            bool: self._to_bool,
            float: self._to_float,
            int: self._to_int,
            text_type: self._to_str,
            list: self._to_list,
            dict: self._to_dict,
            date: self._to_date,
            datetime: self._to_datetime,
            time: self._to_time,
        }

        if PY2:
            self._converters[str] = lambda o: str(self._to_str(o))

    @property
    def converters(self):
        """
        Get the converters.
        :return dict: The converters.
        """
        return self._converters

    @staticmethod
    def instance():
        """
        Get a singleton instance of Decoder.
        :return Decoder: The singleton instance of Decoder.
        """
        if not hasattr(Decoder, '_instance'):
            Decoder._instance = Decoder()
        return Decoder._instance

    def decode(self, o, type):
        """
        Decode the given value to the given data type.
        :param o: The value to be decoded, it cannot be None.
        :param type: The format to be decoded.
        :return: The value decoded.
        """
        if o is None:
            raise ValueError('o cannot be None')

        if type is None:
            raise ValueError('type cannot be None')

        conv = self._converters.get(type)

        if conv is None:
            raise DecoderError('Type %s not supported' % text_type(type))

        try:
            return conv(o)
        except Exception as e:
            raise DecoderError('Error decoding %s to %s' %
                               (text_type(o), text_type(type)), text_type(e))

    def _to_bool(self, o):
        """
        Convert a given object to bool.
        :param o: The object to be converted.
        :return bool: The bool value converted.
        """
        if isinstance(o, bool):
            return o

        s = text_type(o).lower()

        if s in self.true_values:
            return True

        if s in self.false_values:
            return False

        raise ValueError('Could not convert string to bool: ' + s)

    def _to_float(self, o):
        """
        Convert a given object to float.
        :param o: The object to be converted.
        :return float: The float value converted.
        """
        return float(o)

    def _to_int(self, o):
        """
        Convert a given object to int.
        :param o: The object to be converted.
        :return int: The int value converted.
        """
        return int(o)

    def _to_str(self, o):
        """
        Convert a given object to str.
        :param o: The object to be converted.
        :return str: The str value converted.
        """
        return text_type(o)

    def _to_list(self, o):
        """
        Convert a given object to list.
        :param o: The object to be converted.
        :return list: The list value converted.
        """
        if isinstance(o, list):
            return o

        if not isinstance(o, string_types):
            raise TypeError('Expected str, got %s' % text_type(type(o)))

        items = o.split(self.list_delimiter)

        for i, item in enumerate(items):
            items[i] = item.strip()

        return items

    def _to_dict(self, o):
        """
        Convert a given object to dict.
        :param o: The object to be converted.
        :return dict: The dict value converted.
        """
        if isinstance(o, dict):
            return o

        if not isinstance(o, string_types):
            raise TypeError('Expected str, got %s' % text_type(type(o)))

        pairs = o.split(self.dict_delimiter)

        d = {}

        for pair in pairs:
            kv = pair.split('=')

            key = kv[0].strip()
            value = kv[1].strip()

            d[key] = value

        return d

    def _to_date(self, o):
        """
        Convert an ISO8601-formatted date string to a date object.
        :param o: The object to be converted.
        :return date: The date value converted.
        """
        if isinstance(o, datetime):
            return o.date()

        if isinstance(o, date):
            return o

        if not isinstance(o, string_types):
            raise TypeError('Expected str, got %s' % text_type(type(o)))

        return datetime.strptime(o[:10], '%Y-%m-%d').date()

    def _to_datetime(self, o):
        """
        Convert an ISO8601-formatted datetime string to a datetime object.
        :param o: The object to be converted.
        :return datetime: The datetime value converted.
        """
        if isinstance(o, datetime):
            return o

        if isinstance(o, date):
            return datetime(o.year, o.month, o.day)

        if not isinstance(o, string_types):
            raise TypeError('Expected str, got %s' % text_type(type(o)))

        # Strip off timezone info.
        return datetime.strptime(o[:19], '%Y-%m-%dT%H:%M:%S')

    def _to_time(self, o):
        """
        Convert an ISO8601-formatted time string to a time object.
        :param o: The object to be converted.
        :return time: The time value converted.
        """
        if isinstance(o, time):
            return o

        if isinstance(o, datetime):
            return time(o.hour, o.minute, o.second)

        if not isinstance(o, string_types):
            raise TypeError('Expected str, got %s' % text_type(type(o)))

        if len(o) > 8:  # has microseconds
            fmt = '%H:%M:%S.%f'
        else:
            fmt = '%H:%M:%S'

        return datetime.strptime(o, fmt).time()
