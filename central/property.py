import logging

from . import abc
from .compat import string_types, text_type
from .utils import EventHandler, Version


logger = logging.getLogger(__name__)


class PropertyManager(abc.PropertyManager):
    """
    Implementation of PropertyManager which keeps track of any change
    on the config source attached to it.

    The PropertyContainer returned are reused for each property name.
    Once created a PropertyContainer property cannot be removed,
    however, listeners may be added and removed.

    Example usage:

    .. code-block:: python

        from central.config import MemoryConfig
        from central.properties import PropertyManager

        config = MemoryConfig(data={'key': 'value'})
        properties = PropertyManager(config)

        prop = properties.get_property('key').as_str('default value')

        value = prop.get()

        @prop.on_updated
        def prop_updated(value):
            print(value)

        config.set('key', 'new value')

    :param abc.Config: The config source which provides the values for properties.
    """
    def __init__(self, config):
        if not isinstance(config, abc.Config):
            raise TypeError('config must be an abc.Config')

        self._containers = {}
        self._version = Version()
        self._config = config
        self._config.updated.add(self._config_updated)

    def get_property(self, name):
        """
        Get a property for the property name.

        This implementation caches the properties
        by name, so the same object is returned
        for the same property name.

        :param str name: The name of the property.
        :return PropertyContainer: The property object.
        """
        if not isinstance(name, string_types):
            raise TypeError('name must be a str')

        container = self._containers.get(name)

        if not container:
            container = self._containers[name] = PropertyContainer(name, self._config, self._version)

        return container

    def _config_updated(self):
        """
        Called when the config source attached was changed.
        """
        self._invalidate()

    def _invalidate(self):
        """
        Invalidate the cached value in all properties.

        It forces all properties to get its value from
        the config source again.
        """
        self._version.number += 1


class PropertyContainer(abc.PropertyContainer):
    """
    Implementation of PropertyContainer which reuses
    the same Property object for each data type.

    It should be created by PropertyManager.

    :param str name: The name of the property.
    :param abc.Config: The config source which provides the value to the property.
    :param Version version: The current version of the data,
        used to know if data of the property has been changed.
    """
    def __init__(self, name, config, version):
        if not isinstance(name, string_types):
            raise TypeError('name must be a str')

        if not isinstance(config, abc.Config):
            raise TypeError('config must be an abc.Config')

        if not isinstance(version, Version):
            raise TypeError('version must be a Version')

        self._name = name
        self._config = config
        self._version = version
        self._properties = []

    def as_bool(self, default):
        """
        Get a cached bool property.
        :param default: The default value used if the
            config source doesn't hold the property name.
        :return Property: The property object.
        """
        return self.as_type(bool, default)

    def as_float(self, default):
        """
        Get a cached float property.
        :param default: The default value used if the
            config source doesn't hold the property name.
        :return Property: The property object.
        """
        return self.as_type(float, default)

    def as_int(self, default):
        """
        Get a cached int property.
        :param default: The default value used if the
            config source doesn't hold the property name.
        :return Property: The property object.
        """
        return self.as_type(int, default)

    def as_str(self, default):
        """
        Get a cached str property.
        :param default: The default value used if the
            config source doesn't hold the property name.
        :return Property: The property object.
        """
        return self.as_type(text_type, default)

    def as_dict(self, default):
        """
        Get a cached dict property.
        :param default: The default value used if the
            config source doesn't hold the property name.
        :return Property: The property object.
        """
        return self.as_type(dict, default)

    def as_list(self, default):
        """
        Get a cached list property.
        :param default: The default value used if the
            config source doesn't hold the property name.
        :return Property: The property object.
        """
        return self.as_type(list, default)

    def as_type(self, type, default):
        """
        Get a cached property based on the given type.
        :param type: The type to convert the value to.
        :param default: The default value used if the
            config source doesn't hold the property name.
        :return Property: The property object.
        """
        for prop in self._properties:
            if prop.type == type and prop.default == default:
                return prop

        prop = Property(self._name, default, type, self._config, self._version)

        self._properties.append(prop)

        return prop


class Property(abc.Property):
    """
    Implementation of Property which caches the latest value
    retrieved from the config source.

    It should be created by PropertyContainer.

    :param str name: The name of the property.
    :param default: The default value used if the
        config source does not hold the property name.
    :param type: The type to convert the value to.
    :param abc.Config: The config source which provides the value to the property.
    :param Version version: The current version of the data,
        used to know if data of the property has been changed.
    """
    def __init__(self, name, default, type, config, version):
        if not isinstance(name, string_types):
            raise TypeError('name must be a str')

        if type is None:
            raise ValueError('type cannot be None')

        if not isinstance(config, abc.Config):
            raise TypeError('config must be an abc.Config')

        if not isinstance(version, Version):
            raise TypeError('version must be a Version')

        self._name = name
        self._default = default
        self._type = type
        self._config = config
        self._master_version = version
        self._current_version = -1
        self._value = None
        self._updated = EventHandler(after_add_func=self._after_add_updated,
                                     after_remove_func=self._after_remove_updated)

    @property
    def name(self):
        """
        Get the name.
        :return str: The name.
        """
        return self._name

    @property
    def default(self):
        """
        Get the default value.
        :return: The default value.
        """
        return self._default

    @property
    def type(self):
        """
        Get the data type to be converted.
        :return: The data type to be converted.
        """
        return self._type

    @property
    def updated(self):
        """
        Get the updated event handler.
        :return EventHandler: The event handler.
        """
        return self._updated

    def get(self):
        """
        Get the most recent value of the property.
        :return: The most recent value of the property.
        """
        latest_version = self._master_version.number

        if self._current_version == latest_version:
            return self._value

        self._current_version = latest_version

        try:
            self._value = self._config.get_value(self._name, self._type, self._default)
        except:
            self._value = self._default() if callable(self._default) else self._default
            logger.warning('Unable to get current version of property %s' % self._name, exc_info=True)

        return self._value

    def on_updated(self, func):
        """
        Add a new callback for updated event.
        It can also be used as decorator.
        :param func: The callback.
        """
        self.updated.add(func)

    def _after_add_updated(self):
        """
        Add a new listener for the first subscriber of data modification.
        """
        if len(self._updated) == 1:
            self._master_version.changed.add(self._version_changed)

    def _after_remove_updated(self):
        """
        Remove the listener if there is not subscribers for data modification.
        """
        if len(self._updated) == 0:
            self._master_version.changed.remove(self._version_changed)

    def _version_changed(self):
        """
        Called when the version of the data has been changed.
        """
        self._update_value()

    def _update_value(self):
        """
        Update the value of property with the most recent value from the config source.
        """
        previous_value = self._value
        new_value = self.get()

        if previous_value != new_value:
            self._value = new_value
            self.updated(new_value)

    def __str__(self):
        """
        Get a string representation of a property.
        :return str: The string representation of a property.
        """
        return text_type(self.get())
