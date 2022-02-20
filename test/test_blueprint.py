# blueprint.py

from factoriotools._factorio_version import (
    __factorio_version__, 
    __factorio_version_info__
)
from factoriotools.blueprint import (
    Blueprint, BlueprintBook, get_blueprintable_from_string
)
from factoriotools.errors import (
    MalformedBlueprintString, IncorrectBlueprintType, InvalidSignalID, 
    DuplicateIDException
)
from factoriotools.tile_data import tile_names
from factoriotools.utils import (
    string_2_JSON, JSON_2_string, encode_version, decode_version, 
)

from schema import SchemaError

import string
from io import StringIO
import random

from unittest import TestCase

class BlueprintUtilsTesting(TestCase):
    def test_string_2_JSON(self):
        # Blueprints
        resulting_dict = string_2_JSON("0eNqN0N0KwjAMBeB3yXU33E/d7KuISKdRCltW2mxsjL67ncIEvdDLHnK+lCzQtANaZ4hBLWAuPXlQxwW8uZNu14xni6BgNI6HmAgg3a3BayLZQRBg6IoTqCycBCCxYYMv5vmYzzR0Dbo4sLVv2nPCTpO3veOkwZYjbXsfuz2te6Mnd1UqBcygkqyuUxmC+CLzjfyt7X9qxabhZB16/8cf6w813sAwdtF431bAiM4/W3mdldUhr8qDLCtZhPAAeZl+cQ==")
        self.assertEqual(
            resulting_dict,
            {
                "blueprint": {
                    "item": "blueprint",
                    "version": 281479274954753,
                    "icons": [
                        {
                            "signal": {
                                "type": "virtual",
                                "name": "signal-0"
                            },
                            "index": 1
                        }
                    ],
                    "entities": [
                        {
                            "entity_number": 1,
                            "name": "fast-transport-belt",
                            "position": {
                                "x": 507.5,
                                "y": -188.5
                            }
                        },
                        {
                            "entity_number": 2,
                            "name": "transport-belt",
                            "position": {
                                "x": 506.5,
                                "y": -188.5
                            }
                        },
                        {
                            "entity_number": 3,
                            "name": "express-transport-belt",
                            "position": {
                                "x": 508.5,
                                "y": -188.5
                            }
                        }
                    ]
                }
            }
        )
        # Blueprint Books
        # TODO

    def test_JSON_2_string(self):
        # Blueprints
        test_dict = {
            "arbitrary_data_1": 1,
            "arbitrary_data_2": 2.0,
            "arbitrary_data_3": [
                "stringy", "strigger", "others"
            ],
            "finally": {
                "key": "value"
            }
        }
        self.assertEqual(
            JSON_2_string(test_dict),
            "0eNplyEEKgCAURdG9vLFE2sytRMiPzCQx+Fog0t6ThjW6h1tBPPvMxMUslMlIaCm+U0Grrv/tAXpEyuyjKxCvnLPceOTNcsIksPpIIRToit224KJwWtz3AzZ8Kjs="
        )
        # Blueprint Books
        # TODO

    def test_encode_version(self):
        self.assertEqual(
            encode_version(1, 1, 50, 1),
            281479274954753
        )

    def test_decode_version(self):
        self.assertEqual(
            decode_version(281479274954753),
            (1, 1, 50, 1)
        )

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
        try:
            blueprintable = get_blueprintable_from_string(
                "0lmaothisiswrong"
            )
        except MalformedBlueprintString:
            pass
        else:
            raise AssertionError("Should have raised MalformedBlueprintString") # pragma: no coverage


