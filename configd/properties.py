from . import abc
from .utils.event import EventHandler
from .utils.version import Version


class PropertyManager(abc.PropertyManager):
    """
    Implementation of PropertyManager which keeps track of any change
    on the config source attached to it.

    The PropertyContainer returned are reused for each property name.
    Once created a PropertyContainer property cannot be removed,
    however, listeners may be added and removed.

    Example usage:

    .. code-block:: python

        from configd.config import MemoryConfig
        from configd.properties import PropertyManager

        config = MemoryConfig(data={'key': 'value'})
        properties = PropertyManager(config)

        prop = properties.get_property('key').as_type(str, 'default value')

        value = prop.get()

        def prop_updated(value):
            print(value)

        prop.updated.add(prop_updated)

        config.set('key', 'new value')

    :param abc.Config: The config source which provides the values for properties.
    """
    def __init__(self, config):
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
        self._name = name
        self._config = config
        self._version = version
        self._properties = {}

    def as_type(self, cast, default):
        """
        Get a cached property based on the given type.
        :param cast: The type to convert the value to.
        :param default: The default value used if the
            config source doesn't hold the property name.
        :return Property: The property object.
        """
        key = (cast, default)

        prop = self._properties.get(key)

        if prop is None:
            prop = self._properties[key] = Property(self._name, default, cast, self._config, self._version)

        return prop


class Property(abc.Property):
    """
    Implementation of Property which caches the latest value
    retrieved from the config source.

    It should be created by PropertyContainer.

    :param str name: The name of the property.
    :param default: The default value used if the
        config source doesn't hold the property name.
    :param cast: The type to convert the value to.
    :param abc.Config: The config source which provides the value to the property.
    :param Version version: The current version of the data,
        used to know if data of the property has been changed.
    """
    def __init__(self, name, default, cast, config, version):
        self._name = name
        self._default = default
        self._cast = cast
        self._config = config
        self._master_version = version
        self._current_version = -1
        self._value = None
        self._updated = EventHandler(after_add_func=self._after_add_updated,
                                     after_remove_func=self._after_remove_updated)

    def get(self):
        """
        Get the most recent value of the property.
        :return: The most recent value of the property.
        """
        latest_version = self._master_version.number

        if self._current_version != latest_version:
            self._current_version = latest_version
            self._value = self._config.get(self._name, self._default, self._cast)

        return self._value

    @property
    def updated(self):
        """
        Get the updated event handler.
        :return EventHandler: The event handler.
        """
        return self._updated

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
