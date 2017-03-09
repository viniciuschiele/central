from __future__ import absolute_import

from configd.config import MemoryConfig
from configd.property import PropertyManager, PropertyContainer, Property
from configd.compat import string_types
from configd.utils import EventHandler, Version
from threading import Event
from unittest import TestCase


class TestPropertyManager(TestCase):
    def test_init_config_with_none_value(self):
        with self.assertRaises(TypeError):
            PropertyManager(config=None)

    def test_init_config_with_str_value(self):
        with self.assertRaises(TypeError):
            PropertyManager(config='str')

    def test_get_property_with_name_as_none(self):
        properties = PropertyManager(MemoryConfig())
        with self.assertRaises(TypeError):
            properties.get_property(None)

    def test_get_property_with_name_as_int(self):
        properties = PropertyManager(MemoryConfig())
        with self.assertRaises(TypeError):
            properties.get_property(123)

    def test_get_property_with_name_as_str(self):
        properties = PropertyManager(MemoryConfig())
        self.assertEqual(PropertyContainer, type(properties.get_property('key')))

    def test_get_property_for_same_key(self):
        properties = PropertyManager(MemoryConfig())
        self.assertEqual(properties.get_property('key'), properties.get_property('key'))

    def test_invalidate_properties(self):
        config = MemoryConfig()
        properties = PropertyManager(config)

        self.assertEqual(0, properties._version.number)

        config.set('key', 'value')

        self.assertEqual(1, properties._version.number)


class TestPropertyContainer(TestCase):
    def test_init_name_with_none_value(self):
        with self.assertRaises(TypeError):
            PropertyContainer(name=None, config=MemoryConfig(), version=Version())

    def test_init_name_with_int_value(self):
        with self.assertRaises(TypeError):
            PropertyContainer(name=123, config=MemoryConfig(), version=Version())

    def test_init_config_with_none_value(self):
        with self.assertRaises(TypeError):
            PropertyContainer(name='key', config=None, version=Version())

    def test_init_config_with_int_value(self):
        with self.assertRaises(TypeError):
            PropertyContainer(name='key', config=123, version=Version())

    def test_init_version_with_none_value(self):
        with self.assertRaises(TypeError):
            PropertyContainer(name='key', config=MemoryConfig(), version=None)

    def test_init_version_with_int_value(self):
        with self.assertRaises(TypeError):
            PropertyContainer(name='key', config=MemoryConfig(), version=123)

    def test_as_bool_with_existent_key(self):
        config = MemoryConfig()
        config.set('key', '0')

        container = PropertyContainer('key', config, version=Version())

        self.assertIsInstance(container.as_bool(True).get(), bool)
        self.assertEqual(False, container.as_bool(True).get())

    def test_as_bool_with_nonexistent_key(self):
        config = MemoryConfig()
        container = PropertyContainer('key', config, version=Version())
        self.assertEqual(True, container.as_bool(True).get())

    def test_as_float_with_existent_key(self):
        config = MemoryConfig()
        config.set('key', '2')

        container = PropertyContainer('key', config, version=Version())
        self.assertIsInstance(container.as_float(1.0).get(), float)
        self.assertEqual(2, container.as_float(1.0).get())

    def test_as_float_with_nonexistent_key(self):
        config = MemoryConfig()
        container = PropertyContainer('key', config, version=Version())
        self.assertIsInstance(container.as_float(1.0).get(), float)
        self.assertEqual(1.0, container.as_float(1.0).get())

    def test_as_int_with_existent_key(self):
        config = MemoryConfig()
        config.set('key', '2')

        container = PropertyContainer('key', config, version=Version())
        self.assertIsInstance(container.as_int(1).get(), int)
        self.assertEqual(2, container.as_int(1).get())

    def test_as_int_with_nonexistent_key(self):
        config = MemoryConfig()
        container = PropertyContainer('key', config, version=Version())
        self.assertIsInstance(container.as_int(1).get(), int)
        self.assertEqual(1, container.as_int(1).get())

    def test_as_str_with_existent_key(self):
        config = MemoryConfig()
        config.set('key', 'value')

        container = PropertyContainer('key', config, version=Version())
        self.assertIsInstance(container.as_str('default value').get(), string_types)
        self.assertEqual('value', container.as_str('default value').get())

    def test_as_str_with_nonexistent_key(self):
        config = MemoryConfig()
        container = PropertyContainer('key', config, version=Version())
        self.assertIsInstance(container.as_str('default value').get(), string_types)
        self.assertEqual('default value', container.as_str('default value').get())

    def test_as_dict_with_existent_key(self):
        config = MemoryConfig()
        config.set('key', {'key': 'value'})

        container = PropertyContainer('key', config, version=Version())
        self.assertIsInstance(container.as_dict({}).get(), dict)
        self.assertEqual({'key': 'value'}, container.as_dict({}).get())

    def test_as_dict_with_nonexistent_key(self):
        config = MemoryConfig()
        container = PropertyContainer('key', config, version=Version())
        self.assertIsInstance(container.as_dict({}).get(), dict)
        self.assertEqual({}, container.as_dict({}).get())

    def test_as_list_with_existent_key(self):
        config = MemoryConfig()
        config.set('key', ['value'])

        container = PropertyContainer('key', config, version=Version())
        self.assertIsInstance(container.as_list([]).get(), list)
        self.assertEqual(['value'], container.as_list([]).get())

    def test_as_list_with_nonexistent_key(self):
        config = MemoryConfig()
        container = PropertyContainer('key', config, version=Version())
        self.assertIsInstance(container.as_list([]).get(), list)
        self.assertEqual([], container.as_list([]).get())

    def test_as_type_with_existent_key(self):
        config = MemoryConfig()
        config.set('key', '2')

        container = PropertyContainer('key', config, version=Version())
        self.assertIsInstance(container.as_type(int, 1).get(), int)
        self.assertEqual(2, container.as_type(int, 1).get())

    def test_as_type_with_nonexistent_key(self):
        config = MemoryConfig()
        container = PropertyContainer('key', config, version=Version())
        self.assertIsInstance(container.as_type(int, 1).get(), int)
        self.assertEqual(1, container.as_type(int, 1).get())

    def test_as_type_for_same_existent_key(self):
        config = MemoryConfig()
        config.set('key', '2')

        container = PropertyContainer('key', config, version=Version())

        self.assertEqual(container.as_type(int, 1), container.as_type(int, 1))


