# test_assembling_machine.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.entity import AssemblingMachine, assembling_machines
from draftsman.error import InvalidEntityError, InvalidRecipeError, InvalidItemError
from draftsman.warning import (
    DraftsmanWarning,
    ModuleLimitationWarning,
    ItemLimitationWarning,
)

from schema import SchemaError
import warnings

import sys

if sys.version_info >= (3, 3):  # pragma: no coverage
    from unittest import TestCase
else:  # pragma: no coverage
    from unittest2 import TestCase


class AssemblingMachineTesting(TestCase):
    def test_constructor_init(self):
        assembler = AssemblingMachine("assembling-machine-1", recipe="iron-gear-wheel")
        self.assertEqual(
            assembler.to_dict(),
            {
                "name": "assembling-machine-1",
                "position": {"x": 1.5, "y": 1.5},
                "recipe": "iron-gear-wheel",
            },
        )
        assembler.recipe = None
        self.assertEqual(
            assembler.to_dict(),
            {"name": "assembling-machine-1", "position": {"x": 1.5, "y": 1.5}},
        )

        # Warnings
        with self.assertWarns(DraftsmanWarning):
            AssemblingMachine(unused_keyword="whatever")

        # Errors
        with self.assertRaises(InvalidEntityError):
            AssemblingMachine("not an assembling machine")
        with self.assertRaises(InvalidRecipeError):
            AssemblingMachine(recipe="invalid")

    def test_set_recipe(self):
        machine = AssemblingMachine("assembling-machine-3")
        machine.set_item_request("productivity-module-3", 2)

        with warnings.catch_warnings(record=True) as w:
            machine.recipe = "iron-gear-wheel"
            self.assertEqual(len(w), 0)

        with self.assertWarns(ModuleLimitationWarning):
            machine.recipe = "wooden-chest"

        machine.set_item_request("speed-module-3", 2)
        with self.assertWarns(ModuleLimitationWarning):
            machine.recipe = "iron-chest"

    def test_set_item_request(self):
        # TODO: test items that are not modules
        machine = AssemblingMachine("assembling-machine-3")
        machine.recipe = "wooden-chest"
        with self.assertWarns(ModuleLimitationWarning):
            machine.set_item_request("productivity-module-3", 2)

        machine.set_item_request("wood", 20)
        self.assertEqual(machine.items, {"productivity-module-3": 2, "wood": 20})

        machine.recipe = None
        machine.set_item_requests(None)

        machine.set_item_request("iron-plate", 100)
        self.assertEqual(machine.items, {"iron-plate": 100})
        machine.recipe = "iron-gear-wheel"
        # Raise warning when setting recipe that conficts with request
        with self.assertWarns(ItemLimitationWarning):
            machine.recipe = "wooden-chest"

        with self.assertWarns(ItemLimitationWarning):
            machine.set_item_request("copper-cable", 100)

        machine.recipe = "electronic-circuit"

        # Errors
        with self.assertRaises(InvalidItemError):
            machine.set_item_request("incorrect", "nonsense")
        with self.assertRaises(TypeError):
            machine.set_item_request("speed-module-2", "nonsense")
