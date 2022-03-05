# blueprint.py

from draftsman._factorio_version import __factorio_version_info__

import draftsman.utils as utils
# from draftsman.signatures import (
#     COLOR, 
#     ICON, 
#     BLUEPRINT, 
#     BLUEPRINT_BOOK
# )
from draftsman import signatures
from draftsman.errors import (
    IncorrectBlueprintType,
    DuplicateIDException,
    MalformedBlueprintString,
    EntityNotCircuitConnectable,
    EntityNotPowerConnectable,
    InvalidSignalID
)
from draftsman.entity import new_entity
from draftsman.prototypes.mixins import Entity # TODO: change this
from draftsman.tile import Tile
from draftsman.signal import signal_IDs
from draftsman.utils import get_signal_type


import base64
import copy
from io import FileIO
import json
from logging import FileHandler
from typing import Any, Union
import zlib

# TODO: maybe add error checking?
# Checking if the signals passed into setIcons are actual signals, etc.
# TODO: figure out a way to specify all the regular entities
# TODO: make sure entities cannot be placed on top of one another
# TODO: add groups (back)
# TODO: add more Blueprint member functions
# TODO: complete BlueprintBook
# TODO: GAY RIGHTS
# TODO: Limit blueprints to 10,000 tiles x 10,000 tiles
# "Ordered to create blueprint with unreasonable size"
# TODO: move wire connection assertion checks into entity

class BiDict(dict):
    def __init__(self, *args, **kwargs):
        super(BiDict, self).__init__(*args, **kwargs)
        self.inverse = {}
        for key, value in self.items():
            self.inverse[value] = key
            # If we want multiple key -> value pairs:
            #self.inverse.setdefault(value, []).append(key)

    def __setitem__(self, key: Any, value: Any) -> None:
        if key in self:
            del self.inverse[self[key]]
        #    self.inverse[self[key]].remove(key)
        super(BiDict, self).__setitem__(key, value)
        self.inverse[value] = key

    # def __getitem__(self, key: Any) -> Any:
    #     pass

    def __delitem__(self, key: Any) -> None:
        if self[key] in self.inverse and not self.inverse[self[key]]:
            del self.inverse[self[key]]
        super(BiDict, self).__delitem__(key)

