# test.py

import string
import random
from io import StringIO

import factoriotools

from factoriotools.tile_data import tile_names
from factoriotools.signal_data import signal_IDs
from factoriotools.signals import (
    InvalidSignalID
)
from factoriotools.tile import (
    InvalidTileID
)
from factoriotools.blueprint import (
    IncorrectBlueprintType, MalformedBlueprintString
)
from schema import SchemaError

import unittest

################################################################################

class ValidateVersion(unittest.TestCase):
    def test_versions(self):
        self.assertEqual(factoriotools.__version__, "0.1")
        self.assertEqual(factoriotools.__version_info__, (0, 1))
        self.assertEqual(factoriotools.__factorio_version__, "1.1.53.1")
        self.assertEqual(factoriotools.__factorio_version_info__, (1, 1, 53, 1))


class ValidateSignalData(unittest.TestCase):
    pass


class ValidateTileData(unittest.TestCase):
    pass


class ValidateEntityData(unittest.TestCase):
    pass


################################################################################


class SignalIDTesting(unittest.TestCase):
    def test_constructor(self):
        signal_id = factoriotools.SignalID(name = "test-name", type = "example")
        self.assertEqual(signal_id.name, "test-name")
        self.assertEqual(signal_id.type, "example")

    def test_to_dict(self):
        self.assertEqual(
            signal_IDs["signal-0"].to_dict(),
            {"name": "signal-0", "type": "virtual"}
        )

    def test_repr(self):
        self.assertEqual(
            str(signal_IDs["signal-0"]),
            "SignalID{'name': 'signal-0', 'type': 'virtual'}"
        )


class SignalUtilsTesting(unittest.TestCase):
    def test_get_signal_type(self):
        # Valid pairs
        pairs = {
            "transport-belt": "item",
            "offshore-pump": "item",
            "signal-anything": "virtual",
            "signal-red": "virtual",
            "crude-oil": "fluid",
            "steam": "fluid"
        }
        for signal_name, signal_type in pairs.items():
            self.assertEqual(
                factoriotools.get_signal_type(signal_name),
                signal_type
            )
        # Invalid name
        try:
            factoriotools.get_signal_type("something invalid")
        except InvalidSignalID:
            pass
        else:
            raise AssertionError("Should have raised InvalidSignalID")


class SignalTesting(unittest.TestCase):
    def test_constructor(self):
        # String arg
        signal = factoriotools.Signal("transport-belt", 100)
        self.assertEqual(signal.id.name, "transport-belt")
        self.assertEqual(signal.id.type, "item")
        self.assertEqual(signal.count, 100)
        # SignalID arg
        signal = factoriotools.Signal(signal_IDs["transport-belt"], 100)
        self.assertEqual(signal.id.name, "transport-belt")
        self.assertEqual(signal.id.type, "item")
        self.assertEqual(signal.count, 100)
        # Invalid arg
        try:
            signal = factoriotools.Signal(False, 200)
        except ValueError:
            pass
        else:
            raise AssertionError("Should have raised ValueError")

    def test_change_id(self):
        # String arg
        signal = factoriotools.Signal("transport-belt", -25)
        signal.change_id("fast-transport-belt")
        self.assertEqual(signal.id.name, "fast-transport-belt")
        self.assertEqual(signal.count, -25)
        # SignalID arg
        signal.change_id(signal_IDs["express-transport-belt"])
        self.assertEqual(signal.id.name, "express-transport-belt")
        self.assertEqual(signal.count, -25)
        # Invalid arg
        try:
            signal.change_id(False)
        except ValueError:
            pass
        else:
            raise AssertionError("Should have raised ValueError")

    def test_to_dict(self):
        signal = factoriotools.Signal("transport-belt", 2000000000)
        self.assertEqual(
            signal.to_dict(),
            {
                "signal": {
                    "name": "transport-belt",
                    "type": "item"
                },
                "count": 2000000000
            }
        )
        signal.count = 100
        self.assertEqual(
            signal.to_dict(),
            {
                "signal": {
                    "name": "transport-belt",
                    "type": "item"
                },
                "count": 100
            }
        )

    def test_repr(self):
        signal = factoriotools.Signal("transport-belt", 100)
        self.assertEqual(
            str(signal),
            "Signal{'count': 100, 'signal': {'name': 'transport-belt', 'type': 'item'}}"
        )


