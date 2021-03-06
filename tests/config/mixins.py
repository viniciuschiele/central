from __future__ import absolute_import

from collections import MutableMapping

from central.compat import text_type
from central.config import PrefixedConfig, ReloadConfig
from central.decoders import Decoder
from central.exceptions import ConfigError
from central.interpolation import BashInterpolator, ConfigLookup
from central.utils import EventHandler


class BaseConfigMixin(object):
    def test_get_lookup_with_default_value(self):
        config = self._create_base_config()
        self.assertEqual(ConfigLookup, type(config.lookup))

    def test_set_lookup_with_lookup_value(self):
        config = self._create_base_config()
        config2 = self._create_base_config()

        config.lookup = config2.lookup

        self.assertEqual(config.lookup, config2.lookup)

    def test_set_lookup_with_none_value(self):
        config = self._create_base_config()
        config.lookup = None
        self.assertEqual(ConfigLookup, type(config.lookup))
        self.assertEqual(config, config.lookup.config)

    def test_set_lookup_with_string_value(self):
        config = self._create_base_config()
        with self.assertRaises(TypeError):
            config.lookup = 'non config'

    def test_get_updated_with_default_value(self):
        config = self._create_base_config()
        self.assertEqual(EventHandler, type(config.updated))

    def test_on_updated_with_func_value(self):
        def func():
            pass

        config = self._create_base_config()
        config.on_updated(func)

        self.assertEqual(1, len(config.updated))

    def test_reload_with_interval(self):
        config = self._create_base_config().reload_every(12345)
        self.assertEqual(ReloadConfig, type(config))
        self.assertEqual(12345, config.scheduler.interval)

    def test_prefixed_with_prefix(self):
        config = self._create_base_config().prefixed('database')
        self.assertEqual(PrefixedConfig, type(config))
        self.assertEqual('database', config.prefix)

    def test_get_before_loading(self):
        config = self._create_base_config()
        self.assertIsNone(config.get_int('key_int'))

    def test_get_after_loading(self):
        config = self._create_base_config(load_data=True)
        self.assertEqual(1, config.get_int('key_int'))

    def test_get_raw_with_key_as_none(self):
        config = self._create_base_config(load_data=True)
        with self.assertRaises(TypeError):
            config.get_raw(None)

    def test_get_raw_with_key_as_integer(self):
        config = self._create_base_config(load_data=True)
        with self.assertRaises(TypeError):
            config.get_raw(1234)

    def test_get_raw_with_existent_key(self):
        config = self._create_base_config(load_data=True)
        self.assertEqual('value', config.get_raw('key_str'))

    def test_get_value_with_nonexistent_key(self):
        config = self._create_base_config()
        self.assertIsNone(config.get_raw('not_found'))

    def test_get_value_with_key_as_none(self):
        config = self._create_base_config(load_data=True)
        with self.assertRaises(TypeError):
            config.get_value(None, str)

    def test_get_value_with_key_as_integer(self):
        config = self._create_base_config(load_data=True)
        with self.assertRaises(TypeError):
            config.get_value(1234, str)

    def test_get_value_with_type_as_none(self):
        config = self._create_base_config(load_data=True)
        with self.assertRaises(TypeError):
            config.get_value('key', None)

    def test_get_value_with_existent_key(self):
        config = self._create_base_config(load_data=True)
        self.assertEqual('value', config.get_value('key_str', str))

    def test_get_value_with_default_value(self):
        config = self._create_base_config()
        self.assertEqual(2, config.get_value('not_found', int, default=2))

    def test_get_value_with_callable_default_value(self):
        config = self._create_base_config()
        self.assertEqual(2, config.get_value('not_found', int, default=lambda: 2))

    def test_get_value_with_interpolated_key(self):
        config = self._create_base_config(load_data=True)
        self.assertEqual('value', config.get_value('key_interpolated', str))

    def test_get_value_with_existent_delimited_key(self):
        config = self._create_base_config(load_data=True)
        self.assertEqual('value', config.get_value('key_delimited.key_str', str))

    def test_get_value_with_existent_delimited_key_non_dict(self):
        config = self._create_base_config(load_data=True)
        self.assertIsNone(config.get_value('key_str.other_key', str))

    def test_get_value_with_nonexistent_delimited_key(self):
        config = self._create_base_config(load_data=True)
        self.assertIsNone(config.get_value('key_parent.not_found', str))

    def test_get_value_with_type_as_int(self):
        config = self._create_base_config(load_data=True)
        self.assertEqual(1, config.get_value('key_int_as_str', int))

    def test_get_value_with_wrong_case_key(self):
        config = self._create_base_config(load_data=True)
        self.assertEqual('value', config.get_value('key_STR', str))

    def test_get_bool_with_existent_key(self):
        config = self._create_base_config(load_data=True)
        self.assertEqual(bool, type(config.get_bool('key_int')))
        self.assertEqual(True, config.get_bool('key_int'))

    def test_get_int_with_existent_key(self):
        config = self._create_base_config(load_data=True)
        self.assertEqual(int, type(config.get_int('key_int_as_str')))
        self.assertEqual(1, config.get_int('key_int_as_str'))

    def test_get_float_with_existent_key(self):
        config = self._create_base_config(load_data=True)
        self.assertEqual(float, type(config.get_float('key_int_as_str')))
        self.assertEqual(1.0, config.get_int('key_int_as_str'))

    def test_get_str_with_existent_key(self):
        config = self._create_base_config(load_data=True)
        self.assertEqual(text_type, type(config.get_str('key_int')))
        self.assertEqual('1', config.get_str('key_int'))

    def test_get_dict_with_existent_key(self):
        config = self._create_base_config(load_data=True)
        self.assertIsInstance(config.get_dict('key_dict_as_str'), MutableMapping)
        self.assertEqual({'item_key': 'value'}, config.get_dict('key_dict_as_str'))

    def test_get_list_with_existent_key(self):
        config = self._create_base_config(load_data=True)
        self.assertIsInstance(config.get_list('key_list_as_str'), list)
        self.assertEqual(['item1', 'item2'], config.get_list('key_list_as_str'))

    def test_contains_with_existent_key(self):
        config = self._create_base_config(load_data=True)
        self.assertEqual(True, 'key_str' in config)

    def test_contains_with_nonexistent_key(self):
        config = self._create_base_config()
        self.assertEqual(False, 'not_found' in config)

    def test_contains_with_wrong_case_key(self):
        config = self._create_base_config(load_data=True)
        self.assertEqual(True, 'key_STR' in config)

    def test_get_item_with_existent_key(self):
        config = self._create_base_config(load_data=True)
        self.assertEqual('value', config['key_str'])

    def test_get_item_with_nonexistent_key(self):
        config = self._create_base_config()
        with self.assertRaises(KeyError):
            print(config['not_found'])

    def test_get_item_with_wrong_case_key(self):
        config = self._create_base_config(load_data=True)
        self.assertEqual('value', config['key_STR'])

    def test_keys(self):
        config = self._create_base_config(load_data=True)

        keys = {'key_str', 'key_int', 'key_int_as_str', 'key_dict_as_str', 'key_list_as_str', 'key_interpolated'}

        config_keys = set()

        for key in config.keys():
            config_keys.add(key)

        for key in keys:
            self.assertTrue(key in config_keys)

        self.assertTrue(('key_ignore_case' in config_keys and 'key_IGNORE_case' not in config_keys) or
                        ('key_ignore_case' not in config_keys and 'key_IGNORE_case' in config_keys))

    def test_values(self):
        config = self._create_base_config(load_data=True)

        length = len(config)
        counter = 0

        for value in config.values():
            self.assertIsNotNone(value)
            counter += 1

        self.assertEqual(counter, length)

    def test_items(self):
        config = self._create_base_config(load_data=True)

        length = len(config)
        counter = 0

        for key, value in config.items():
            self.assertIsNotNone(key)
            self.assertIsNotNone(value)
            counter += 1

        self.assertEqual(counter, length)

    def test_iter(self):
        config = self._create_base_config(load_data=True)

        keys = {'key_str', 'key_int', 'key_int_as_str', 'key_dict_as_str', 'key_list_as_str', 'key_interpolated'}

        config_keys = set()

        for key in config:
            config_keys.add(key)

        for key in keys:
            self.assertTrue(key in config_keys)

        self.assertTrue(('key_ignore_case' in config_keys and 'key_IGNORE_case' not in config_keys) or
                        ('key_ignore_case' not in config_keys and 'key_IGNORE_case' in config_keys))

    def test_len_greater_than_0(self):
        config = self._create_base_config(load_data=True)
        self.assertGreater(len(config), 0)

    def _create_base_config(self, load_data=False):
        raise NotImplementedError()