class Blueprint:
    """
    Factorio Blueprint class. Pretty standard, although notable features include
    the ability to store ids associated to each entity for ease of access.
    """
    def __init__(self, blueprint_string=None):
        """
        Creates a Blueprint class. Will load the data from `blueprint_string`
        if provided, otherwise initializes with defaults.

        Args:
            blueprint_string (str): Factorio-format blueprint string
        """
        # We specify self.root and self.blueprint regardless of whether or not
        # a blueprint string is provided
        if blueprint_string is not None:
            self.load_from_string(blueprint_string)
        else:
            self.blueprint = dict()
            self.blueprint["item"] = "blueprint"
            self._setup_defaults()

        # Create a complimentary list to store entity IDs. These allow the user
        # to specify names to each component to aid in referencing specific 
        # component before their final numeric values are known.
        self.entity_numbers = BiDict()
        self.tile_numbers = BiDict()
        self.schedule_numbers = BiDict()

    def load_from_string(self, blueprint_string: str) -> None:
        """
        Load the Blueprint with the contents of `blueprint_string`.

        Args:
            blueprint_string (str): Factorio-encoded blueprint string
        """
        root = utils.string_2_JSON(blueprint_string)
        # Ensure that the blueprint string actually points to a blueprint
        if "blueprint" not in root:
            raise IncorrectBlueprintType
        self.blueprint  = root["blueprint"]
        self._setup_defaults()

        # Attempt to load entities
        self._load_entities_from_root()

    def load_from_file(self, blueprint_file: FileIO) -> None:
        """
        Load the Blueprint with the contents file handle `blueprint_file`.

        Args:
            blueprint_file (file-object): File object to read the data from
        """
        root = utils.string_2_JSON(blueprint_file.read())
        if "blueprint" not in root:
            raise IncorrectBlueprintType
        self.blueprint = root["blueprint"]
        self._setup_defaults()

        # Attempt to load entities
        self._load_entities_from_root()

    def set_label(self, label: str) -> None:
        """
        Sets the Blueprint's label (title). Setting label to `None` deletes the
        parameter from the Blueprint.

        Args:
            label (str): The new title of the blueprint

        Raises:
            ValueError if `label` is not a string
        """
        if label is None:
            if "label" in self.blueprint:
                del self.blueprint["label"]
        elif isinstance(label, str):
            self.blueprint["label"] = label
        else:
            raise ValueError("`label` must be a string!")

    def set_label_color(self, r: float, g: float, 
                        b: float, a: float = 1.0) -> None:
        """
        Sets the color of the Blueprint's label (title).

        Args:
            r (float): Red component, 0.0 - 1.0
            g (float): Green component, 0.0 - 1.0
            b (float): Blue component, 0.0 - 1.0
            a (float): Alpha component, 0.0 - 1.0

        Raises:
            SchemaError if any of the values cannot be resolved to floats
        """
        data = signatures.COLOR.validate({"r": r, "g": g, "b": b, "a": a})
        self.blueprint["label_color"] = data

    def set_icons(self, *signals) -> None:
        """
        Sets the icon or icons associated with the blueprint.
        
        Args:
            *signals: List of signal names to set as icons

        Raises:
            InvalidSignalID if any signal is not a string or unknown
        """
        # Reset the current icon list, or initialize it if it doesn't exist
        self.blueprint["icons"] = list()

        for i, signal in enumerate(signals):
            out = {"index": i + 1 }
            try: 
                out["signal"] = signal_IDs[signal].to_dict()
            except KeyError:
                raise InvalidSignalID("'" + str(signal) + "'")
            # This is probably redundant
            out = signatures.ICON.validate(out)
            self.blueprint["icons"].append(out)

    def set_description(self, description: str) -> None:
        """
        Sets the description for the blueprint.
        """
        self.blueprint["description"] = description

    def set_version(self, major: int, minor: int, 
                    patch: int = 0, dev_ver: int = 0) -> None:
        """
        Sets the intended version of the Blueprint.

        Args:
            major (int): Major version number
            minor (int): Minor version number
            patch (int): Patch number
            dev_ver (int): Development version
        """
        self.blueprint["version"] = utils.encode_version(major, minor, patch, dev_ver)

    def add_entity(self, entity: Union[Entity, str], **kwargs) -> None:
        """
        """
        entity_id = None
        if "id" in kwargs:
            entity_id = kwargs["id"]
            #entity.id = kwargs["id"]
        elif hasattr(entity, "id"):
            entity_id = entity.id
        
        if entity_id is not None:
            if entity_id in self.entity_numbers: # Same ID!
                raise DuplicateIDException(entity_id)

        if isinstance(entity, str):
            entity = new_entity(entity, **kwargs)

        # TODO: if entity is hidden, warn the user
        # TODO: if the current entity would overlap another, warn the user

        # Create a validated copy of the data?
        #data_copy = ENTITY_SCHEMA.validate(data)

        # DEEPCopy so we're not stupid
        entity_copy = copy.deepcopy(entity)

        if "id" in kwargs:
            entity_copy.id = kwargs["id"]

        # Add entity_number based on current entity length
        n = len(self.entities)

        # Add the entity to entities
        self.entities.append(entity_copy)
        
        # Keep track of the id and the entity it points to
        if entity_id is not None:
            self.entity_numbers[entity_id] = n
        else:
            self.entity_numbers.inverse[n] = None

    def set_entity_id(self, entity_number: int, id: str) -> None:
        """
        Adds an `id` to an already added Entity.
        """
        self.entity_numbers[id] = entity_number

    def find_entity_by_id(self, id: str) -> Entity:
        """
        Gets the entity with the corresponding `id` assigned to it. If you want
        to get the entity by index, use `blueprint.entities[i]` instead.
        """
        return self.entities[self.entity_numbers[id]]

    def find_entity(self, name: str, position: tuple) -> Entity:
        """
        Finds an entity with `name` at a grid position `position`.
        """
        # TODO
        for entity in self.entities:
            # Check to see if point contained in aabb
            # if so, return that entity
            pass

    def find_entities(self, aabb: list = None) -> list[Entity]:
        """
        Returns a list of all entities within the area `aabb`. Works similiarly
        to `LuaSurface.find_entities`. If no `aabb` is provided then the 
        function simply returns all the entities in the blueprint.
        """
        if aabb is None:
            return self.entities

        out = list()
        for entity in self.entities:
            # Check to see if entity is overlapped by aabb
            # if so, append to out
            pass
        return out

    def find_entities_filtered(self, **kwargs) -> list[Entity]:
        """
        Returns a filtered list of entities within the blueprint. Works 
        similarly to `LuaSurface.find_entities_filtered`. 

        Possible keywords include:
        * area: AABB to search in
        * position: grid position to search
        * radius: radius around position to search in
        * name: name or set of names, only entities with those names will be
        returned
        * type: type or set of types, only entities of those types will be 
        returned
        * direction: direction or set of directions, only entities facing those
        directions will be returned
        * invert: Boolean, whether or not to invert the search selection
        """

        # TODO: implement limit from LuaSurface

        search_region = self.entities
        if "position" in kwargs:
            if "radius" in kwargs:
                # Intersect entities with circle
                pass
            else:
                # Intersect entities with point
                pass
        elif "area" in kwargs:
            # Intersect entities with area
            pass

        if isinstance(kwargs.get("name", None), str):
            names = {kwargs.pop("name", None)}
        else:
            names = kwargs.pop("name", None)
        if isinstance(kwargs.get("type", None), str):
            types = {kwargs.pop("type", None)}
        else:
            types = kwargs.pop("type", None)
        if isinstance(kwargs.get("direction", None), str):
            directions = {kwargs.pop("direction", None)}
        else:
            directions = kwargs.pop("direction", None)

        def test(entity):
            if names is not None and entity.name not in names:
                return False
            if types is not None and entity.type not in types:
                return False
            if directions is not None and entity.direction not in directions:
                return False
            return True

        if "invert" in kwargs:
            return list(filter(lambda entity: not test(entity), search_region))
        else:
            return list(filter(lambda entity: test(entity), search_region))

    def remove_entity(self, entity_id: Union[int, str]) -> Entity:
        """
        Removes the entity with the id `entity_id`.
        """
        # Figure out what entity we're talking about
        if isinstance(entity_id, int):
            entity_id = self.entity_numbers.inverse[entity_id]
        entity_number = self.entity_numbers[entity_id]

        # Shift self.entity_numbers to reflect the changes to self.entities
        del self.entity_numbers[entity_id]
        for id in self.entity_numbers:
            current_number = self.entity_numbers[id]
            if current_number > entity_number:
                self.entity_numbers[id] -= 1

        # Return the removed entity because why not
        return self.entities.pop(entity_number - 1)

    def add_power_connection(self, id1: Union[str, int], id2: Union[str, int], side1: int = 1, side2: int = 1) -> None:
        """
        Adds a copper wire power connection between two entities.
        """
        if isinstance(id1, str):
            num1 = self.entity_numbers[id1]
            entity_1 = self.entities[num1]
        else:
            entity_1 = self.entities[id1]

        if isinstance(id2, str):
            num2 = self.entity_numbers[id2]
            entity_2 = self.entities[num2]
        else:
            entity_2 = self.entities[id2]
        
        if not entity_1.power_connectable:
            raise EntityNotPowerConnectable(entity_1.name)
        if not entity_2.power_connectable:
            raise EntityNotPowerConnectable(entity_2.name)
        
        # Assert that entities are close enough to connect with wires
        # TODO

        # Handle entity 1
        entity_1.add_power_connection(entity_2, side1)
        # Handle entity 2
        #entity_2.add_power_connection(entity_1, id1, side2)

    def add_circuit_connection(self, color, id1, id2, side1 = 1, side2 = 1):
        """
        Adds a circuit wire connection between two entities.
        """
        if color not in {"red", "green"}:
            raise ValueError("'{}' is an invalid circuit wire color")

        if isinstance(id1, str):
            num1 = self.entity_numbers[id1]
            entity_1 = self.entities[num1]
        else:
            entity_1 = self.entities[id1]
        
        if isinstance(id2, str):
            num2 = self.entity_numbers[id2]
            entity_2 = self.entities[num2]
        else:
            entity_2 = self.entities[id2]

        # print(entity_1)
        # print(entity_2)

        # Assert that both entities can be connected to
        # if not hasattr(entity_1, "circuit_connectable"):
        if not entity_1.circuit_connectable:
            raise EntityNotCircuitConnectable(entity_1.name)
        if not entity_2.circuit_connectable:
            raise EntityNotCircuitConnectable(entity_2.name)

        # Assert that the entities are close enough to connect with wires
        # TODO

        # If either of the connected entities is a wall, make sure that they are
        # both adjacent to a gate
        # If not, raise a warning

        # Handle entity 1
        entity_1.add_circuit_connection(color, entity_2, side1, side2)
        # # Handle entity 2
        # entity_2.add_circuit_connection(color, entity_1, side2, side1)

    def remove_circuit_connection(self, color, id1, id2, side1 = 1, side2 = 1):
        """
        Adds a circuit wire connection between two entities.
        """
        if color not in {"red", "green"}:
            raise ValueError("'{}' is an invalid circuit wire color")

        if isinstance(id1, str):
            num1 = self.entity_numbers[id1]
            entity_1 = self.entities[num1]
        else:
            entity_1 = self.entities[id1]
        
        if isinstance(id2, str):
            num2 = self.entity_numbers[id2]
            entity_2 = self.entities[num2]
        else:
            entity_2 = self.entities[id2]

        # Handle entity 1
        entity_1.remove_circuit_connection(color, entity_2, side1, side2)
        # Handle entity 2
        entity_2.remove_circuit_connection(color, entity_1, side2, side1)

    def add_tile(self, tile_name: str, x: int, y: int, id: str = None) -> None:
        """
        Add a tile to the Blueprint.
        """
        if id is not None:
            if id not in self.tile_numbers:
                self.tile_numbers[id] = len(self.tiles)
            else: # Same ID!
                raise DuplicateIDException(
                    "'{}' already used in blueprint tiles".format(id)
                )
        
        self.tiles.append(Tile(tile_name, x, y))

    def find_tile_by_id(self, id: str) -> Tile:
        """
        Gets the tile with the corresponding `id` assigned to it. If you want to
        get the tile by index, use `blueprint.tiles[i]` instead.
        """
        return self.tiles[self.tile_numbers[id]]

    def find_tile(self, x: int, y: int) -> Tile:
        """
        """
        for tile in self.tiles:
            if tile.x == x and tile.y == y:
                return tile
        return None

    def find_tiles_filtered(self, **kwargs) -> list[Tile]:
        # TODO
        pass

    def read_version(self) -> str:
        """
        Returns the version of the Blueprint in human-readable string.
        """
        version_tuple = utils.decode_version(self.blueprint["version"])
        return utils.version_tuple_2_string(version_tuple)

    def to_dict(self) -> dict:
        """
        Returns the blueprint as a dictionary. Intended for getting the 
        precursor to a Factorio blueprint string.
        """
        out_dict = copy.deepcopy(self.blueprint)

        # Convert entity objects into copies of their dict representation
        for i, entity in enumerate(self.entities):
            out_dict["entities"][i] = copy.deepcopy(entity.to_dict())
            out_dict["entities"][i]["entity_number"] = i + 1

        # Convert all tiles into dicts
        for i, tile in enumerate(self.tiles):
            out_dict["tiles"][i] = copy.deepcopy(tile.to_dict())

        # Convert all schedules into dicts
        # TODO

        # Change all connections to use entity_number
        # FIXME: this is really gross
        for entity in out_dict["entities"]:
            if "connections" in entity: # wire connections
                connections = entity["connections"]
                for side in connections:
                    if side in {"1", "2"}:
                        for color in connections[side]:
                            connection_points = connections[side][color]
                            #print(connection_points)
                            for j, point in enumerate(connection_points):
                                old = point["entity_id"]
                                if isinstance(old, str):
                                    point["entity_id"] = self.entity_numbers[old]+1
                    elif side in {"Cu0", "Cu1"}:
                        connection_points = connections[side]
                        for point in connection_points:
                            old = point["entity_id"]
                            if isinstance(old, str):
                                point["entity_id"] = self.entity_numbers[old]+1
            if "neighbours" in entity:
                neighbours = entity["neighbours"]
                for i, neighbour in enumerate(neighbours):
                    if isinstance(neighbour, str):
                        neighbours[i] = self.entity_numbers[neighbour]+1

        # Delete empty entries to compress as much as possible
        if len(out_dict["entities"]) == 0:
            del out_dict["entities"]
        if len(out_dict["tiles"]) == 0:
            del out_dict["tiles"]
        if len(out_dict["schedules"]) == 0:
            del out_dict["schedules"]

        # Make sure the final dictionary is valid
        out_dict = signatures.BLUEPRINT.validate(out_dict)
        
        return out_dict

    def to_string(self) -> str:
        """
        Returns the Blueprint as a Factorio blueprint string.
        """
        return utils.JSON_2_string({"blueprint": self.to_dict()})

    def __setitem__(self, key, value):
        self.blueprint[key] = value

    def __getitem__(self, key):
        return self.blueprint[key]

    def __repr__(self) -> str:
        return "<Blueprint>\n" + json.dumps(self.to_dict(), indent=2)

    def _setup_defaults(self):
        """
        """
        # Init default values if none
        # These values always exist in a Blueprint object, but if they are empty
        # they are deleted from the final blueprint string
        if "entities" not in self.blueprint:
            self.blueprint["entities"] = list()
        if "tiles" not in self.blueprint:
            self.blueprint["tiles"] = list()
        if "schedules" not in self.blueprint:
            self.blueprint["schedules"] = list()
        if "version" not in self.blueprint:
            maj, min, pat, dev = __factorio_version_info__
            self.blueprint["version"] = utils.encode_version(maj, min, pat, dev)

        self.entities   = self.blueprint["entities"]
        self.tiles      = self.blueprint["tiles"]
        self.schedules  = self.blueprint["schedules"]

    def _load_entities_from_root(self):
        new_entities = dict()
        for entity_dict in self.entities:
            rest_of_the_keys = copy.deepcopy(entity_dict)
            del rest_of_the_keys["name"] # TODO: change, this is clunky
            entity = new_entity(entity_dict["name"], **rest_of_the_keys)

            new_entities[entity_dict["entity_number"]] = entity
            self._entities_length += 1
            self.entity_number_to_id[entity_dict["entity_number"]] = None

        self.entities = new_entities