class TileTesting(unittest.TestCase):
    def test_constructor(self):
        # Specific position
        tile = factoriotools.Tile("hazard-concrete-right", 100, -100)
        self.assertEqual(tile.name, "hazard-concrete-right")
        self.assertEqual(tile.x,  100)
        self.assertEqual(tile.y, -100)
        # Default position
        tile = factoriotools.Tile("hazard-concrete-right")
        self.assertEqual(tile.name, "hazard-concrete-right")
        self.assertEqual(tile.x, 0)
        self.assertEqual(tile.y, 0)
        # Invalid name
        try:
            tile = factoriotools.Tile("weeeeee")
        except InvalidTileID:
            pass
        else:
            raise AssertionError("Should have raised InvalidTileID")
        pass

    def test_change_name(self):
        tile = factoriotools.Tile("hazard-concrete-left")
        self.assertEqual(tile.name, "hazard-concrete-left")
        self.assertEqual(tile.x, 0)
        self.assertEqual(tile.y, 0)
        tile.change_name("refined-hazard-concrete-left")
        self.assertEqual(tile.name, "refined-hazard-concrete-left")
        self.assertEqual(tile.x, 0)
        self.assertEqual(tile.y, 0)
        # Invalid name
        try:
            tile.change_name("weeeeee")
        except InvalidTileID:
            pass
        else:
            raise AssertionError("Should have raised InvalidTileID")
        pass

    def test_set_position(self):
        tile = factoriotools.Tile("landfill", 0, 0)
        tile.set_position(-123, 123)
        self.assertEqual(tile.x, -123)
        self.assertEqual(tile.y, 123)

    def test_to_dict(self):
        tile = factoriotools.Tile("landfill", 123, 123)
        self.assertEqual(
            tile.to_dict(),
            {"name": "landfill", "position": {"x": 123, "y": 123}}
        )

    def test_repr(self):
        tile = factoriotools.Tile("concrete", 0, 0)
        self.assertEqual(
            str(tile),
            "<Tile>{'name': 'concrete', 'position': {'x': 0, 'y': 0}}"
        )


class EntityTesting(unittest.TestCase):
    pass


class BlueprintUtilsTesting(unittest.TestCase):
    def test_string_2_JSON(self):
        # Blueprints
        resulting_dict = factoriotools.string_2_JSON("0eNqN0N0KwjAMBeB3yXU33E/d7KuISKdRCltW2mxsjL67ncIEvdDLHnK+lCzQtANaZ4hBLWAuPXlQxwW8uZNu14xni6BgNI6HmAgg3a3BayLZQRBg6IoTqCycBCCxYYMv5vmYzzR0Dbo4sLVv2nPCTpO3veOkwZYjbXsfuz2te6Mnd1UqBcygkqyuUxmC+CLzjfyt7X9qxabhZB16/8cf6w813sAwdtF431bAiM4/W3mdldUhr8qDLCtZhPAAeZl+cQ==")
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
            factoriotools.JSON_2_string(test_dict),
            "0eNplyEEKgCAURdG9vLFE2sytRMiPzCQx+Fog0t6ThjW6h1tBPPvMxMUslMlIaCm+U0Grrv/tAXpEyuyjKxCvnLPceOTNcsIksPpIIRToit224KJwWtz3AzZ8Kjs="
        )
        # Blueprint Books
        # TODO

    def test_encode_version(self):
        self.assertEqual(
            factoriotools.encode_version(1, 1, 50, 1),
            281479274954753
        )

    def test_decode_version(self):
        self.assertEqual(
            factoriotools.decode_version(281479274954753),
            (1, 1, 50, 1)
        )

    def test_get_blueprintable_from_string(self):
        # Valid Format
        blueprintable = factoriotools.get_blueprintable_from_string(
            "0eNqrVkrKKU0tKMrMK1GyqlbKLEnNVbJCEtNRKkstKs7Mz1OyMrIwNDG3NDI3sTQ1MTc1rq0FAHmyE1c="
        )
        self.assertIsInstance(blueprintable, factoriotools.Blueprint)
        # Valid format, but blueprint book string
        blueprintable = factoriotools.get_blueprintable_from_string(
            "0eNqrVkrKKU0tKMrMK4lPys/PVrKqVsosSc1VskJI6IIldJQSk0syy1LjM/NSUiuUrAx0lMpSi4oz8/OUrIwsDE3MLY3MTSxNTcxNjWtrAVWjHQY="
        )
        self.assertIsInstance(blueprintable, factoriotools.BlueprintBook)
        # Invalid format
        try:
            blueprintable = factoriotools.get_blueprintable_from_string(
                "0lmaothisiswrong"
            )
        except MalformedBlueprintString:
            pass
        else:
            raise AssertionError("Should have raised MalformedBlueprintString")


