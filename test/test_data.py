# test_data.py
# -*- encoding: utf-8 -*-

from draftsman.data import entities

import sys

if sys.version_info >= (3, 3):  # pragma: no coverage
    import unittest
else:  # pragma: no coverage
    import unittest2 as unittest


class EntitiesDataTesting(unittest.TestCase):
    def test_all_entities_have_flippable(self):
        for entity_name in entities.raw:
            try:
                entities.flippable[entity_name]
            except KeyError: # pragma: no coverage
                self.fail("'{}' had no entry in entities.flippable".format(entity_name))