class BlueprintBook:
    """
    Factorio Blueprint Book.
    """
    def __init__(self, blueprint_string:str = None, blueprints:list = []):
        # Ensure that the blueprint loaded is actually the correct object type

        # add blueprints
        self.root = dict()
        self.root["blueprint_book"] = dict()

        # TODO: validate that blueprints are actually blueprints
        self.blueprints = blueprints

        self.blueprint_book = self.root
        pass

    def load_from_string(self, blueprint_string:str) -> None:
        pass

    def load_from_file(self, blueprint_file:str) -> None:
        pass

    def set_metadata(self, **kwargs) -> None: # TODO: test
        """
        Sets any or all of the Blueprints metadata elements, where:
        * `label` expects a string,
        * `label_color` expects a dict with `r`, `g`, `b`, `a` components, and
        * `icons` expects an array of `Icon` objects (see Factorio specs)

        Args:
            **kwargs: Can be any of "label", "label_color", or "icons"
        """
        valid_keywords = ["label", "label_color", "icons"]
        for key, value in kwargs.items():
            if key in valid_keywords:
                self.object[key] = value

    def set_label(self, label:str) -> None:
        """
        Sets the Blueprint's label (title).

        Args:
            label (str): The new title of the blueprint
        """
        self.object["label"] = label

    def set_label_color(self, r:float, g:float, b:float, a:float = 1.0) -> None:
        """
        Sets the color of the Blueprint's label (title).

        Args:
            r (float): Red component, 0.0 - 1.0
            g (float): Green component, 0.0 - 1.0
            b (float): Blue component, 0.0 - 1.0
            a (float): Alpha component, 0.0 - 1.0
        """
        self.object["label_color"] = {"r": r, "g": g, "b": b, "a": a}

    def set_icons(self, signal_list:list) -> None:
        """
        Sets the icon or icons associated with the blueprint. `signal_list` is
        an array of strings; each signal corresponds to their index in the 
        array. For example, if you wanted to set the first index to `wooden-box`
        and the second to `heavy-oil`, you would send 
        `["wooden-box", "heavy-oil"]` as `signal_list`.
        
        Args:
            data (list): List of signal names to set as icons
        """
        # Reset the current icon list, or initialize it if it doesn't exist
        self.object["icons"] = list()

        for i, signal in enumerate(signal_list):
            out = {"index": i + 1 }
            out["signal"] = {"name": signal, "type": get_signal_type(signal)}
            self.object["icons"].append(out)

    def set_version(self, major:int, minor:int, patch:int = 0, dev_ver:int = 0) -> None:
        """
        Sets the intended version of the Blueprint.

        Args:
            major (int): Major version number
            minor (int): Minor version number
            patch (int): Patch number
            dev_ver (int): Development version
        """
        self.object["version"] = utils.encode_version(major, minor, patch, dev_ver)

    def add_blueprint(self, blueprint:Blueprint) -> None:
        self.blueprints.append(blueprint)

    def set_blueprint(self, index:int, blueprint:Blueprint) -> None:
        self.blueprints[index] = blueprint

    def get_blueprint(self, index:int) -> Blueprint:
        return self.blueprints[index]

    def read_version(self) -> str:
        """
        Returns the version of the Blueprint in human-readable string.
        """
        version_tuple = utils.decode_version(self.object["version"])
        return '.'.join(str(i) for i in version_tuple)

    def to_dict(self) -> dict:
        pass # TODO

    def to_string(self) -> str:
        """
        """
        # Get the root dicts from each blueprint and insert them into blueprints
        self.root["blueprints"] = []
        for i, blueprint in enumerate(self.blueprints):
            blueprint_entry = {"index": i, "blueprint": blueprint.to_dict()}
            self.root["blueprints"].append(blueprint_entry)

        print(json.dumps(self.root, indent=2))
        return utils.JSON_2_string({"blueprint_book": self.root})

    def __setitem__(self, key, value):
        self.blueprint_book[key] = value

    def __getitem__(self, key):
        return self.blueprint_book[key]

    def __str__(self):
        return "< BlueprintBook >\n" + json.dumps(self.root, indent=2)