class BlueprintTesting(unittest.TestCase):
    def test_to_dict(self):
        ### Simple blueprint ###
        blueprint = factoriotools.Blueprint()
        self.assertEqual(
            blueprint.to_dict(), 
            {"item": "blueprint", "version": 281479274954753}
        )
        ### Complex blueprint ###
        # TODO

    def test_to_string(self):
        ### Simple blueprint ###
        blueprint = factoriotools.Blueprint()
        self.assertEqual(
            blueprint.to_string(),
            "0eNqrVkrKKU0tKMrMK1GyqlbKLEnNVbJCEtNRKkstKs7Mz1OyMrIwNDG3NDI3sTQ1MTc1rq0FAHmyE1c="
        )
        ### Complex blueprint ###
        # TODO

    def test_constructor_blueprint_string(self):
        ### Simple blueprint ###
        # Valid Format
        blueprint = factoriotools.Blueprint(
            "0eNqrVkrKKU0tKMrMK1GyqlbKLEnNVbJCEtNRKkstKs7Mz1OyMrIwNDG3NDI3sTQ1MTc1rq0FAHmyE1c="
        )
        self.assertEqual(
            blueprint.to_dict(), 
            {"item": "blueprint", "version": 281479274954753}
        )
        self.assertEqual(
            blueprint.to_string(), 
            "0eNqrVkrKKU0tKMrMK1GyqlbKLEnNVbJCEtNRKkstKs7Mz1OyMrIwNDG3NDI3sTQ1MTc1rq0FAHmyE1c="
        )
        self.assertIs(blueprint["entities"],  blueprint.blueprint["entities"])
        self.assertIs(blueprint["tiles"],     blueprint.blueprint["tiles"])
        self.assertIs(blueprint["schedules"], blueprint.blueprint["schedules"])
        # Valid format, but blueprint book string
        try:
            blueprint = factoriotools.Blueprint(
                "0eNqrVkrKKU0tKMrMK4lPys/PVrKqVsosSc1VskJI6IIldJQSk0syy1LjM/NSUiuUrAx0lMpSi4oz8/OUrIwsDE3MLY3MTSxNTcxNjWtrAVWjHQY="
            )
        except IncorrectBlueprintType:
            pass
        else:
            raise AssertionError("Should have raised IncorrectBlueprintType")
        # Invalid format
        try:
            blueprint = factoriotools.Blueprint("0lmaothisiswrong")
        except MalformedBlueprintString:
            pass
        else:
            raise AssertionError("Should have raised MalformedBlueprintString")
        ### Complex blueprint ###
        # TODO

    def test_load_from_string(self):
        ### Simple blueprint ###
        blueprint = factoriotools.Blueprint()
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
            raise AssertionError("Should have raised IncorrectBlueprintType")
        # Invalid blueprint
        try:
            blueprint.load_from_string("0lmaothisiswrong")
        except MalformedBlueprintString:
            pass
        else:
            raise AssertionError("Should have raised MalformedBlueprintString")

    def test_load_from_file(self):
        # Valid format
        blueprint = factoriotools.Blueprint()
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
            test_file.close()
        except IncorrectBlueprintType:
            pass
        else:
            raise AssertionError("Should have raised IncorrectBlueprintType")
        # Invalid blueprint
        try:
            test_file = StringIO()
            test_file.write("0lmaothisiswrong")
            test_file.seek(0)
            blueprint.load_from_file(test_file)
            test_file.close()
        except MalformedBlueprintString:
            pass
        else:
            raise AssertionError("Should have raised MalformedBlueprintString")

    def test_getitem(self):
        blueprint = factoriotools.Blueprint()
        blueprint.set_label("testing")
        self.assertIs(blueprint["label"], blueprint.blueprint["label"])

    def test_setitem(self):
        blueprint = factoriotools.Blueprint()
        blueprint["label"] = "testing"
        self.assertEqual(blueprint["label"], blueprint.blueprint["label"])

    def test_repr(self):
        blueprint = factoriotools.Blueprint()
        self.assertEqual(
            str(blueprint),
"""<Blueprint>
{
  "item": "blueprint",
  "version": 281479274954753
}"""
        )

    def test_set_label(self):
        blueprint = factoriotools.Blueprint()
        # String
        blueprint.set_label("testing The LABEL")
        self.assertEqual(
            blueprint.to_dict(),
            {"item": "blueprint", "label": "testing The LABEL", "version": 281479274954753}
        )
        # None
        blueprint.set_label(None)
        self.assertEqual(
            blueprint.to_dict(),
            {"item": "blueprint", "version": 281479274954753}
        )
        # Other
        try:
            blueprint.set_label(100)
        except ValueError:
            pass
        else:
            raise AssertionError("Should have raised ValueError")

    def test_set_label_color(self):
        blueprint = factoriotools.Blueprint()
        # No Args
        try:
            blueprint.set_label_color()
        except TypeError:
            pass
        else:
            raise AssertionError("Should have raised TypeError")
        # Valid 3 args
        # Test for floating point conversion error by using 0.1
        blueprint.set_label_color(0.5, 0.1, 0.5)
        self.assertEqual(
            blueprint.to_dict(),
            {
                "item": "blueprint", 
                "label_color": {"r": 0.5, "g": 0.1, "b": 0.5, "a": 1.0},
                "version": 281479274954753
            }
        )
        # Valid 4 args
        blueprint.set_label_color(1.0, 1.0, 1.0, 0.25)
        self.assertEqual(
            blueprint.to_dict(),
            {
                "item": "blueprint", 
                "label_color": {"r": 1.0, "g": 1.0, "b": 1.0, "a": 0.25},
                "version": 281479274954753
            }
        )
        # Invalid Data
        try:
            blueprint.set_label_color("red", blueprint, 5)
        except SchemaError:
            pass
        else:
            raise AssertionError("Should have raised SchemaError")

    def test_set_icons(self):
        blueprint = factoriotools.Blueprint()
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
            raise AssertionError("Should have raised InvalidSignalID")

        # Incorrect Signal Type
        try:
            blueprint.set_icons(123456, "uh-oh")
        except InvalidSignalID:
            pass
        else:
            raise AssertionError("Should have raised InvalidSignalID")

    def test_set_version(self):
        blueprint = factoriotools.Blueprint()
        blueprint.set_version(1, 0, 40, 0)
        self.assertEqual(blueprint["version"], 281474979332096)
        try:
            blueprint.set_version("1", "0", "40", "0")
        except TypeError:
            pass
        else:
            raise AssertionError("Should have raised TypeError")

    def test_read_version(self):
        blueprint = factoriotools.Blueprint()
        self.assertEqual(
            blueprint.read_version(), 
            factoriotools.__factorio_version__
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
        blueprint = factoriotools.Blueprint()

        # Checkerboard grid
        for x in range(4):
            for y in range(4):
                if (x + y) % 2 == 0:
                    name = "refined-concrete"
                else:
                    name = "refined-hazard-concrete-left"
                blueprint.add_tile(name, x, y)

        self.assertEqual(
            blueprint.to_string(),
            "0eNqlkdEKwiAYhd/lv3aQvxtrvkp0YesfCZsbzkU19u5ZEAUlMb3xwuM5x8M3w6GdaLDaOJAzaEcdyI87Bk63NILczWBUR1601GhDx6zuTW3JkX8z9KN2ujePiAvIDYOrP5eFfZlO6qbs25u11LhQAP8V8K8VU1tFfAAP7w5/m4e3rmnFmFaxzoSpXDGGK6ZyxVSuIoarSOUqYriK19Y9gzPZ8angludlhWVeFXlZePEO5cFSJQ=="
        )

    def test_tile_duplicate_ids(self):
        # Go through every tile
        for tile in tile_names:
            blueprint = factoriotools.Blueprint()
            # Create a random string so there's no bias
            letters = string.ascii_letters
            randomID = ''.join(random.choice(letters) for _ in range(10))
            try:
                blueprint.add_tile(tile, 0, 1, randomID)
                blueprint.add_tile(tile, 1, 0, randomID)
            except factoriotools.DuplicateIDException:
                continue
            else:
                raise AssertionError("Should have raised DuplicateIDException")

    def test_get_tile_at_position(self):
        blueprint = factoriotools.Blueprint()
        blueprint.add_tile("refined-concrete", 0, 0)
        blueprint.add_tile("landfill", 10, 10)

        self.assertIs(
            blueprint.tile_at_position(0, 0),
            blueprint.tiles[0]
        )
        self.assertIs(
            blueprint.tile_at_position(10, 10),
            blueprint.tiles[1]
        )
        try:
            blueprint.tile_at_position(5, 5).set_position(15, 15)
        except AttributeError:
            pass
        else:
            raise AssertionError("Should have raised AttributeError")

    def test_get_tile_with_id(self):
        blueprint = factoriotools.Blueprint()
        blueprint.add_tile("refined-concrete", 0, 0, "the_id")
        self.assertIs(blueprint.tile_with_id('the_id'), blueprint["tiles"][0])
        try:
            blueprint.tile_with_id("another_id")
        except KeyError:
            pass
        else:
            raise AssertionError("Should have raised KeyError")


class BlueprintBookTesting(unittest.TestCase):
    pass


def main():
    # TODO: chage this so that it just executes unittest.main()
    blueprint = factoriotools.Blueprint()

    #blueprint.set_label("testing")
    #blueprint.set_label_color(1.0, 0.0, 0.0)
    #blueprint.set_icons(["signal-T", "signal-E", "signal-S", "signal-T"])

    #entity = Entity("transport-belt")
    #entity.position = {...} # throw error if wrong
    #entity.direction = Blueprint.UP # throw error if wrong (maybe Entity.UP?)
    #entity.control_behaviour = {...} # throw error if wrong
    #entity.connections = {...} # throw error if wrong
    #blueprint.addEntity(entity, "testing_id") # ID is optional

    # once an entity is created, see if we can get it back
    # we can use the numeric index if its known
    #returned_entity = blueprint.get_entity(0)
    # otherwise we can use the ID if its specified
    #returned_entity = blueprint.get_entity("testing_id")

    # Test basic entity creation
    #inserter_1 = factoriotools.Inserter("fast-inserter", position = [0, 0])

    # wooden_chest= factoriotools.StorageContainer(name="wooden-chest", position = [0, 0])
    # wooden_chest.set_bar_index(1) # remember: 0 indexed
    # steel_chest = factoriotools.new_entity("steel-chest", position = [1, 0])
    # steel_chest.set_bar_index(2)
    # storage_chest = factoriotools.new_entity("logistics-chest-storage", position = [2, 0])

    #blueprint.add_entity(wooden_chest, id = "test1")
    #blueprint.add_entity(steel_chest, id = "test2")
    #blueprint.add_entity(storage_chest, id = "test3")

    #blueprint.add_connection("red", "test1", 1, "test2", 1)
    #blueprint.add_connection("red", "test2", 1, "test3", 1)

    # Test power pole connections, both manual and automatic

    # test_group = factorio.Group("group_name")

    # test_group.add_entity("transport-belt", "blah1", direction = factorio.RIGHT)
    # test_group.add_entity("transport-belt", "blah2", direction = factorio.UP)
    # test_group.add_tile("stone-path", 0, 0)

    ##################################

    # wooden_chest = factoriotools.new_entity("wooden-chest")
    # wooden_chest.set_grid_position(0, 0)
    # blueprint.add_entity(wooden_chest, id = "wooden_chest")

    # iron_chest = factoriotools.new_entity("iron-chest")
    # iron_chest.set_grid_position(1, 0)
    # iron_chest.set_bar_index(20)
    # blueprint.add_entity(iron_chest, id = "iron_chest")

    # steel_chest = factoriotools.new_entity("steel-chest")
    # steel_chest.set_grid_position(2, 0)
    # steel_chest.set_bar_index(1)
    # blueprint.add_entity(steel_chest, id = "steel_chest")
    
    # storage_tank = factoriotools.new_entity("storage-tank")
    # storage_tank.set_grid_position(0, 1)
    # blueprint.add_entity(storage_tank, id = "storage_tank")

    # blueprint.add_circuit_connection("red", "wooden_chest", "iron_chest")
    # blueprint.add_circuit_connection("red", "iron_chest", "steel_chest")
    # blueprint.add_circuit_connection("red", "steel_chest", "storage_tank")

    # transport_belt = factoriotools.new_entity("transport-belt")
    # transport_belt.set_grid_position(0, 4)
    # blueprint.add_entity(transport_belt)
    # transport_belt.set_grid_position(1, 4)
    # transport_belt.set_enable_disable(False)
    # transport_belt.set_read_hand_contents(True)
    # transport_belt.set_read_mode(factoriotools.ReadMode.PULSE)
    # blueprint.add_entity(transport_belt, id = "yellow_belt")

    # #fast_belt = factoriotools.new_entity("fast-transport-belt")
    # fast_belt = factoriotools.TransportBelt(name="fast-transport-belt")
    # fast_belt.set_grid_position(2, 4)
    # fast_belt.set_enable_disable(True)
    # fast_belt.set_enabled_condition("electric-mining-drill", ">", 15)
    # blueprint.add_entity(fast_belt, id = "red_belt")
    # fast_belt.set_grid_position(3, 4)
    # fast_belt.set_direction(factoriotools.WEST)
    # fast_belt.set_enable_disable(True)
    # fast_belt.set_read_hand_contents(True)
    # fast_belt.set_read_mode(factoriotools.ReadMode.HOLD)
    # fast_belt.set_enabled_condition() # Reset enabled condition
    # blueprint.add_entity(fast_belt, id = "other_red_belt")
    # #fast_belt.set_name("express-transport-belt")
    # express_belt = factoriotools.TransportBelt(
    #     name="express-transport-belt", 
    #     position=[4, 4],
    #     direction = factoriotools.EAST,
    #     control_behavior={
    #         "circuit_enable_disable": True,
    #         "circuit_read_hand_contents": True,
    #         "circuit_contents_read_mode": 0,
    #         "circuit_condition": {
    #             "first_signal": "signal-blue",
    #             "comparator": ">=",
    #             "second_signal": "signal-blue"
    #         }
    #     })
    # blueprint.add_entity(express_belt, id = "blue_belt")

    # blueprint.add_circuit_connection("red", "yellow_belt", "red_belt")
    # blueprint.add_circuit_connection("green", "other_red_belt", "blue_belt")

    # underground_belt = factoriotools.new_entity("underground-belt")
    # underground_belt.set_grid_position(0, 6)
    # blueprint.add_entity(underground_belt)
    # underground_belt.set_grid_position(0, 5)
    # underground_belt.set_io_type("output")
    # blueprint.add_entity(underground_belt)

    # underground_belt = factoriotools.UndergroundBelt(name = "fast-underground-belt")
    # underground_belt.set_grid_position(1, 5)
    # underground_belt.set_io_type("output")
    # blueprint.add_entity(underground_belt)
    # underground_belt.set_grid_position(1, 6)
    # underground_belt.set_io_type("input")
    # blueprint.add_entity(underground_belt)

    # underground_belt = factoriotools.new_entity("express-underground-belt")
    # underground_belt.set_direction(factoriotools.EAST)
    # blueprint.add_entity(underground_belt, id = "under1")
    # blueprint.add_entity(underground_belt, id = "under2")

    # blueprint.find_entity_by_id("under1").set_grid_position(2, 5)
    # #blueprint.entities["under1"].set_io_type("input") # input is default
    # blueprint.find_entity_by_id("under2").set_grid_position(3, 5)
    # blueprint.find_entity_by_id("under2").set_io_type("output")

    # splitter = factoriotools.Splitter("splitter")
    # splitter.set_grid_position(0, 7)
    # blueprint.add_entity(splitter)
    # splitter.name = "fast-splitter"
    # splitter.direction = factoriotools.SOUTH
    # splitter.input_priority = "left"
    # splitter.output_priority = "right"
    # splitter.set_grid_position(2, 7)
    # blueprint.add_entity(splitter)
    # splitter.name = "express-splitter"
    # splitter.set_direction(factoriotools.EAST)
    # #splitter.set_grid_position(4, 6) # currently busted with rotated entities
    # splitter.set_absolute_position(4.5, 7) # can do this instead
    # splitter.set_input_priority(None)
    # splitter.set_output_priority("left")
    # splitter.set_filter("small-lamp")
    # blueprint.add_entity(splitter)

    # inserter = factoriotools.Inserter("burner-inserter")
    # inserter.set_direction(factoriotools.SOUTH)

    # inserter.set_grid_position(0, 8)
    # inserter.set_mode_of_operation(factoriotools.ModeOfOperation.NONE) # this is far too close to None
    # inserter.set_stack_size_override(2)
    # blueprint.add_entity(inserter, id = "a")
    
    # inserter.name = "inserter"
    # inserter.set_grid_position(1, 8)
    # inserter.set_stack_size_override(None)
    # inserter.set_mode_of_operation(None)
    # inserter.set_enabled_condition("crude-oil", "=", "heavy-oil")
    # blueprint.add_entity(inserter, id = "b")

    # inserter.name = "long-handed-inserter"
    # inserter.set_grid_position(2, 8)
    # inserter.remove_enabled_condition()
    # inserter.set_mode_of_operation(factoriotools.ModeOfOperation.NONE)
    # inserter.set_read_hand_contents(True)
    # inserter.set_read_mode(factoriotools.ReadMode.PULSE)
    # blueprint.add_entity(inserter, id = "c")

    # inserter.name = "fast-inserter"
    # inserter.set_grid_position(3, 8)
    # inserter.set_mode_of_operation(None)
    # inserter.set_read_mode(factoriotools.ReadMode.HOLD)
    # inserter.set_enabled_condition("signal-1", ">=", "signal-2")
    # print(inserter.control_behavior)
    # blueprint.add_entity(inserter, id = "d")

    # inserter.name = "stack-inserter"
    # inserter.set_grid_position(4, 8)
    # inserter.set_enabled_condition("signal-anything", ">", 0)
    # inserter.set_read_hand_contents(True)
    # inserter.set_read_mode(factoriotools.ReadMode.PULSE)
    # inserter.set_circuit_stack_size(True)
    # inserter.set_stack_control_signal("signal-S")
    # blueprint.add_entity(inserter, id = "e")

    # blueprint.add_circuit_connection("green", "a", "b")
    # blueprint.add_circuit_connection("green", "b", "c")
    # blueprint.add_circuit_connection("green", "c", "d")
    # blueprint.add_circuit_connection("green", "d", "e")

    # blueprint.add_entity("filter-inserter", position = [0, 9], id = "unwired1")
    # blueprint.add_entity("stack-filter-inserter", position = [1, 9], id = "unwired2")

    # filter_inserter = blueprint.find_entity_by_id("unwired1")
    # filter_inserter.set_item_filters([
    #     "logistic-chest-active-provider", 
    #     "logistic-chest-passive-provider",
    #     "logistic-chest-storage",
    #     "logistic-chest-buffer",
    #     "logistic-chest-requester"
    # ])
    # stack_filter_inserter = blueprint.find_entity_by_id("unwired2")
    # stack_filter_inserter.set_item_filters([
    #     "roboport"
    # ])
    # stack_filter_inserter.set_filter_mode("blacklist")
    # stack_filter_inserter.set_stack_size_override(6)

    # blueprint.add_entity(
    #     "filter-inserter", id = "wired1",
    #     position = [2, 9], 
    #     direction = factoriotools.SOUTH,
    #     control_behavior = {
    #         "circuit_mode_of_operation": factoriotools.ModeOfOperation.SET_FILTERS,
    #         "circuit_hand_read_mode": factoriotools.ReadMode.HOLD,
    #         "circuit_set_stack_size": True,
    #         "stack_control_input_signal": "signal-S"
    #     }
    # )
    # blueprint.add_entity(
    #     "stack-filter-inserter", id = "wired2",
    #     position = [3, 9],
    #     direction = factoriotools.SOUTH,
    #     control_behavior = {
    #         #"circuit_condition": ["signal-anything", ">", 10],
    #         "circuit_condition": {
    #             "first_signal": "signal-anything",
    #             "comparator": ">",
    #             "constant": 10
    #         },
    #         "circuit_read_hand_contents": True,
    #         "circuit_set_stack_size": True,
    #         "stack_control_input_signal": "signal-S"
    #     },
    #     filters = ["raw-fish"],
    #     filter_mode = "blacklist"
    # )

    # blueprint.add_circuit_connection("red", "wired1", "wired2")

    # blueprint.add_entity(
    #     "loader", 
    #     position = [0, 10],
    #     direction = factoriotools.NORTH,
    #     type = "output"
    # )
    # blueprint.add_entity(
    #     "fast-loader", 
    #     position = [1, 10],
    #     direction = factoriotools.SOUTH,
    #     filters = ["wood"],
    #     type = "input"
    # )
    # blueprint.add_entity(
    #     "express-loader", 
    #     position = [2, 10],
    #     direction = factoriotools.SOUTH,
    #     filters = ["coal", "stone", "iron-ore", "copper-ore", "uranium-ore"],
    #     type = "output"
    # )

    # wood_pole = factoriotools.ElectricPole("small-electric-pole")
    # wood_pole.set_grid_position(0, 12)
    # blueprint.add_entity(wood_pole, id = "wood_pole")
    # medium_pole = factoriotools.ElectricPole("medium-electric-pole")
    # medium_pole.set_grid_position(1, 12)
    # medium_pole.add_power_connection("wood_pole") # duplicate, but lets handle
    # medium_pole.add_power_connection("big_pole")
    # blueprint.add_entity(medium_pole, id = "medium_pole")
    # blueprint.add_entity(
    #     "big-electric-pole", id = "big_pole",
    #     position = [2, 12],
    #     neighbours = ["medium_pole", "substation"]
    # )
    # blueprint.add_entity(
    #     "substation", id = "substation",
    #     position = [4, 12],
    #     neighbours = ["big_pole"]
    # )

    # blueprint.add_power_connection("wood_pole", "medium_pole")
    # #blueprint.add_power_connection("medium_pole", "wood_pole")
    # blueprint.add_circuit_connection("red", "big_pole", "substation")
    # blueprint.add_circuit_connection("green", "big_pole", "substation")

    # blueprint.add_entity("pipe", position = [0, 14])
    # blueprint.add_entity("pipe-to-ground", position = [1, 14], direction = factoriotools.WEST)
    # blueprint.add_entity("pipe-to-ground", position = [2, 14], direction = factoriotools.EAST)

    # pump = factoriotools.Pump("pump")
    # pump.set_direction(factoriotools.EAST)
    # pump.set_grid_position(3, 14)
    # pump.set_enabled_condition("substation", ">", 1)
    # blueprint.add_entity(pump, id = "pump")

    # blueprint.add_circuit_connection("red", "substation", "pump")
    # blueprint.add_circuit_connection("green", "substation", "pump")

    #########################################

    rail = factoriotools.StraightRail("straight-rail")
    rail.set_grid_position(0, 0)
    for i in range(8):
        rail.set_direction(i)
        blueprint.add_entity(rail)

    rail.set_direction(factoriotools.EAST)
    for i in range(4):
        rail.set_grid_position((i + 1) * 2, 0)
        blueprint.add_entity(rail)

    rail = factoriotools.CurvedRail("curved-rail")
    rail.set_grid_position(12, -2)
    # for i in range(0, 8, 2):
    #     rail.set_direction(i)
    #     blueprint.add_entity(rail)
    rail.set_direction(factoriotools.EAST)
    blueprint.add_entity(rail)
    rail.set_grid_position(12, 0)
    rail.set_direction(factoriotools.SOUTHEAST)
    blueprint.add_entity(rail)

    locomotive = factoriotools.Locomotive("locomotive")
    locomotive.set_absolute_position(5, 1)
    locomotive.set_orientation(0.75)
    blueprint.add_entity(locomotive)

    print(blueprint)
    print(blueprint.to_string())

if __name__ == "__main__":
    main()