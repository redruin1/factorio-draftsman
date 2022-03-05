# test_assembling_machine.py

from draftsman.entity import AssemblingMachine, assembling_machines
from draftsman.errors import InvalidEntityID, InvalidRecipeID

from unittest import TestCase

class AssemblingMachineTesting(TestCase):
    def test_default_constructor(self):
        assembler = AssemblingMachine()
        self.assertEqual(
            assembler.to_dict(),
            {
                "name": "assembling-machine-1",
                "position": {"x": 1.5, "y": 1.5}
            }
        )

    def test_constructor_init(self):
        assembler = AssemblingMachine(
            "assembling-machine-1",
            recipe = "iron-gear-wheel"
        )
        self.assertEqual(
            assembler.to_dict(),
            {
                "name": "assembling-machine-1",
                "position": {"x": 1.5, "y": 1.5},
                "recipe": "iron-gear-wheel"
            }
        )
        assembler.set_recipe(None)
        self.assertEqual(
            assembler.to_dict(),
            {
                "name": "assembling-machine-1",
                "position": {"x": 1.5, "y": 1.5}
            }
        )

        # Warnings
        with self.assertWarns(UserWarning):
            AssemblingMachine(unused_keyword = "whatever")

        # Errors
        with self.assertRaises(InvalidEntityID):
            AssemblingMachine("not an assembling machine")
        with self.assertRaises(InvalidRecipeID):
            AssemblingMachine(recipe = "invalid")

    def test_set_recipe(self):
        # TODO: handle the case where the machine changes from a recipe that can
        # be prod moduled to a recipe where it cannot; throw a warning if that's
        # the case
        pass