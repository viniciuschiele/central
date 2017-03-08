from __future__ import absolute_import

from configd.config import PollingConfig, PrefixedConfig
from configd.decoders import Decoder
from configd.exceptions import ConfigError
from configd.interpolation import StrInterpolator, ConfigStrLookup
from configd.utils.compat import text_type
from configd.utils.event import EventHandler


class BaseConfigMixin(object):
    def test_get_lookup_with_default_value(self):
        config = self._create_base_config()
        self.assertEqual(ConfigStrLookup, type(config.lookup))

    def test_set_lookup_with_lookup_value(self):
        config = self._create_base_config()
        config2 = self._create_base_config()

        config.lookup = config2.lookup

        self.assertEqual(config.lookup, config2.lookup)

    def test_set_lookup_with_none_value(self):
        config = self._create_base_config()
        config.lookup = None
        self.assertEqual(ConfigStrLookup, type(config.lookup))
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

    def test_polling_with_interval(self):
        config = self._create_base_config().polling(12345)
        self.assertEqual(PollingConfig, type(config))
        self.assertEqual(12345, config.scheduler.interval)

    def test_prefixed_with_prefix(self):
        config = self._create_base_config().prefixed('database')
        self.assertEqual(PrefixedConfig, type(config))
        self.assertEqual('database.', config.prefix)

    def test_get_before_loading(self):
        config = self._create_base_config()
        self.assertIsNone(config.get('key_int'))

    def test_get_after_loading(self):
        config = self._create_base_config(load_data=True)
        self.assertEqual(1, config.get('key_int', cast=int))

    def test_get_with_key_as_none(self):
        config = self._create_base_config()
        with self.assertRaises(TypeError):
            config.get(None)

    def test_get_with_key_as_integer(self):
        config = self._create_base_config()
        with self.assertRaises(TypeError):
            config.get(1234)

    def test_get_with_existent_key(self):
        config = self._create_base_config(load_data=True)
        self.assertEqual('value', config.get('key_str'))

    def test_get_with_nonexistent_key(self):
        config = self._create_base_config()
        self.assertIsNone(config.get('not_found'))

    def test_get_with_nonexistent_key_and_default_value(self):
        config = self._create_base_config()
        self.assertEqual(2, config.get('not_found', default=2))

    def test_get_with_interpolated_key(self):
        config = self._create_base_config(load_data=True)
        self.assertEqual('value', config.get('key_interpolated'))

    def test_get_with_existent_delimited_key(self):
        config = self._create_base_config(load_data=True)
        self.assertEqual('child', config.get('key_parent.key_child'))

    def test_get_with_existent_delimited_key_non_dict(self):
        config = self._create_base_config(load_data=True)
        self.assertIsNone(config.get('key_str.other_key', cast=text_type))

    def test_get_with_nonexistent_delimited_key(self):
        config = self._create_base_config(load_data=True)
        self.assertIsNone(config.get('key_parent.not_found'))

    def test_get_with_cast_as_int(self):
        config = self._create_base_config(load_data=True)
        self.assertEqual(1, config.get('key_int_as_str', cast=int))

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
        self.assertEqual(StrInterpolator, type(config.interpolator))

    def test_set_interpolator_with_interpolator_value(self):
        config = self._create_base_config()

        interpolator = StrInterpolator()
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

    def test_get_new_key(self):
        config = self._create_base_config(load_data=True)
        self.assertEqual('new value', config.get('key_new'))

    def test_get_overridden_key(self):
        config = self._create_base_config(load_data=True)
        self.assertEqual('value overridden', config.get('key_overridden'))

    def test_invalid_next(self):
        config = self._create_config_with_invalid_next()
        with self.assertRaises(ConfigError):
            config.load()