class TestProperty(TestCase):
    def test_init_name_with_none_value(self):
        with self.assertRaises(TypeError):
            Property(name=None, default=1, cast=int, config=MemoryConfig(), version=Version())

    def test_init_name_with_int_value(self):
        with self.assertRaises(TypeError):
            Property(name=123, default=1, cast=int, config=MemoryConfig(), version=Version())

    def test_init_name_with_str_value(self):
        prop = Property(name='name', default=1, cast=int, config=MemoryConfig(), version=Version())
        self.assertEqual('name', prop.name)

    def test_init_cast_with_none_value(self):
        with self.assertRaises(ValueError):
            Property(name='key', default=1, cast=None, config=MemoryConfig(), version=Version())

    def test_init_cast_with_int_value(self):
        prop = Property(name='key', default=1, cast=int, config=MemoryConfig(), version=Version())
        self.assertEqual(int, prop.cast)

    def test_init_config_with_none_value(self):
        with self.assertRaises(TypeError):
            Property(name='key', default=1, cast=int, config=None, version=Version())

    def test_init_config_with_int_value(self):
        with self.assertRaises(TypeError):
            Property(name='key', default=1, cast=int, config=123, version=Version())

    def test_init_version_with_none_value(self):
        with self.assertRaises(TypeError):
            Property(name='key', default=1, cast=int, config=MemoryConfig(), version=None)

    def test_init_version_with_int_value(self):
        with self.assertRaises(TypeError):
            Property(name='key', default=1, cast=int, config=MemoryConfig(), version=123)

    def test_get_updated_with_default_value(self):
        prop = Property(name='key', default=1, cast=int, config=MemoryConfig(), version=Version())
        self.assertEqual(EventHandler, type(prop.updated))

    def test_get_with_existent_key(self):
        config = MemoryConfig()
        config.set('key', '2')

        prop = Property('key', 1, int, config, Version())
        self.assertEqual(2, prop.get())

    def test_get_with_nonexistent_key(self):
        prop = Property('key', 1, int, MemoryConfig(), Version())
        self.assertEqual(1, prop.get())

    def test_get_with_invalidated_key(self):
        config = MemoryConfig()
        config.set('key', '2')

        version = Version()

        prop = Property('key', 1, int, config, version)

        self.assertEqual(2, prop.get())

        config.set('key', '3')

        version.number += 1

        self.assertEqual(3, prop.get())

    def test_on_updated_with_func_value(self):
        prop = Property(name='key', default=1, cast=int, config=MemoryConfig(), version=Version())

        def dummy():
            pass

        prop.on_updated(dummy)

        self.assertEqual(1, len(prop.updated))

    def test_add_updated_with_func_value(self):
        config = MemoryConfig()
        version = Version()
        ev = Event()

        prop = Property(name='key', default=1, cast=int, config=config, version=version)

        def dummy(v):
            ev.set()

        prop.updated.add(dummy)

        version.number += 1

        self.assertTrue(ev.is_set())

    def test_remove_updated_with_func_value(self):
        config = MemoryConfig()
        version = Version()
        ev = Event()

        prop = Property(name='key', default=1, cast=int, config=config, version=version)

        def dummy(v):
            ev.set()

        prop.updated.add(dummy)
        prop.updated.remove(dummy)

        version.number += 1

        self.assertFalse(ev.is_set())

    def test_str(self):
        config = MemoryConfig()
        config.set('key', '2')

        prop = Property(name='key', default=1, cast=int, config=config, version=Version())
        self.assertEqual('2', str(prop))