class BaseDataConfigMixin(BaseConfigMixin):
    def test_get_decoder_with_default_value(self):
        config = self._create_base_config()
        self.assertEqual(Decoder, type(config.decoder))

    def test_set_decoder_with_decoder_value(self):
        config = self._create_base_config()

        decoder = Decoder()
        config.decoder = decoder

        self.assertEqual(decoder, config.decoder)

    def test_set_decoder_with_none_value(self):
        config = self._create_base_config()
        with self.assertRaises(TypeError):
            config.decoder = None

    def test_set_decoder_with_string_value(self):
        config = self._create_base_config()
        with self.assertRaises(TypeError):
            config.decoder = 'non decoder'

    def test_get_interpolator_with_default_value(self):
        config = self._create_base_config()
        self.assertEqual(BashInterpolator, type(config.interpolator))

    def test_set_interpolator_with_interpolator_value(self):
        config = self._create_base_config()

        interpolator = BashInterpolator()
        config.interpolator = interpolator

        self.assertEqual(interpolator, config.interpolator)

    def test_set_interpolator_with_none_value(self):
        config = self._create_base_config()
        with self.assertRaises(TypeError):
            config.interpolator = None

    def test_set_interpolator_with_string_value(self):
        config = self._create_base_config()
        with self.assertRaises(TypeError):
            config.interpolator = 'non interpolator'


class NextMixin(object):
    def _create_config_with_invalid_next(self):
        raise NotImplementedError()

    def test_get_value_with_new_key(self):
        config = self._create_base_config(load_data=True)
        self.assertEqual('new value', config.get_value('key_new', str))

    def test_get_value_with_overridden_key(self):
        config = self._create_base_config(load_data=True)
        self.assertEqual('value overridden', config.get_value('key_overridden', str))

    def test_invalid_next(self):
        config = self._create_config_with_invalid_next()
        with self.assertRaises(ConfigError):
            config.load()
