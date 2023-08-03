# test_lab.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.entity import Lab, labs
from draftsman.error import InvalidEntityError, InvalidItemError
from draftsman.warning import (
    DraftsmanWarning,
    ModuleCapacityWarning,
    ItemLimitationWarning,
)

import sys
import pytest

if sys.version_info >= (3, 3):  # pragma: no coverage
    import unittest
else:  # pragma: no coverage
    import unittest2 as unittest


class LabTesting(unittest.TestCase):
    def test_contstructor_init(self):
        lab = Lab()

        with pytest.warns(DraftsmanWarning):
            Lab(unused_keyword="whatever")

        with pytest.raises(InvalidEntityError):
            Lab("this is not a lab")

    def test_inputs(self):
        lab = Lab("lab")

        assert lab.inputs == [
            "automation-science-pack",
            "logistic-science-pack",
            "military-science-pack",
            "chemical-science-pack",
            "production-science-pack",
            "utility-science-pack",
            "space-science-pack",
        ]

    def test_set_item_request(self):
        lab = Lab("lab")

        lab.set_item_request("productivity-module-3", 2)
        assert lab.items == {"productivity-module-3": 2}
        assert lab.module_slots_occupied == 2

        # Warnings
        with pytest.warns(ModuleCapacityWarning):
            lab.set_item_request("speed-module-2", 2)
        assert lab.items == {"productivity-module-3": 2, "speed-module-2": 2}
        assert lab.module_slots_occupied == 4

        lab.set_item_request("speed-module-2", None)
        assert lab.items == {"productivity-module-3": 2}

        lab.set_item_request("automation-science-pack", 10)
        assert lab.items == {"productivity-module-3": 2, "automation-science-pack": 10}
        assert lab.module_slots_occupied == 2

        with pytest.warns(ItemLimitationWarning):
            lab.set_item_request("iron-plate", 100)
        assert lab.items == {
            "productivity-module-3": 2,
            "automation-science-pack": 10,
            "iron-plate": 100,
        }

        # Errors
        lab.set_item_requests(None)
        assert lab.module_slots_occupied == 0

        with pytest.raises(TypeError):
            lab.set_item_request(TypeError, 100)
        with pytest.raises(InvalidItemError):
            lab.set_item_request("incorrect", 100)
        with pytest.raises(TypeError):
            lab.set_item_request("logistic-science-pack", TypeError)
        with pytest.raises(ValueError):
            lab.set_item_request("logistic-science-pack", -1)

        assert lab.items == {}
        assert lab.module_slots_occupied == 0

    def test_mergable_with(self):
        lab1 = Lab("lab")
        lab2 = Lab("lab", tags={"some": "stuff"})

        assert lab1.mergable_with(lab1)

        assert lab1.mergable_with(lab2)
        assert lab2.mergable_with(lab1)

        lab2.tile_position = (1, 1)
        assert not lab1.mergable_with(lab2)

    def test_merge(self):
        lab1 = Lab("lab")
        lab2 = Lab("lab", tags={"some": "stuff"})

        lab1.merge(lab2)
        del lab2

        assert lab1.tags == {"some": "stuff"}
