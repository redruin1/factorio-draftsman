# blueprint.py

from factoriotools._factorio_version import __factorio_version_info__

import factoriotools.utils as utils
from factoriotools.signatures import (
    COLOR_SCHEMA, 
    ICON_SCHEMA, 
    BLUEPRINT_SCHEMA, 
    BLUEPRINT_BOOK_SCHEMA
)
from factoriotools.errors import (
    IncorrectBlueprintType,
    DuplicateIDException,
    MalformedBlueprintString,
    EntityNotCircuitConnectable,
    EntityNotPowerConnectable
)
from factoriotools.entity import Entity, new_entity
from factoriotools.tile import Tile
from factoriotools.signals import signal_IDs, get_signal_type, InvalidSignalID

import base64
import copy
from io import FileIO
import json
from logging import FileHandler
from typing import Union
import zlib

# TODO: maybe add error checking?
# Checking if the signals passed into setIcons are actual signals, etc.

# TODO: figure out a way to specify all the regular entities

# TODO: add more Blueprint member functions

# TODO: complete BlueprintBook

# TODO: GAY RIGHTS

# TODO: Limit blueprints to 10,000 tiles x 10,000 tiles
# "Ordered to create blueprint with unreasonable size"

class Blueprint:
    """
    Factorio Blueprint class. Pretty standard, although notable features include
    the ability to store ids associated to each entity for ease of access.

    We should maintain a internal dict representation in the blueprint format, 
    as well as a set of easy to manipulate lists of objects (entities, schedules, etc.)
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
        # to specify names to each entity to aid in referencing specific 
        # entities before their final numeric values are known.
        #self.entity_metadata = dict()
        self.entity_id_to_number = {}
        self.entity_number_to_id = {}
        
        self.tile_metadata = dict()

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

    # def set_metadata(self, **kwargs) -> None: # TODO: test
    #     """
    #     Sets any or all of the Blueprints metadata elements, where:
    #     * `label` expects a string,
    #     * `label_color` expects a dict with `r`, `g`, `b`, `a` components, and
    #     * `icons` expects an array of `Icon` objects (see Factorio specs)

    #     Args:
    #         **kwargs: Can be any of "label", "label_color", or "icons"
    #     """
    #     valid_keywords = ["label", "label_color", "icons"]
    #     for key, value in kwargs.items():
    #         if key in valid_keywords:
    #             self.blueprint[key] = value

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
        data = COLOR_SCHEMA.validate({"r": r, "g": g, "b": b, "a": a})
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
            out = ICON_SCHEMA.validate(out)
            self.blueprint["icons"].append(out)

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

    def add_entity(self, entity: Union[Entity, dict], **kwargs) -> None:
        """
        """
        if isinstance(entity, str):
            entity = new_entity(entity, **kwargs)

        #data = entity.to_dict()

        # Create a validated copy of the data
        #data_copy = ENTITY_SCHEMA.validate(data)

        # DEEPCopy so we're not stupid
        entity_copy = copy.deepcopy(entity)

        # Add entity_number based on current entity length
        n = self._entities_length + 1
        #data_copy["entity_number"] = n
        # FIXME: this is inelegant, because entity_number should have no meaning to an entity on its own: only when in a blueprint does it make sense
        entity_copy.entity_number = n

        # Add the entity to entities
        #self.entities.append(entity_copy)
        self.entities[n] = entity_copy
        
        # Store the ID for use later, even if the blueprint doesn't use it
        if "id" in kwargs:
            self.entities[kwargs["id"]] = entity_copy

            self.entity_number_to_id[n] = kwargs["id"]
            self.entity_id_to_number[kwargs["id"]] = n
        else:
            self.entity_number_to_id[n] = None

        # Keep track of the amount of entities for later
        self._entities_length += 1

        # TODO: maybe keep track of references so if the order of entities changes so do their ids?

    def add_raw_entity(self, entity: dict):
        """
        """
        pass

    def give_entity_id(self, entity_number: int, id: str) -> None:
        """
        Adds an id to an already added Entity.
        """
        pass

    def remove_entity(self, entity_id: Union[str, int]) -> None:
        """
        Removes the entity with the id `entity_id`.
        """
        pass

    def add_power_connection(self, id1, id2):
        """
        Adds a copper wire power connection between two entities.
        """
        entity_1 = self.entities[id1]
        entity_2 = self.entities[id2]
        
        if not entity_1.power_connectable:
            raise EntityNotPowerConnectable(entity_1.name)
        if not entity_2.power_connectable:
            raise EntityNotPowerConnectable(entity_2.name)
        
        # TODO
        pass

    def add_wire_connection(self, color, id1, side1, id2, side2):
        """
        Adds a circuit wire connection between two entities.
        """
        # Ensure inputs are correct
        # if isinstance(id1, int):
        #     entity_1 = self.entities[id1]
        # elif isinstance(id1, str):
        #     try:
        #         id1 = self.entity_metadata[id1]
        #     except KeyError:
        #         raise
        #     entity_1 = self.entities[id1 - 1]
        # else:
        #     raise ValueError("id1 must be either a int or a str")
        entity_1 = self.entities[id1]

        # if isinstance(id2, int):
        #     entity_2 = self.entities[id2 - 1]
        # elif isinstance(id2, str):
        #     try:
        #         id2 = self.entity_metadata[id2]
        #     except KeyError:
        #         raise
        #     entity_2 = self.entities[id2 - 1]
        # else:
        #     raise ValueError("id2 must be either a int or a str")
        entity_2 = self.entities[id2]

        # Assert that both entities can be connected to
        #assert entity_1.circuit_connectable
        #assert entity_2.circuit_connectable
        if not entity_1.circuit_connectable:
            raise EntityNotCircuitConnectable(entity_1.name)
        if not entity_2.circuit_connectable:
            raise EntityNotCircuitConnectable(entity_1.name)

        # Assert that the entities are close enough to connect with wires
        # TODO

        # Handle entity 1
        entity_1.add_circuit_connection_point(color, side1, entity_2.name, id2, side2)

        # Handle entity 2
        entity_2.add_circuit_connection_point(color, side2, entity_1.name, id1, side1)

    def add_tile(self, tile_name: str, x: int, y: int, id: str = None) -> None:
        """
        Add a tile to the Blueprint.
        """
        if id is not None:
            if id not in self.tile_metadata:
                self.tile_metadata[id] = len(self.tiles)
            else: # Same ID!
                raise DuplicateIDException(
                    "{} already used in blueprint tiles".format(id)
                )
        
        self.tiles.append(Tile(tile_name, x, y))

    # def entity_with_id(self, id: str) -> Entity:
    #     """
    #     Gets a copy of an entity from the Blueprint.

    #     Raises:
    #         TypeError: if `entity` is neither an `int` or `str`.
    #     """
    #     # if isinstance(entity, int):
    #     #     return Entity(self.root["entities"][entity]) # this really has no use
    #     #     # if we wanted to do it this way we'd just do blueprint.entities[whatever]
    #     # elif isinstance(entity, str):
    #     #     entity_index = self.entity_metadata[entity]
    #     #     return Entity(self.root["entities"][entity_index])
    #     # else:
    #     #     raise TypeError("Incorrect type of entity; int or str required")
        
    #     entity_index = self.entity_metadata[id]
    #     return self.entities[entity_index]

    def entity_at_position(self, id: Union[int, str]) -> Entity:
        """
        """
        # TODO
        pass

    def tile_with_id(self, id: str) -> Tile:
        """
        """
        tile_index = self.tile_metadata[id]
        return self.tiles[tile_index]

    def tile_at_position(self, x, y) -> Tile:
        """
        """
        for tile in self.tiles:
            if tile.x == x and tile.y == y:
                return tile
        return None

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

        # vv Old vv
        # for i, entity in enumerate(self.entities):
        #     out_dict["entities"][i] = entity.to_dict()
        #     #out_dict["entities"][i]["entity_number"] = i + 1 # FIXME

        # Convert all entities into dicts
        out_dict['entities'] = list()
        for i in range(0, self._entities_length):
            entity_dict_copy = copy.deepcopy(self.entities[i + 1].to_dict())
            out_dict["entities"].append(entity_dict_copy)

        # Convert all tiles into dicts
        for i, tile in enumerate(self.tiles):
            out_dict["tiles"][i] = tile.to_dict()

        # Convert all schedules into dicts
        # TODO

        # Change all wire connections to use entity_number
        for entity in out_dict["entities"]:
            print(entity)
            if "connections" in entity:
                connections = entity["connections"]
                for side in connections:
                    #print(connections[side])
                    for color in connections[side]:
                        connection_points = connections[side][color]
                        for point in connection_points:
                            old = point["entity_id"]
                            if isinstance(old, str):
                                point["entity_id"] = self.entity_id_to_number[old]

        # Change all power connections to use entity_number

        # Delete empty entries to compress as much as possible
        if len(out_dict["entities"]) == 0:
            del out_dict["entities"]
        if len(out_dict["tiles"]) == 0:
            del out_dict["tiles"]
        if len(out_dict["schedules"]) == 0:
            del out_dict["schedules"]

        # Make sure the final dictionary is valid
        out_dict = BLUEPRINT_SCHEMA.validate(out_dict)
        
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
            self.blueprint["entities"] = dict()
        if "tiles" not in self.blueprint:
            self.blueprint["tiles"] = list()
        if "schedules" not in self.blueprint:
            self.blueprint["schedules"] = list()
        if "version" not in self.blueprint:
            maj, min, pat = __factorio_version_info__
            self.blueprint["version"] = utils.encode_version(maj, min, pat, 0)

        self.entities   = self.blueprint["entities"]
        self._entities_length = 0
        self.tiles      = self.blueprint["tiles"]
        self._tiles_length = 0
        self.schedules  = self.blueprint["schedules"]
        self._schedules_length = 0

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
    def __init__(self, blueprint_string:str = None):
        # Ensure that the blueprint loaded is actually the correct object type

        # add blueprints
        self.root = dict()
        self.root["blueprint_book"] = dict()

        self.blueprints = list()

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

    def to_string(self) -> str:
        """
        """
        # Get the root dicts from each blueprint and insert them into blueprints
        for blueprint in self.blueprints:
            print(blueprint)
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