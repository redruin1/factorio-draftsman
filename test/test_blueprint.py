# blueprint.py

from draftsman._factorio_version import (
    __factorio_version__, 
    __factorio_version_info__
)
from draftsman.blueprint import (
    Blueprint, BlueprintBook, get_blueprintable_from_string
)
from draftsman.error import (
    MalformedBlueprintStringError, IncorrectBlueprintTypeError, 
    InvalidSignalError, DuplicateIDError
)
from draftsman.utils import (
    string_2_JSON, JSON_2_string, encode_version, decode_version, 
)

import draftsman.data.tiles as tiles

from schema import SchemaError

import string
from io import StringIO
import random

from unittest import TestCase


class BlueprintTesting(TestCase):
    def test_to_dict(self):
        ### Simple blueprint ###
        blueprint = Blueprint()
        self.assertEqual(
            blueprint.to_dict(), 
            {"item": "blueprint", 
            "version": encode_version(*__factorio_version_info__)}
        )
        self.assertIs(blueprint["entities"],  blueprint.root["entities"])
        self.assertIs(blueprint["tiles"],     blueprint.root["tiles"])
        self.assertIs(blueprint["schedules"], blueprint.root["schedules"])
        ### Complex blueprint ###
        # TODO

    def test_to_string(self):
        ### Simple blueprint ###
        blueprint = Blueprint()
        blueprint.set_version(1, 1, 54, 0)
        self.assertEqual(
            blueprint.to_string(),
            "0eNqrVkrKKU0tKMrMK1GyqlbKLEnNVbJCEtNRKkstKs7Mz1OyMrIwNDG3NDI3NTI0s7A0q60FAHmRE1c="
        )
        self.assertIs(blueprint["entities"],  blueprint.root["entities"])
        self.assertIs(blueprint["tiles"],     blueprint.root["tiles"])
        self.assertIs(blueprint["schedules"], blueprint.root["schedules"])
        ### Complex blueprint ###
        # TODO

    def test_constructor(self):
        ### Simple blueprint ###
        # Valid Format
        blueprint = Blueprint(
            "0eNqrVkrKKU0tKMrMK1GyqlbKLEnNVbJCEtNRKkstKs7Mz1OyMrIwNDG3NDI3NTI0s7A0q60FAHmRE1c="
        )
        self.assertEqual(
            blueprint.to_dict(), 
            {"item": "blueprint", "version": encode_version(1, 1, 54, 0)}
        )
        self.assertEqual(
            blueprint.to_string(), 
            "0eNqrVkrKKU0tKMrMK1GyqlbKLEnNVbJCEtNRKkstKs7Mz1OyMrIwNDG3NDI3NTI0s7A0q60FAHmRE1c="
        )
        self.assertIs(blueprint["entities"],  blueprint.blueprint["entities"])
        self.assertIs(blueprint["tiles"],     blueprint.blueprint["tiles"])
        self.assertIs(blueprint["schedules"], blueprint.blueprint["schedules"])
        # Valid format, but blueprint book string
        with self.assertRaises(IncorrectBlueprintTypeError):
            blueprint = Blueprint(
                "0eNqrVkrKKU0tKMrMK4lPys/PVrKqVsosSc1VskJI6IIldJQSk0syy1LjM/NSUiuUrAx0lMpSi4oz8/OUrIwsDE3MLY3MTSxNTcxNjWtrAVWjHQY="
            )
        # Invalid format
        with self.assertRaises(MalformedBlueprintStringError):
            blueprint = get_blueprintable_from_string(
                "0lmaothisiswrong"
            )
        ### Complex blueprint ###
        # TODO

    def test_load_from_string(self):
        ### Simple blueprint ###
        blueprint = Blueprint()
        # Valid format
        blueprint.load_from_string("0eNqrVkrKKU0tKMrMK1GyqlbKLEnNVbJCEtNRKkstKs7Mz1OyMrIwNDG3NDI3sTQ1MTc1rq0FAHmyE1c=")
        self.assertIs(blueprint["entities"],  blueprint.blueprint["entities"])
        self.assertIs(blueprint["tiles"],     blueprint.blueprint["tiles"])
        self.assertIs(blueprint["schedules"], blueprint.blueprint["schedules"])
        # Valid format, but blueprint book string
        with self.assertRaises(IncorrectBlueprintTypeError):
            blueprint = Blueprint(
                "0eNqrVkrKKU0tKMrMK4lPys/PVrKqVsosSc1VskJI6IIldJQSk0syy1LjM/NSUiuUrAx0lMpSi4oz8/OUrIwsDE3MLY3MTSxNTcxNjWtrAVWjHQY="
            )
        # Invalid format
        with self.assertRaises(MalformedBlueprintStringError):
            blueprint = get_blueprintable_from_string(
                "0lmaothisiswrong"
            )

    def test_load_from_file(self):
        # Valid format
        blueprint = Blueprint()
        test_file = StringIO()
        test_file.write(
            "0eNqrVkrKKU0tKMrMK1GyqlbKLEnNVbJCEtNRKkstKs7Mz1OyMrIwNDG3NDI3sTQ1MTc1rq0FAHmyE1c="
        )
        test_file.seek(0)
        blueprint.load_from_file(test_file)
        self.assertIs(blueprint["entities"], blueprint.blueprint["entities"])
        self.assertIs(blueprint["tiles"], blueprint.blueprint["tiles"])
        self.assertIs(blueprint["schedules"], blueprint.blueprint["schedules"])
        test_file.close()
        # Valid format, but blueprint book
        with self.assertRaises(IncorrectBlueprintTypeError):
            test_file = StringIO()
            test_file.write(
                "0eNqrVkrKKU0tKMrMK4lPys/PVrKqVsosSc1VskJI6IIldJQSk0syy1LjM/NSUiuUrAx0lMpSi4oz8/OUrIwsDE3MLY3MTSxNTcxNjWtrAVWjHQY="
            )
            test_file.seek(0)
            blueprint.load_from_file(test_file)
        # Invalid blueprint
        with self.assertRaises(MalformedBlueprintStringError):
            test_file = StringIO()
            test_file.write("0lmaothisiswrong")
            test_file.seek(0)
            blueprint.load_from_file(test_file)

    def test_getitem(self):
        blueprint = Blueprint()
        blueprint.set_label("testing")
        self.assertIs(blueprint["label"], blueprint.blueprint["label"])

    def test_setitem(self):
        blueprint = Blueprint()
        blueprint["label"] = "testing"
        self.assertEqual(blueprint["label"], blueprint.blueprint["label"])

    def test_repr(self):
        blueprint = Blueprint()
        blueprint.set_version(1, 1, 54, 0)
        self.assertEqual(
            str(blueprint),
"""Blueprint{
  "item": "blueprint",
  "version": 281479275216896
}"""
        )

    def test_set_label(self):
        blueprint = Blueprint()
        blueprint.set_version(1, 1, 54, 0)
        # String
        blueprint.set_label("testing The LABEL")
        self.assertEqual(
            blueprint.to_dict(),
            {
                "item": "blueprint", 
                "label": "testing The LABEL", 
                "version": encode_version(1, 1, 54, 0)
            }
        )
        # None
        blueprint.set_label(None)
        self.assertEqual(
            blueprint.to_dict(),
            {
                "item": "blueprint", 
                "version": encode_version(1, 1, 54, 0)
            }
        )
        # Other
        with self.assertRaises(ValueError):
            blueprint.set_label(100)

    def test_set_label_color(self):
        blueprint = Blueprint()
        blueprint.set_version(1, 1, 54, 0)
        # Valid 3 args
        # Test for floating point conversion error by using 0.1
        blueprint.set_label_color(0.5, 0.1, 0.5)
        self.assertEqual(
            blueprint.to_dict(),
            {
                "item": "blueprint", 
                "label_color": {"r": 0.5, "g": 0.1, "b": 0.5, "a": 1.0},
                "version": encode_version(1, 1, 54, 0)
            }
        )
        # Valid 4 args
        blueprint.set_label_color(1.0, 1.0, 1.0, 0.25)
        self.assertEqual(
            blueprint.to_dict(),
            {
                "item": "blueprint", 
                "label_color": {"r": 1.0, "g": 1.0, "b": 1.0, "a": 0.25},
                "version": encode_version(1, 1, 54, 0)
            }
        )
        # Invalid Data
        with self.assertRaises(SchemaError):
            blueprint.set_label_color("red", blueprint, 5)

    def test_set_icons(self):
        blueprint = Blueprint()
        # Single Icon
        blueprint.set_icons("signal-A")
        self.assertEqual(
            blueprint["icons"],
            [
                {
                    "signal": {
                        "name": "signal-A",
                        "type": "virtual"
                    },
                    "index": 1
                }
            ]
        )
        # Multiple Icon
        blueprint.set_icons("signal-A", "signal-B", "signal-C")
        self.assertEqual(
            blueprint["icons"],
            [
                {
                    "signal": {
                        "name": "signal-A",
                        "type": "virtual"
                    },
                    "index": 1
                },
                {
                    "signal": {
                        "name": "signal-B",
                        "type": "virtual"
                    },
                    "index": 2
                },
                {
                    "signal": {
                        "name": "signal-C",
                        "type": "virtual"
                    },
                    "index": 3
                }
            ]
        )
        # Incorrect Signal Name
        with self.assertRaises(InvalidSignalError):
            blueprint.set_icons("wrong!")

        # Incorrect Signal Type
        with self.assertRaises(InvalidSignalError):
            blueprint.set_icons(123456, "uh-oh")

    def test_set_description(self):
        blueprint = Blueprint()
        blueprint.set_description("An example description.")
        self.assertEqual(blueprint["description"], "An example description.")
        # TODO: error checking

    def test_set_version(self):
        blueprint = Blueprint()
        blueprint.set_version(1, 0, 40, 0)
        self.assertEqual(blueprint["version"], 281474979332096)
        with self.assertRaises(TypeError):
            blueprint.set_version("1", "0", "40", "0")

    def test_set_snapping_grid_size(self):
        blueprint = Blueprint()
        pass
    
    def test_set_snapping_grid_position(self):
        pass

    def test_set_absolute_snapping(self):
        pass

    def test_set_position_relative_to_grid(self):
        pass

    def test_rotate(self):
        blueprint = Blueprint()
        with self.assertRaises(NotImplementedError):
            blueprint.rotate(1)

    def test_flip(self):
        blueprint = Blueprint()
        with self.assertRaises(NotImplementedError):
            blueprint.flip()

    def test_add_entity(self):
        pass

    def test_entity_duplicate_ids(self):
        pass # TODO

    def test_add_power_connections(self):
        pass

    def test_add_connections(self):
        pass

    def test_add_tile(self):
        blueprint = Blueprint()
        blueprint.set_version(1, 1, 54, 0)

        # Checkerboard grid
        for x in range(2):
            for y in range(2):
                if (x + y) % 2 == 0:
                    name = "refined-concrete"
                else:
                    name = "refined-hazard-concrete-left"
                blueprint.add_tile(name, x, y)

        self.assertEqual(
            blueprint.to_dict(),
            {
                "item": "blueprint",
                "tiles": [
                    {
                        "name": "refined-concrete",
                        "position": {
                            "x": 0,
                            "y": 0
                        }
                    },
                    {
                        "name": "refined-hazard-concrete-left",
                        "position": {
                            "x": 0,
                            "y": 1
                        }
                    },
                    {
                        "name": "refined-hazard-concrete-left",
                        "position": {
                            "x": 1,
                            "y": 0
                        }
                    },
                    {
                        "name": "refined-concrete",
                        "position": {
                            "x": 1,
                            "y": 1
                        }
                    }
                ],
                "version": encode_version(1, 1, 54, 0)
            }
        )

    def test_tile_duplicate_ids(self):
        # Go through every tile
        for tile in tiles.raw:
            blueprint = Blueprint()
            # Create a random string so there's no bias
            letters = string.ascii_letters
            randomID = ''.join(random.choice(letters) for _ in range(10))
            with self.assertRaises(DuplicateIDError):
                blueprint.add_tile(tile, 0, 1, randomID)
                blueprint.add_tile(tile, 1, 0, randomID)

    def test_get_tile_at_position(self):
        blueprint = Blueprint()
        blueprint.add_tile("refined-concrete", 0, 0)
        blueprint.add_tile("landfill", 10, 10)

        self.assertIs(
            blueprint.find_tile(0, 0),
            blueprint.tiles[0]
        )
        self.assertIs(
            blueprint.find_tile(10, 10),
            blueprint.tiles[1]
        )
        with self.assertRaises(AttributeError):
            blueprint.find_tile(5, 5).set_position(15, 15)

    def test_find_tile_with_id(self):
        blueprint = Blueprint()
        blueprint.add_tile("refined-concrete", 0, 0, "the_id")
        self.assertIs(blueprint.tiles["the_id"], blueprint["tiles"][0])
        with self.assertRaises(KeyError):
            blueprint.tiles["another_id"]

    def test_version_tuple(self):
        blueprint = Blueprint()
        self.assertEqual(
            blueprint.version_tuple(), 
            __factorio_version_info__
        )
        blueprint.set_version(0, 0, 0, 0)
        self.assertEqual(
            blueprint.version_tuple(),
            (0, 0, 0, 0)
        )

    def test_version_string(self):
        blueprint = Blueprint()
        self.assertEqual(
            blueprint.version_string(), 
            __factorio_version__
        )
        blueprint.set_version(0, 0, 0, 0)
        self.assertEqual(
            blueprint.version_string(),
            "0.0.0.0"
        )


class BlueprintBookTesting(TestCase):
    pass


class BlueprintUtilsTesting(TestCase):
    def test_get_blueprintable_from_string(self):
        # Valid Format
        blueprintable = get_blueprintable_from_string(
            "0eNqrVkrKKU0tKMrMK1GyqlbKLEnNVbJCEtNRKkstKs7Mz1OyMrIwNDG3NDI3sTQ1MTc1rq0FAHmyE1c="
        )
        self.assertIsInstance(blueprintable, Blueprint)
        # Valid format, but blueprint book string
        blueprintable = get_blueprintable_from_string(
            "0eNqrVkrKKU0tKMrMK4lPys/PVrKqVsosSc1VskJI6IIldJQSk0syy1LjM/NSUiuUrAx0lMpSi4oz8/OUrIwsDE3MLY3MTSxNTcxNjWtrAVWjHQY="
        )
        self.assertIsInstance(blueprintable, BlueprintBook)
        # Invalid format
        with self.assertRaises(MalformedBlueprintStringError):
            blueprintable = get_blueprintable_from_string(
                "0lmaothisiswrong"
            )