class BlueprintTesting(TestCase):
    def test_to_dict(self):
        ### Simple blueprint ###
        blueprint = Blueprint()
        self.assertEqual(
            blueprint.to_dict(), 
            {"item": "blueprint", 
            "version": encode_version(*__factorio_version_info__)}
        )
        self.assertIs(blueprint["entities"],  blueprint.blueprint["entities"])
        self.assertIs(blueprint["tiles"],     blueprint.blueprint["tiles"])
        self.assertIs(blueprint["schedules"], blueprint.blueprint["schedules"])
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
        self.assertIs(blueprint["entities"],  blueprint.blueprint["entities"])
        self.assertIs(blueprint["tiles"],     blueprint.blueprint["tiles"])
        self.assertIs(blueprint["schedules"], blueprint.blueprint["schedules"])
        ### Complex blueprint ###
        # TODO

    def test_constructor_blueprint_string(self):
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
        try:
            blueprint = Blueprint(
                "0eNqrVkrKKU0tKMrMK4lPys/PVrKqVsosSc1VskJI6IIldJQSk0syy1LjM/NSUiuUrAx0lMpSi4oz8/OUrIwsDE3MLY3MTSxNTcxNjWtrAVWjHQY="
            )
        except IncorrectBlueprintType:
            pass
        else:
            raise AssertionError("Should have raised IncorrectBlueprintType") # pragma: no coverage
        # Invalid format
        try:
            blueprint = Blueprint("0lmaothisiswrong")
        except MalformedBlueprintString:
            pass
        else:
            raise AssertionError("Should have raised MalformedBlueprintString") # pragma: no coverage
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
        # Valid format, but blueprint book
        try:
            blueprint.load_from_string(
                "0eNqrVkrKKU0tKMrMK4lPys/PVrKqVsosSc1VskJI6IIldJQSk0syy1LjM/NSUiuUrAx0lMpSi4oz8/OUrIwsDE3MLY3MTSxNTcxNjWtrAVWjHQY="
            )
        except IncorrectBlueprintType:
            pass
        else:
            raise AssertionError("Should have raised IncorrectBlueprintType") # pragma: no coverage
        # Invalid blueprint
        try:
            blueprint.load_from_string("0lmaothisiswrong")
        except MalformedBlueprintString:
            pass
        else:
            raise AssertionError("Should have raised MalformedBlueprintString") # pragma: no coverage

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
        try:
            test_file = StringIO()
            test_file.write(
                "0eNqrVkrKKU0tKMrMK4lPys/PVrKqVsosSc1VskJI6IIldJQSk0syy1LjM/NSUiuUrAx0lMpSi4oz8/OUrIwsDE3MLY3MTSxNTcxNjWtrAVWjHQY="
            )
            test_file.seek(0)
            blueprint.load_from_file(test_file)
        except IncorrectBlueprintType:
            test_file.close()
        else:
            raise AssertionError("Should have raised IncorrectBlueprintType") # pragma: no coverage
        # Invalid blueprint
        try:
            test_file = StringIO()
            test_file.write("0lmaothisiswrong")
            test_file.seek(0)
            blueprint.load_from_file(test_file)
        except MalformedBlueprintString:
            test_file.close()
        else:
            raise AssertionError("Should have raised MalformedBlueprintString") # pragma: no coverage

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
"""<Blueprint>
{
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
        try:
            blueprint.set_label(100)
        except ValueError:
            pass
        else:
            raise AssertionError("Should have raised ValueError") # pragma: no coverage

    def test_set_label_color(self):
        blueprint = Blueprint()
        blueprint.set_version(1, 1, 54, 0)
        # No Args
        try:
            blueprint.set_label_color()
        except TypeError:
            pass
        else:
            raise AssertionError("Should have raised TypeError") # pragma: no coverage
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
        try:
            blueprint.set_label_color("red", blueprint, 5)
        except SchemaError:
            pass
        else:
            raise AssertionError("Should have raised SchemaError") # pragma: no coverage

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
        try:
            blueprint.set_icons("wrong!")
        except InvalidSignalID:
            pass
        else:
            raise AssertionError("Should have raised InvalidSignalID") # pragma: no coverage

        # Incorrect Signal Type
        try:
            blueprint.set_icons(123456, "uh-oh")
        except InvalidSignalID:
            pass
        else:
            raise AssertionError("Should have raised InvalidSignalID") # pragma: no coverage

    def test_set_version(self):
        blueprint = Blueprint()
        blueprint.set_version(1, 0, 40, 0)
        self.assertEqual(blueprint["version"], 281474979332096)
        try:
            blueprint.set_version("1", "0", "40", "0")
        except TypeError:
            pass
        else:
            raise AssertionError("Should have raised TypeError") # pragma: no coverage

    def test_read_version(self):
        blueprint = Blueprint()
        self.assertEqual(
            blueprint.read_version(), 
            __factorio_version__
        )
        blueprint.set_version(0, 0, 0, 0)
        self.assertEqual(
            blueprint.read_version(),
            "0.0.0.0"
        )

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
        for tile in tile_names:
            blueprint = Blueprint()
            # Create a random string so there's no bias
            letters = string.ascii_letters
            randomID = ''.join(random.choice(letters) for _ in range(10))
            try:
                blueprint.add_tile(tile, 0, 1, randomID)
                blueprint.add_tile(tile, 1, 0, randomID)
            except DuplicateIDException:
                continue
            else:
                raise AssertionError("Should have raised DuplicateIDException") # pragma: no coverage

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
        try:
            blueprint.find_tile(5, 5).set_position(15, 15)
        except AttributeError:
            pass
        else:
            raise AssertionError("Should have raised AttributeError") # pragma: no coverage

    def test_find_tile_with_id(self):
        blueprint = Blueprint()
        blueprint.add_tile("refined-concrete", 0, 0, "the_id")
        self.assertIs(blueprint.find_tile_by_id('the_id'), blueprint["tiles"][0])
        try:
            blueprint.find_tile_by_id("another_id")
        except KeyError:
            pass
        else:
            raise AssertionError("Should have raised KeyError") # pragma: no coverage


class BlueprintBookTesting(TestCase):
    pass