from datetime import date, datetime, time
from .compat import binary_type, text_type, string_types

TRUE_VALUES = ['1', 't', 'true', 'y']
FALSE_VALUES = ['0', 'f', 'false', 'n']
LIST_DELIMITER = ','
DICT_DELIMITER = ';'


def to_bool(o):
    """
    Convert a given object to bool.
    :param o: The object to be converted.
    :return bool: The bool value converted.
    """
    if isinstance(o, bool):
        return o

    s = text_type(o).lower()

    if s in TRUE_VALUES:
        return True

    if s in FALSE_VALUES:
        return False

    raise ValueError('Could not convert string to bool: ' + s)


def to_bytes(o):
    """
    Convert a given object to bytes.
    :param o: The object to be converted.
    :return bytes: The bytes value converted.
    """
    return binary_type(o)


def to_float(o):
    """
    Convert a given object to float.
    :param o: The object to be converted.
    :return float: The float value converted.
    """
    return float(o)


def to_int(o):
    """
    Convert a given object to int.
    :param o: The object to be converted.
    :return int: The int value converted.
    """
    return int(o)


def to_str(o):
    """
    Convert a given object to str.
    :param o: The object to be converted.
    :return str: The str value converted.
    """
    return text_type(o)


def to_list(o):
    """
    Convert a given object to list.
    :param o: The object to be converted.
    :return list: The list value converted.
    """
    if isinstance(o, list):
        return o

    if not isinstance(o, string_types):
        raise TypeError('Expected str, got %s' % text_type(type(o)))

    items = o.split(LIST_DELIMITER)

    for i, item in enumerate(items):
        items[i] = item.strip()

    return items


def to_dict(o):
    """
    Convert a given object to dict.
    :param o: The object to be converted.
    :return dict: The dict value converted.
    """
    if isinstance(o, dict):
        return o

    if not isinstance(o, string_types):
        raise TypeError('Expected str, got %s' % text_type(type(o)))

    pairs = o.split(DICT_DELIMITER)

    d = {}

    for pair in pairs:
        kv = pair.split('=')

        key = kv[0].strip()
        value = kv[1].strip()

        d[key] = value

    return d


def to_date(o):
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


def to_datetime(o):
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


def to_time(o):
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
