from __future__ import absolute_import

from central.structures import IgnoreCaseDict
from unittest import TestCase


class TestIgnoreCaseDict(TestCase):
    def test_preserved_original_keys(self):
        d = IgnoreCaseDict()
        d['Key'] = 'value'

        self.assertEqual({'Key'}, set(d.keys()))

    def test_contains_with_case_insensitive_key(self):
        d = IgnoreCaseDict()
        d['Key'] = 'value'

        self.assertTrue('KEY' in d)

    def test_get_with_case_insensitive_key(self):
        d = IgnoreCaseDict()
        d['Key'] = 'value'

        self.assertEqual('value', d.get('KEY'))