def get_blueprintable_from_string(blueprint_string:str) \
        -> Union[Blueprint, BlueprintBook]:
    """
    Gets a Blueprintable object based off of the `blueprint_string`.

    Returns:
        Either a Blueprint or a BlueprintBook, depending on the input string.

    Raises:
        NameError: if the blueprint_string cannot be resolved to be a valid
        Blueprint or BlueprintBook.
    """
    temp = utils.string_2_JSON(blueprint_string)
    if "blueprint" in temp:
        return Blueprint(blueprint_string)
    elif "blueprint_book" in temp:
        return BlueprintBook(blueprint_string)
    else:
        raise MalformedBlueprintString

if __name__ == "__main__":
    # test_dict = NestedDict()

    # test_dict["really"]["long"]["dict"]["chain"] = list()

    # test_dict["really"]["long"]["dict"]["chain"].append(NestedDict({"testing": 123}))

    # test_dict["really"]["long"]["dict"]["chain"][0]["brotha"]["other"] = 123

    # print(test_dict)

    # bp = Blueprint()

    # bp.set_version(1, 1, 50, 0)

    # print(bp["version"])

    # bp["version"] = encode_version(1, 1, 40, 0)

    # print(bp["version"])
    # print(bp.read_version())

    dict_with_some_stuff = {"hello": 100, "yes": "this is phone"}

    print(dict_with_some_stuff)

    other_dict = {"blueprint": dict_with_some_stuff}

    print(other_dict)

    #test_list = NestedList()

    #test_list[0][0][0]["testing"] = 100

    #print(test_list)

    pass