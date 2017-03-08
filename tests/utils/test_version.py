from __future__ import absolute_import

from configd.utils.event import EventHandler
from configd.utils.version import Version
from unittest import TestCase


class TestVersion(TestCase):
    def test_get_changed_with_default_value(self):
        version = Version()
        self.assertEqual(EventHandler, type(version.changed))

    def test_get_number_with_default_value(self):
        version = Version()
        self.assertEqual(0, version.number)

    def test_set_number_with_int_value(self):
        version = Version()
        version.number = 2
        self.assertEqual(2, version.number)

    def test_str(self):
        version = Version()
        self.assertEqual('0', str(version))

    def test_repr(self):
        version = Version()
        self.assertEqual('Version(0)', repr(version))
