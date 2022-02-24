# entity.py

# TODO: create verification for the initial load of an entity by making a schema for each entity class (?)
#   This would only be useful if the whole thing was loaded in the constructor anyway, otherwise we'd still need all
#   the other error checking code, making it somewhat redundant.
#   Maybe at the end, right before converting to dict? I've had this conversation with myself before...
# >>>> Nah, screw that shit, we use Schema itself to normalize and verify the data, because Im pretty sure I can do that for everything
# TODO: add `set_name` function in entity, so you can change an entity's type but keep its metadata
# TODO: value check everything + warnings
# TODO: add rail grid placing, add warnings/errors for rails that are placed an odd number of tiles apart
#   in fact, a rails and rail entities have a whole lot of extra rules that need to be accounted for
# TODO: make programmable speaker work with string names for things as well as integers
# TODO: get rid of _normalize functions, I dont like them
# TODO: documentation!
# TODO: "succinct" mode for to_dict(), integrate with better default setting/management

from draftsman.errors import (
    InvalidEntityID, InvalidItemID, InvalidSignalID, 
    InvalidArithmeticOperation, InvalidConditionOperation,
    InvalidMode, InvalidWireType, InvalidConnectionSide, 
    EntityNotCircuitConnectable, EntityNotPowerConnectable, InvalidRecipeID
)
from draftsman.signal import Signal, item_signals, signal_dict
from draftsman.signatures import (
    VEC_SCHEMA, IVEC_SCHEMA, INTEGER_SCHEMA, STRING_SCHEMA, POSITION_SCHEMA, 
    BAR_SCHEMA, CONNECTIONS_SCHEMA, CONNECTION_POINT_SCHEMA, DIRECTION_SCHEMA, 
    CONTROL_BEHAVIOR_SCHEMA, STACK_SIZE_SCHEMA
)

import abc
import copy
from enum import IntEnum
import math
from typing import Any, Union, Callable
import warnings

class Direction(IntEnum):
    NORTH = 0
    NORTHEAST = 1
    EAST = 2
    SOUTHEAST = 3
    SOUTH = 4
    SOUTHWEST = 5
    WEST = 6
    NORTHWEST = 7

class ReadMode(IntEnum):
    PULSE = 0
    HOLD = 1

class ModeOfOperation(IntEnum):
    ENABLE_DISABLE = 0
    SET_FILTERS = 1
    NONE = 3

# from entity_data import *

def warn_user(message):
    warnings.warn(message, stacklevel=3)

from draftsman.data.entities import entity_dimensions, circuit_wire_distances, power_wire_distances
from draftsman.data.recipes import *
import draftsman.data.instruments

entity_inventory_sizes = {
    "wooden-chest": 16,
    "iron-chest": 32,
    "steel-chest": 48,
    "logistic-chest-active-provider": 48,
    "logistic-chest-passive-provider": 48,
    "logistic-chest-storage": 48,
    "logistic-chest-buffer": 48,
    "logistic-chest-requester": 48,
}

entity_instruments = {
    "programmable-speaker": {
        "piano": ["blah"]
    }
}

containers = [
    "wooden-chest", "iron-chest", "steel-chest", 
    "logistic-chest-active-provider", "logistic-chest-passive-provider"
]

storage_tanks = [
    "storage-tank"
]

transport_belts = [
    "transport-belt", "fast-transport-belt", "express-transport-belt"
]

underground_belts = [
    "underground-belt", "fast-underground-belt", "express-underground-belt"
]

splitters = [
    "splitter", "fast-splitter", "express-splitter"
]

inserters = [
    "burner-inserter", "inserter", "long-handed-inserter", "fast-inserter",
    "stack-inserter"
]

filter_inserters = [
    "filter-inserter", "stack-filter-inserter"
]

loaders = [
    "loader", "fast-loader", "express-loader"
] # No vanilla loaders that arent hidden

electric_poles = [
    "small-electric-pole", "medium-electric-pole", "big-electric-pole", 
    "substation"
]

pipes = [
    "pipe"
]

underground_pipes = [
    "pipe-to-ground"
]

pumps = [
    "pump"
]

straight_rails = [
    "straight-rail"
]

curved_rails = [
    "curved-rail"
]

train_stops = [
    "train-stop"
]

rail_signals = [
    "rail-signal"
]

rail_chain_signals = [
    "rail-chain-signal"
]

locomotives = [
    "locomotive"
]

cargo_wagons = [
    "cargo-wagon"
]

fluid_wagons = [
    "fluid-wagon"
]

artillery_wagons = [
    "artillery-wagon"
]

logistic_storage_containers = [
    "logistic-chest-storage"
]

logistic_buffer_containers = [
    "logistic-chest-buffer"
]

logistic_request_containers = [
    "logistic-chest-requester"
]

roboports = [
    "roboport"
]

lamps = [
    "small-lamp"
]

arithmetic_combinators = [
    "arithmetic-combinator"
]

decider_combinators = [
    "decider-combinator"
]

constant_combinators = [
    "constant-combinator"
]

power_switches = [
    "power-switch"
]

programmable_speakers = [
    "programmable-speaker"
]

boilers = [
    "boiler", "heat-exchanger"
]

generators = [
    "steam-engine", "steam-turbine"
]

solar_panels = [
    "solar-panel"
]

accumulators = [
    "accumulator"
]

reactors = [
    "nuclear-reactor"
]

heat_pipes = [
    "heat-pipe"
]

mining_drills = [
    "burner-mining-drill", "electric-mining-drill", "pumpjack"
]

offshore_pumps = [
    "offshore-pump"
]

furnaces = [
    "stone-furnace", "steel-furnace", "electric-furnace"
]

assembling_machines = [
    "assembling-machine-1", "assembling-machine-2", "assembling-machine-3",
    "chemical-plant", "oil-refinery", "centrifuge"
]

labs = [
    "lab"
]

beacons = [
    "beacon"
]

rocket_silos = [
    "rocket-silo"
]

land_mines = [
    "land-mine"
]

walls = [
    "stone-wall"
]

gates = [
    "gate"
]

turrets = [
    "gun-turret", "laser-turret", "flamethrower-turret", "artillery-turret"
]

radars = [
    "radar"
]

electric_energy_interfaces = [
    "electric-energy-interface"
]

linked_containers = [
    "linked-chest"
]

heat_interfaces = [
    "heat-interface"
]

linked_belts = [
    "linked-belt"
]

infinity_containers = [
    "infinity-chest"
]

infinity_pipes = [
    "infinity-pipe"
]

burner_generators = [
    "burner-generator"
]


class EntityLike(metaclass=abc.ABCMeta):
    def __init__(self, name: str, position: Union[list, dict] = [0, 0], **kwargs):
        pass

    def set_name():
        pass

    def set_id():
        pass

    @abc.abstractmethod
    def to_dict():
        pass

# Mixins!
# TODO: organize
class Entity:
    def __init__(self, name: str, position: Union[list, dict] = [0, 0], **kwargs):
        # Create a set of keywords that transfer in to_dict function
        # Since some things we want to keep internal without sending to to_dict
        self.exports = dict()
        # Create a set of arguments that weren't used by Entity or its Mixins
        # Use this after the init is called to see if there were any kwargs that
        # were incorrect and issue warnings about them because I'm two test
        # cases in and I LITERALLY already messed up
        self.unused_args = kwargs

        # Name (External)
        self.name = name 
        self._add_export("name")

        # ID (Internal)
        self.id = None
        if "id" in kwargs:
            kwargs["id"] = STRING_SCHEMA.validate(kwargs["id"])
            self.set_id(kwargs["id"])
            self.unused_args.pop("id")

        # Width and Height (Internal)
        # TODO: change this to AABB
        self.width, self.height = entity_dimensions[name]

        # Power connectable? (Internal) (Overwritten if applicable)
        self.power_connectable = False
        # Dual power connectable? (Internal) (Overwritten if applicable)
        self.dual_power_connectable = False

        # Circuit connectable? (Interal) (Overwritten if applicable)
        self.circuit_connectable = False
        # Dual circuit connectable? (Internal) (Overwritten if applicable)
        self.dual_circuit_connectable = False

        # (Absolute) Position (External)
        # Grid Position (Internal)
        position = POSITION_SCHEMA.validate(position)
        if isinstance(position, list):
            Entity.set_grid_position(self, position[0], position[1])
        elif isinstance(position, dict): # pragma: no branch
            Entity.set_absolute_position(self, position["x"], position["y"])
        self._add_export("position")

        # Tags (External)
        self.tags = {}
        if "tags" in kwargs:
            self.set_tags(kwargs["tags"])
            self.unused_args.pop("tags")
        self._add_export("tags", lambda x: x)

    def set_id(self, id: str) -> None:
        """
        Sets the `id` of the entity. 

        Note: it is impossible to insert two entities into a blueprint with the
        same `id`.
        """
        self.id = STRING_SCHEMA.validate(id)

    def set_absolute_position(self, x: float, y: float) -> None:
        """
        Sets the position of the object, or the position that Factorio uses. On
        most entities, the position of the object is located at the center.
        """
        self.position = {"x": x, "y": y}
        self.position = VEC_SCHEMA.validate(self.position)
        grid_x = round(self.position["x"] - self.width / 2.0)
        grid_y = round(self.position["y"] - self.height / 2.0)
        self.grid_position = [grid_x, grid_y]

    def set_grid_position(self, x: int, y: int) -> None:
        """
        Sets the grid position of the object, or the tile coordinates of the
        object. Calculates the absolute position based off of the dimensions of
        the entity. If a tile is multiple tiles in width or height, the grid
        coordinate is the top left-most tile of the entity.
        """
        self.grid_position = [x, y]
        self.grid_position = IVEC_SCHEMA.validate(self.grid_position)
        absolute_x = self.grid_position[0] + self.width / 2.0
        absolute_y = self.grid_position[1] + self.height / 2.0
        self.position = {"x": absolute_x, "y": absolute_y}

    def set_tags(self, tags: dict) -> None:
        """
        """
        self.tags = tags

    def set_tag(self, tag: str, value: Any) -> None:
        """
        """
        if value is None:
            self.tags.pop(tag, None)
        else:
            self.tags[tag] = value

    def to_dict(self) -> dict:
        """
        Converts the Entity to its JSON dict representation. The keys returned
        are determined by the contents of the `exports` dictionary and their
        function values.
        """
        dict_self = dict(self)
        # Only add the keys in the exports dictionary
        out = {}
        for name, f in self.exports.items():
            value = dict_self[name]
            #print(name, value)
            # Does the value match the criteria to be included?
            if f is None or f(value):
                #print("criteria met")
                out[name] = value
            else:
                #print("criteria failed")
                pass

        return out

    def _add_export(self, name: str, f: Callable = None) -> None:
        """
        Adds an export key with a criteria function.

        We can't just convert the entire entity to a dict, because there are a
        number of keys (for technical or space reasons) that we dont want to
        add to the dictionary. Instead, we hold a dictionary of the keys we do
        want to add to the dictionary and add those if they're present in the
        Entity object.

        However, some items that are present in Entity might be initialized to
        `None` or otherwise redundant values, which would just take up space in 
        the output dict. Hence, we can also provide a criteria function that 
        takes a single argument, the value of the element in the `Entity`. If 
        the function is not present, or if the function is present and returns 
        `True`, then the key and its value are added to the output dict.
        """
        self.exports[name] = f

    def __iter__(self):
        """
        Used when converting Entity to dict.
        """
        for attr, value in self.__dict__.items():
            yield attr, value

    # def __copy__(self): # TODO?
    #     pass

    # def __deepcopy__(self, memo): # TODO?
    #     pass

    def __repr__(self):
        return "<Entity>" + str(self.to_dict())


class DirectionalMixin:
    """ 
    Enables entities to be rotated. 
    """
    def __init__(self, name: str, position: Union[list, dict] = [0, 0], **kwargs):
        super().__init__(name, **kwargs)

        # Rotated width and height
        self.rotated_width = self.width
        self.rotated_height = self.height

        self.direction = 0
        if "direction" in kwargs:
            self.set_direction(kwargs["direction"])
            self.unused_args.pop("direction")
        self._add_export("direction", lambda x: x != 0)

        # Now that we know the entity is rotatable, try calling the set_position
        # equivalents again to now handle the rotation
        position = POSITION_SCHEMA.validate(position) # FIXME: technically redundant
        if isinstance(position, list):
            self.set_grid_position(position[0], position[1])
        elif isinstance(position, dict): # pragma: no branch
            self.set_absolute_position(position["x"], position["y"])


    def set_absolute_position(self, x: float, y: float) -> None:
        """
        Sets the position of the object, or the position that Factorio uses. On
        most entities, the position of the object is located at the center.
        """
        self.position = {"x": x, "y": y}
        self.position = VEC_SCHEMA.validate(self.position)
        grid_x = round(self.position["x"] - self.rotated_width / 2.0)
        grid_y = round(self.position["y"] - self.rotated_height / 2.0)
        self.grid_position = [grid_x, grid_y]

    def set_grid_position(self, x: int, y: int) -> None:
        """
        Sets the grid position of the object, or the tile coordinates of the
        object. Calculates the absolute position based off of the dimensions of
        the entity. If a tile is multiple tiles in width or height, the grid
        coordinate is the top left-most tile of the entity.
        """
        self.grid_position = [x, y]
        self.grid_position = IVEC_SCHEMA.validate(self.grid_position)
        absolute_x = self.grid_position[0] + self.rotated_width / 2.0
        absolute_y = self.grid_position[1] + self.rotated_height / 2.0
        self.position = {"x": absolute_x, "y": absolute_y}

    def set_direction(self, direction: int) -> None:
        """
        """
        self.direction = DIRECTION_SCHEMA.validate(direction)
        if self.direction not in {0, 2, 4, 6}:
            warn_user("this entity only has 4-way rotation")
        if self.direction == Direction.EAST or self.direction == Direction.WEST:
            self.rotated_width = self.height
            self.rotated_height = self.width
        else:
            self.rotated_width = self.width
            self.rotated_height = self.height


class EightWayDirectionalMixin:
    """
    Enables entities to be rotated across 8 directions
    """
    def __init__(self, name: str, **kwargs):
        super().__init__(name, **kwargs)

        self.direction = 0
        if "direction" in kwargs:
            self.set_direction(kwargs["direction"])
        self._add_export("direction", lambda x: x != 0)

    def set_direction(self, direction: int) -> None:
        """
        """
        # TODO: add error checking
        self.direction = direction


class OrientationMixin:
    """ 
    Used in trains and wagons to specify their direction. 
    """
    def __init__(self, name: str, **kwargs):
        super().__init__(name, **kwargs)

        self.orientation = 0.0
        if "orientation" in kwargs:
            self.set_orientation(kwargs["orientation"])
        self._add_export("orientation", lambda x: x != 0)

    def set_orientation(self, orientation: float) -> None:
        """
        Sets the orientation of the train car. (0.0 -> 1.0)
        """
        # TODO: error checking
        self.orientation = orientation


class InventoryMixin:
    """
    Enables the entity to have inventory control.
    """
    def __init__(self, name: str, **kwargs):
        super().__init__(name, **kwargs)

        self.inventory_size = entity_inventory_sizes[self.name]

        self.bar = None
        if "bar" in kwargs:
            self.set_bar_index(kwargs["bar"])
            self.unused_args.pop("bar")
        self._add_export("bar", lambda x: x is not None)

    def set_bar_index(self, index: int) -> None:
        """
        Sets the inventory limiting bar.
        """
        self.bar = BAR_SCHEMA.validate(index)
        if self.bar >= self.inventory_size or self.bar < 0:
            warn_user("Bar index not in range [0, {})"
                      .format(self.inventory_size))


class InventoryFilterMixin:
    """
    Allows inventories to set content filters. Used in cargo wagons.
    """
    def __init__(self, name: str, **kwargs):
        super().__init__(name, **kwargs)

        self.inventory = {}
        if "inventory" in kwargs:
            self.set_inventory(kwargs["inventory"])
        self._add_export("inventory", lambda x: len(x) != 0)

    def set_inventory(self, inventory: dict) -> None:
        """
        Sets the entire inventory configuration for the cargo wagon.
        """
        # Validate filter schema
        # TODO
        self.inventory = inventory

    def set_inventory_filter(self, index: int, name: str) -> None:
        """
        Sets the item filter at location `index` to `name`. If `name` is set to
        `None` the item filter at that location is removed.

        `index`: [0-39] (0-indexed) 
        """
        if "filters" not in self.inventory:
            self.inventory["filters"] = []

        # TODO: error checking
        
        # Check to see if filters already contains an entry with the same index
        for i, filter in enumerate(self.inventory["filters"]):
            if index == filter["index"]: # Index already exists in the list
                if name is None: # Delete the entry
                    del self.inventory["filters"][i]
                else: # Set the new value
                    self.inventory["filters"][i] = {"index": index+1,"name": name}
                    
                return

        # If no entry with the same index was found
        self.inventory["filters"].append({"index": index+1, "name": name})

    def set_bar_index(self, index: int) -> None:
        """
        Sets the bar of the train's inventory. Setting it to `None` removes the
        parameter from the configuration.
        """
        if index is None:
            self.inventory.pop("bar", None)
        else:
            # TODO: add error checking
            self.inventory["bar"] = index


class IOTypeMixin:
    """
    Gives an entity a Input/Output type. Used on underground belts and loaders.
    """
    def __init__(self, name: str, **kwargs):
        super().__init__(name, **kwargs)
        
        self.type = "input" # Default
        if "type" in kwargs:
            self.set_io_type(kwargs["type"])
            self.unused_args.pop("type")
        self._add_export("type", lambda x: x is not None and x != "input")

    def set_io_type(self, type: str):
        """
        Sets whether or not this entity is configured as 'input' or 'output'.
        """
        if type in {"input", "output", None}:
            self.type = type
        else:
            raise ValueError("`type` must be one of 'input', 'output' or 'None'")


class PowerConnectableMixin:
    def __init__(self, name: str, **kwargs):
        super().__init__(name, **kwargs)
        self.power_connectable = True

        self.power_wire_max_distance = power_wire_distances[name]

        self.neighbours = []
        if "neighbours" in kwargs:
            self.neighbours = kwargs["neighbours"]
        self._add_export("neighbours", lambda x: len(x) != 0)

    def _add_power_connection(self, target_entity: Entity, target_id: Union[int, str], source_side: int = 1) -> None:
        """
        Adds a power wire between this entity and another power-connectable one.
        """
        # TODO: raise error if target_id is not power connectable?

        # Issue a warning if the entities being connected are too far apart
        # min_dist = min(self.circuit_wire_max_distance,
        #                target.circuit_wire_max_distance)
        # self_pos = [self.position["x"], self.position["y"]]
        # target_pos = [target.position["x"], target.position["y"]]
        # real_dist = math.dist(self_pos, target_pos)
        # if real_dist > min_dist:
        #     warn_user("Distance between entities ({}) is greater than max ({})"
        #               .format(real_dist, min_dist))

        if target_entity.dual_power_connectable:
            # If the target entity is a power switch, then its not considered a
            # neighbour
            return
        else:
            # Otherwise add it as normal
            if target_id not in self.neighbours:
                self.neighbours.append(target_id)

    def _remove_power_connection_point(self, target_id: Union[int, str]) -> None:
        pass # TODO


class CircuitConnectableMixin:
    """
    Enables the entity to be connected to circuit networks.
    """
    def __init__(self, name: str, **kwargs):
        super().__init__(name, **kwargs)
        self.circuit_connectable = True

        self.circuit_wire_max_distance = circuit_wire_distances[name]

        self.connections = {}
        if "connections" in kwargs:
            self.set_connections(kwargs["connections"])
            self.unused_args.pop("connections")
        self._add_export("connections", lambda x: len(x) != 0)

    def set_connections(self, connections: dict) -> None:
        """
        """
        if connections is None:
            self.connections = {}
        else:
            self.connections = CONNECTIONS_SCHEMA.validate(connections)

    def add_circuit_connection(self, color: str, target: Entity, source_side: int = 1, target_side: int = 1) -> None:
        """
        Adds a connection between this entity and `other_entity`

        NOTE: this function only modifies the current entity; for completeness
        you should also connect the other entity to this one.
        """
        if color not in {"red", "green"}:
            raise InvalidWireType(color)
        if not isinstance(target, Entity):
            raise TypeError("'target' is not an Entity")
        if self.id is None or target.id is None:
            raise ValueError("both entities must have a valid id to connect")
        if source_side not in {1, 2}:
            raise InvalidConnectionSide(source_side)
        if target_side not in {1, 2}:
            raise InvalidConnectionSide(target_side)

        if not target.circuit_connectable:
            raise EntityNotCircuitConnectable(target.name)

        if source_side == 2 and not self.dual_circuit_connectable:
            warn_user("'source_side' was specified as 2, but entity '{}' is not"
                      " dual circuit connectable".format(type(self)))
        if target_side == 2 and not target.dual_circuit_connectable:
            warn_user("'target_side' was specified as 2, but entity '{}' is not"
                      " dual circuit connectable".format(type(target)))

        # Issue a warning if the entities being connected are too far apart
        min_dist = min(self.circuit_wire_max_distance,
                       target.circuit_wire_max_distance)
        self_pos = [self.position["x"], self.position["y"]]
        target_pos = [target.position["x"], target.position["y"]]
        real_dist = math.dist(self_pos, target_pos)
        if real_dist > min_dist:
            warn_user("Distance between entities ({}) is greater than max ({})"
                      .format(real_dist, min_dist))

        # Add target to self.connections
        
        if str(source_side) not in self.connections:
            self.connections[str(source_side)] = dict()
        current_side = self.connections[str(source_side)]

        if color not in current_side:
            current_side[color] = list()
        current_color = current_side[color]
        
        # If dual circuit connectable specify the target side
        if target.dual_circuit_connectable:
            entry = {"entity_id": target.id, "circuit_id": target_side}
        else:
            # However, for most entities you dont need a target_side
            entry = {"entity_id": target.id}

        if entry not in current_color:
            current_color.append(entry)

        # Add self to target.connections

        if str(target_side) not in target.connections:
            target.connections[str(target_side)] = dict()
        current_side = target.connections[str(target_side)]
        
        if color not in current_side:
            current_side[color] = list()
        current_color = current_side[color]

        # If dual circuit connectable specify the target side
        if self.dual_circuit_connectable:
            entry = {"entity_id": self.id, "circuit_id": source_side}
        else:
            # However, for most entities you dont need a target_side
            entry = {"entity_id": self.id}

        if entry not in current_color:
            current_color.append(entry)

    def remove_circuit_connection(self, color: str, target: Entity, source_side: int = 1, target_side: int = 1) -> None:
        """
        Removes a connection point between this entity and `target`.
        """

        if color not in {"red", "green"}:
            raise InvalidWireType(color)
        if not isinstance(target, Entity):
            raise TypeError("'target' is not an Entity")
        if self.id is None or target.id is None:
            raise ValueError("both entities must have a valid id to connect")
        if source_side not in {1, 2}:
            raise InvalidConnectionSide(source_side)
        if target_side not in {1, 2}:
            raise InvalidConnectionSide(target_side)

        # Remove from source
        if target.dual_circuit_connectable:
            entry = {"entity_id": target.id, "circuit_id": target_side}
        else:
            # However, for most entities you dont need a target_side
            entry = {"entity_id": target.id}

        try:
            current_side = self.connections[str(source_side)]
            current_color = current_side[color]
            current_color.remove(entry)
            # Remove redundant structures from source if applicable
            if len(current_color) == 0:
                del self.connections[str(source_side)][color]
            if len(current_side) == 0:
                del self.connections[str(source_side)]
        except (KeyError, ValueError):
            pass

        # Remove from target
        if self.dual_circuit_connectable:
            entry = {"entity_id": self.id, "circuit_id": source_side}
        else:
            # However, for most entities you dont need a target_side
            entry = {"entity_id": self.id}

        try:
            current_side = target.connections[str(target_side)]
            current_color = current_side[color]
            current_color.remove(entry)
            # Remove redundant structures from target if applicable
            if len(current_color) == 0:
                del target.connections[str(target_side)][color]
            if len(current_side) == 0:
                del target.connections[str(target_side)]
        except (KeyError, ValueError):
            pass
        

class ControlBehaviorMixin:
    """
    Enables the entity to specify control behavior.
    """
    def __init__(self, name: str, **kwargs):
        super().__init__(name, **kwargs)

        self.control_behavior = {}
        if "control_behavior" in kwargs:
            self.set_control_behavior(kwargs["control_behavior"])
            self.unused_args.pop("control_behavior")

        self._add_export("control_behavior", lambda x: len(x) != 0)

    def set_control_behavior(self, behavior: dict):
        """
        """
        self.control_behavior = CONTROL_BEHAVIOR_SCHEMA.validate(behavior)

    def _set_condition(self, condition_name: str, a: str, op: str, b: Union[str, int]):
        self.control_behavior[condition_name] = {}
        condition = self.control_behavior[condition_name]
        # Check the inputs
        # A
        if a is None:
            pass # Keep the first signal empty
        elif isinstance(a, str):
            condition["first_signal"] = signal_dict(a)
        elif isinstance(a, int):
            raise TypeError("normal conditions cannot have a constant first")
        else:
            raise TypeError("`a` is neither 'str' nor 'None'")
        
        # TODO: handle the case where the user inputs '≥'
        # Consider the case where someone is pulling the comparator from a 
        # blueprint string that already exists; it would be way easier to simply
        # insert it into the function without having to convert it back and 
        # forth

        # op
        valid_comparisons =  [">", "<", "=", ">=", "<=", "!="]
        if op not in valid_comparisons:
            raise InvalidConditionOperation(op)
        actual_comparisons = [">", "<", "=", "≥",  "≤",  "≠"]
        index = valid_comparisons.index(op)
        condition["comparator"] = actual_comparisons[index]

        # B
        if isinstance(b, str):
            condition["second_signal"] = signal_dict(b)
        elif isinstance(b, int):
            condition["constant"] = b
        else:
            raise TypeError("`b` is neither 'str' or 'int'")


class CircuitConditionMixin: # (ControlBehaviorMixin)
    """
    Allows the Entity to have an circuit enable condition. Used in Pumps, 
    Inserters, Belts, etc.
    """
    def __init__(self, name: str, **kwargs):
        super().__init__(name, **kwargs)

        if "control_behavior" in kwargs:
            # Normalize circuit condition keys if necessary
            self._normalize_circuit_condition()

    def set_enable_disable(self, value: bool) -> None:
        """
        """
        if value is None:
            self.control_behavior.pop("circuit_enable_disable", None)
        elif isinstance(value, bool):
            self.control_behavior["circuit_enable_disable"] = value
        else:
            raise TypeError("`value` must be either 'bool' or 'None'")

    def set_enabled_condition(self, a: str = None, op: str = "<", b: Union[str, int] = 0):
        """
        """
        self._set_condition("circuit_condition", a, op, b)

    def remove_enabled_condition(self):
        """
        """
        self.control_behavior.pop("circuit_condition", None)

    def _normalize_circuit_condition(self) -> None:
        """
        """
        if "circuit_condition" in self.control_behavior:
            circuit_condition = self.control_behavior["circuit_condition"]
            if "first_signal" in circuit_condition:
                # If its a string, change it, otherwise treat it as gospel
                if isinstance(circuit_condition["first_signal"], str):
                    name = circuit_condition["first_signal"]
                    # circuit_condition["first_signal"] = {
                    #     "name": name,
                    #     "type": get_signal_type(name)
                    # }
                    circuit_condition["first_signal"] = signal_dict(name)
            if "comparator" in circuit_condition:
                # Convert user to internal representation
                op = circuit_condition["comparator"]
                valid_comparisons =  [">", "<", "=", ">=", "<=", "!="]
                actual_comparisons = [">", "<", "=", "≥",  "≤",  "≠"]
                index = valid_comparisons.index(op)
                op = actual_comparisons[index]
                circuit_condition["comparator"] = op
            if "second_signal" in circuit_condition:
                # If its a string, change it, otherwise treat it as gospel
                if isinstance(circuit_condition["second_signal"], str):
                    name = circuit_condition["second_signal"]
                    # circuit_condition["second_signal"] = {
                    #     "name": name,
                    #     "type": get_signal_type(name)
                    # }
                    circuit_condition["second_signal"] = signal_dict(name)


class LogisticConditionMixin: # (ControlBehaviorMixin)
    def __init__(self, name: str, **kwargs):
        super().__init__(name, **kwargs)

        if "control_behavior" in kwargs:
            # Normalize logistic conditions if necessary
            self._normalize_logistic_condition()

    def set_connect_to_logistic_network(self, value: bool) -> None:
        """
        """
        if value is None:
            self.control_behavior.pop("connect_to_logistic_network", None)
        elif isinstance(value, bool):
            self.control_behavior["connect_to_logistic_network"] = value
        else:
            raise TypeError("`value` must be either 'bool' or 'None'")

    def set_logistic_condition(self, a: str = None, op: str = "<", b: Union[str, int] = 0):
        """
        """
        self._set_condition("logistic_condition", a, op, b)

    def remove_logistic_condition(self):
        """
        TODO: remove
        """
        self.control_behavior.pop("logistic_condition", None)

    def _normalize_logistic_condition(self):
        """
        """
        if "logistic_condition" in self.control_behavior:
            logistic_condition = self.control_behavior["logistic_condition"]
            if "first_signal" in logistic_condition:
                # If its a string, change it, otherwise treat it as gospel
                if isinstance(logistic_condition["first_signal"], str):
                    name = logistic_condition["first_signal"]
                    logistic_condition["first_signal"] = signal_dict(name)
            if "comparator" in logistic_condition:
                # Convert user to internal representation
                op = logistic_condition["comparator"]
                valid_comparisons =  [">", "<", "=", ">=", "<=", "!="]
                actual_comparisons = [">", "<", "=", "≥",  "≤",  "≠"]
                index = valid_comparisons.index(op)
                op = actual_comparisons[index]
                logistic_condition["comparator"] = op
            if "second_signal" in logistic_condition:
                # If its a string, change it, otherwise treat it as gospel
                if isinstance(logistic_condition["second_signal"], str):
                    name = logistic_condition["second_signal"]
                    logistic_condition["second_signal"] = signal_dict(name)


class CircuitReadContentsMixin: # (ControlBehaviorMixin)
    def __init__(self, name: str, **kwargs):
        super().__init__(name, **kwargs)

    def set_read_contents(self, value: bool) -> None:
        """
        """
        if value is None:
            self.control_behavior.pop("circuit_read_hand_contents", None)
        elif isinstance(value, bool):
            self.control_behavior["circuit_read_hand_contents"] = value
        else:
            raise TypeError("`value` must be either 'bool' or 'None'")

    def set_read_mode(self, mode: ReadMode) -> None:
        """
        """
        if mode is None:
            self.control_behavior.pop("circuit_contents_read_mode", None)
        elif isinstance(mode, int):
            self.control_behavior["circuit_contents_read_mode"] = mode
        else:
            raise TypeError("`mode` must be either 'int' or 'None'")


class CircuitReadHandMixin: # (ControlBehaviorMixin)
    def __init__(self, name: str, **kwargs):
        super().__init__(name, **kwargs)

    def set_read_hand_contents(self, value: bool) -> None:
        """
        """
        if value is None:
            self.control_behavior.pop("circuit_read_hand_contents", None)
        elif isinstance(value, bool):
            self.control_behavior["circuit_read_hand_contents"] = value
        else:
            raise TypeError("`value` must be either 'bool' or 'None'")

    def set_read_mode(self, mode: ReadMode) -> None:
        """
        """
        if mode is None:
            self.control_behavior.pop("circuit_hand_read_mode", None)
        elif isinstance(mode, int):
            self.control_behavior["circuit_hand_read_mode"] = mode
        else:
            raise TypeError("`mode` must be either 'int' or 'None'")


class CircuitReadResourceMixin: # (ControlBehaviorMixin)
    def __init__(self, name: str, **kwargs):
        super().__init__(name, **kwargs)

    def set_read_resources(self, value: bool) -> None:
        """
        """
        self.control_behavior["circuit_read_resources"] = value

    def set_read_mode(self, mode: ReadMode):
        """
        """
        self.control_behavior["circuit_resource_read_mode"] = mode


class StackSizeMixin: # (ControlBehaviorMixin)
    """
    """
    def __init__(self, name: str, **kwargs):
        super().__init__(name, **kwargs)

        self.override_stack_size = None
        if "override_stack_size" in kwargs:
            self.set_stack_size_override(kwargs["override_stack_size"])
            self.unused_args.pop("override_stack_size")
        self._add_export("override_stack_size", lambda x: x is not None)

        self._normalize_stack_signal()

    def set_stack_size_override(self, stack_size: int):
        """
        Sets an inserter's stack size override.
        """
        self.override_stack_size = STACK_SIZE_SCHEMA.validate(stack_size)

    def set_circuit_stack_size_enabled(self, enabled: bool):
        """
        Set if the inserter's stack size is controlled by circuit signal.
        """
        if enabled is None:
            self.control_behavior.pop("circuit_set_stack_size", None)
        elif isinstance(enabled, bool):
            self.control_behavior["circuit_set_stack_size"] = enabled
        else:
            raise TypeError("`enabled` is neither 'bool' nor 'None'")

    def set_stack_control_signal(self, signal: str):
        """
        Specify the stack size input signal for the inserter if enabled.
        """
        # TODO: error checking
        if signal is None:
            self.control_behavior.pop("stack_control_input_signal")
        elif isinstance(signal, str):
            self.control_behavior["stack_control_input_signal"] = signal_dict(signal)
        else:
            raise TypeError("`signal` is neither 'str' nor 'None'")

    def _normalize_stack_signal(self) -> None:
        """
        """
        if "stack_control_input_signal" in self.control_behavior:
            name = self.control_behavior["stack_control_input_signal"]
            if isinstance(name, str):
                self.control_behavior["stack_control_input_signal"] = signal_dict(name)


class ModeOfOperationMixin: # (ControlBehaviorMixin)
    """
    """
    def __init__(self, name: str, **kwargs):
        super().__init__(name, **kwargs)

    def set_mode_of_operation(self, mode: ModeOfOperation):
        """
        """
        if mode is None or mode == ModeOfOperation.ENABLE_DISABLE:
            self.control_behavior.pop("circuit_mode_of_operation", None)
        elif isinstance(mode, int):
            self.control_behavior["circuit_mode_of_operation"] = mode
        else:
            raise TypeError("`mode` should either be 'int' or 'None'")


class ReadRailSignalMixin: # (ControlBehaviorMixin)
    """
    """
    def __init__(self, name: str, **kwargs):
        super().__init__(name, **kwargs)

    def set_red_output_signal(self, signal: str) -> None:
        """
        """
        if signal is None:
            self.control_behavior.pop("red_output_signal", None)
        # TODO: error_checking
        self.control_behavior["red_output_signal"] = signal_dict(signal)

    def set_yellow_output_signal(self, signal: str) -> None:
        """
        """
        if signal is None:
            self.control_behavior.pop("yellow_output_signal", None)
        # TODO: error_checking
        self.control_behavior["yellow_output_signal"] = signal_dict(signal)

    def set_green_output_signal(self, signal: str) -> None:
        """
        """
        if signal is None:
            self.control_behavior.pop("green_output_signal", None)
        # TODO: error_checking
        self.control_behavior["green_output_signal"] = signal_dict(signal)


class FiltersMixin:
    def __init__(self, name: str, **kwargs):
        super().__init__(name, **kwargs)

        self.filters = None
        if "filters" in kwargs:
            self.set_item_filters(kwargs["filters"])
            self.unused_args.pop("filters")
        self._add_export("filters", lambda x: x is not None)

    def set_item_filter(self, index: int, item: str) -> None:
        """
        """
        if self.filters is None:
            self.filters = []

        # TODO: check if index is ouside the range of the max filter slots
        # (which needs to be extracted)

        if item is not None and item not in item_signals:
            raise InvalidItemID(item)

        for i in range(len(self.filters)):
            filter = self.filters[i]
            if filter["index"] == index + 1:
                if item is None:
                    del self.filters[i]
                else:
                    filter["name"] = item
                return
        
        # Otherwise its unique; add to list
        self.filters.append({"index": index + 1, "name": item})

    def set_item_filters(self, filters: list) -> None:
        """
        Sets the item filters for the inserter or loader.
        """
        if filters is None:
            self.filters = None
            return

        # Make sure the items are item signals
        for item in filters:
            if isinstance(item, dict):
                item = item["name"]
            if item not in item_signals:
                raise InvalidItemID(item)

        for i in range(len(filters)):
            if isinstance(filters[i], str):
                self.set_item_filter(i, filters[i])
            else: # dict
                self.set_item_filter(i, filters[i]["name"])


class RecipeMixin: # TODO: finish
    def __init__(self, name: str, **kwargs):
        super().__init__(name, **kwargs)

        # List of all recipies that this machine can make
        self.recipes = recipes[name]

        # Recipe that this machine is currently set to
        self.recipe = None
        if "recipe" in kwargs:
            self.set_recipe(kwargs["recipe"])
        self._add_export("recipe", lambda x: x is not None)

    def set_recipe(self, recipe: str):
        """
        """
        if recipe not in self.recipes:
            raise InvalidRecipeID(recipe)
        self.recipe = recipe


class RequestFiltersMixin:
    """
    Used to allow Logistics Containers to request items from the Logisitics
    network.
    """
    def __init__(self, name: str, **kwargs):
        super().__init__(name, **kwargs)

        self.request_filters = None
        if "request_filters" in kwargs:
            self.set_request_filters(kwargs["request_filters"])
        self._add_export("request_filters", lambda x: x is not None)

    def set_request_filter(self, index: int, name: str, count: int = 0) -> None:
        """
        """
        if self.request_filters is None:
            self.request_filters = []
        
        # TODO: error checking

        # Check to see if filters already contains an entry with the same index
        for i, filter in enumerate(self.request_filters):
            if index == filter["index"]: # Index already exists in the list
                if name is None: # Delete the entry
                    del self.inventory["filters"][i]
                else: # Set the new value
                    self.inventory["filters"][i] = {
                        "index": index+1, "name": name, "count": count
                    }
                    
                return

        # If no entry with the same index was found
        self.request_filters.append({
            "index": index+1, "name": name, "count": count
        })

    def set_request_filters(self, filters: list) -> None:
        """
        """
        # Make sure the items are item signals
        if filters is not None:
            for item in filters:
                if item[0] not in item_signals:
                    raise InvalidItemID(item[0])

        for i in range(len(filters)):
            filters[i] = {"index": i + 1, "name": filters[i][0], "count": filters[i][1]}
        self.request_filters = filters


class RequestItemsMixin: # TODO: finish
    """
    NOTE: this is for module requests and stuff like that, not logistics!

    Think an assembling machine that needs speed modules inside of it
    """
    def __init__(self, name: str, **kwargs):
        super().__init__(name, **kwargs)

        self.items = {}
        if "items" in kwargs:
            self.set_item_requests(kwargs["items"])
        #self.exports.add("items")
        self._add_export("items", lambda x: len(x) != 0)

    def set_item_requests(self, items: dict) -> None:
        # TODO: finish
        for name, amount in items.items():
            self.set_item_request(name, amount)

    def set_item_request(self, item, amount):
        # TODO: finish
        if item not in item_signals:
            raise InvalidSignalID(item)
        self.items[item] = amount

    def remove_item_request(self, item):
        # TODO: finish
        del self.items[item]


class InfinitySettingsMixin:
    def __init__(self, name: str, **kwargs):
        super().__init__(name, **kwargs)

        self.infinity_settings = {}
        if "infinity_settings" in kwargs:
            self.set_infinity_settings(kwargs["infinity_settings"])
        self._add_export("infinity_settings", lambda x: len(x) != 0)

    def set_infinity_settings(self, settings: dict) -> None:
        """
        """
        # TODO: error checking
        if settings is None:
            self.infinity_settings = {}
        else:
            self.infinity_settings = settings


class ColorMixin:
    def __init__(self, name: str, **kwargs):
        super().__init__(name, **kwargs)

        self.color = None
        if "color" in kwargs:
            # color = COLOR_SCHEMA.validate(kwargs["color"])
            color = kwargs["color"]
            if isinstance(color, dict):
                self.set_color(**color)
            elif isinstance(color, list):
                self.set_color(*color)
            else:
                raise ValueError("color")
        self._add_export("color", lambda x: x is not None)

    def set_color(self, r: float, g: float, b: float, a: float = 1.0) -> None:
        """
        """
        self.color = {"r": r, "g": g, "b": b, "a": a}

    def remove_color(self) -> None:
        """
        """
        self.color = None


################################################################################


class Container(CircuitConnectableMixin, InventoryMixin, Entity):
    """
    * `wooden-chest`
    * `iron-chest`
    * `steel-chest`
    * `logistic-chest-active-provider`
    * `logistic-chest-passive-provider`
    """
    def __init__(self, name: str = containers[0], **kwargs):
        if name not in containers:
            raise InvalidEntityID("'{}' is not a valid name for this type".format(name))
        super(Container, self).__init__(name, **kwargs)

        for unused_arg in self.unused_args:
            warn_user("{} has no attribute '{}'".format(type(self), unused_arg))


class StorageTank(CircuitConnectableMixin, DirectionalMixin, Entity):
    """
    """
    def __init__(self, name: str = storage_tanks[0], **kwargs):
        if name not in storage_tanks:
            raise InvalidEntityID("'{}' is not a valid name for this type".format(name))
        super(StorageTank, self).__init__(name, **kwargs)
        
        for unused_arg in self.unused_args:
            warn_user("{} has no attribute '{}'".format(type(self), unused_arg))


class TransportBelt(CircuitReadContentsMixin, LogisticConditionMixin, 
                    CircuitConditionMixin, ControlBehaviorMixin, 
                    CircuitConnectableMixin, DirectionalMixin, Entity):
    """
    """
    def __init__(self, name: str = transport_belts[0], **kwargs):
        if name not in transport_belts:
            raise InvalidEntityID("'{}' is not a valid name for this type".format(name))
        super(TransportBelt, self).__init__(name, **kwargs)

        for unused_arg in self.unused_args:
            warn_user("{} has no attribute '{}'".format(type(self), unused_arg))


class UndergroundBelt(IOTypeMixin, DirectionalMixin, Entity):
    """
    """
    def __init__(self, name: str = underground_belts[0], **kwargs):
        if name not in underground_belts:
            raise InvalidEntityID("'{}' is not a valid name for this type".format(name))
        super(UndergroundBelt, self).__init__(name, **kwargs)

        for unused_arg in self.unused_args:
            warn_user("{} has no attribute '{}'".format(type(self), unused_arg))


class Splitter(DirectionalMixin, Entity):
    """
    """
    def __init__(self, name: str = splitters[0], **kwargs):
        if name not in splitters:
            raise InvalidEntityID("'{}' is not a valid name for this type".format(name))
        super(Splitter, self).__init__(name, **kwargs)

        self.input_priority = None
        if "input_priority" in kwargs:
            self.set_input_priority(kwargs["input_priority"])
            self.unused_args.pop("input_priority")
        self._add_export("input_priority", lambda x: x is not None)

        self.output_priority = None
        if "output_priority" in kwargs:
            self.set_output_priority(kwargs["output_priority"])
            self.unused_args.pop("output_priority")
        self._add_export("output_priority", lambda x: x is not None)

        self.filter = None
        if "filter" in kwargs:
            self.set_filter(kwargs["filter"])
            self.unused_args.pop("filter")
        self._add_export("filter", lambda x: x is not None)

        for unused_arg in self.unused_args:
            warn_user("{} has no attribute '{}'".format(type(self), unused_arg))

    def set_filter(self, item: str) -> None:
        """
        Sets the Splitter's filter to `item`. Default output side is left.
        """
        # TODO: uncomment
        if item in item_signals or item is None:
            self.filter = item
        else:
            raise ValueError("'{}' is not a valid item name".format(item))

    def set_input_priority(self, side: str) -> None:
        """
        Sets the Splitter's input priority to either 'left' or 'right'.
        """
        if side in {"left", "right", None}:
            self.input_priority = side
        else:
            raise ValueError("'{}' is not a valid input side".format(side))

    def set_output_priority(self, side: str) -> None:
        """
        Sets the Splitter's output priority to either 'left' or 'right'.
        """
        if side in {"left", "right", None}:
            self.output_priority = side
        else:
            raise ValueError("'{}' is not a valid input side".format(side))


class Inserter(StackSizeMixin, CircuitReadHandMixin, ModeOfOperationMixin, 
               CircuitConditionMixin, LogisticConditionMixin, 
               ControlBehaviorMixin, CircuitConnectableMixin, DirectionalMixin, 
               Entity):
    """
    """
    def __init__(self, name: str = inserters[0], **kwargs):
        if name not in inserters:
            raise InvalidEntityID("'{}' is not a valid name for this type".format(name))
        super(Inserter, self).__init__(name, **kwargs)

        for unused_arg in self.unused_args:
            warn_user("{} has no attribute '{}'".format(type(self), unused_arg))


class FilterInserter(FiltersMixin, StackSizeMixin, CircuitReadHandMixin, 
                     ModeOfOperationMixin, CircuitConditionMixin, 
                     LogisticConditionMixin, ControlBehaviorMixin, 
                     CircuitConnectableMixin, DirectionalMixin, Entity):
    """
    """
    def __init__(self, name: str = filter_inserters[0], **kwargs):
        if name not in filter_inserters:
            raise InvalidEntityID("'{}' is not a valid name for this type".format(name))
        super(FilterInserter, self).__init__(name, **kwargs)

        self.filter_mode = None
        if "filter_mode" in kwargs:
            self.set_filter_mode(kwargs["filter_mode"])
        self._add_export("filter_mode", lambda x: x is not None)

        for unused_arg in self.unused_args:
            warn_user("{} has no attribute '{}'".format(type(self), unused_arg))

    def set_filter_mode(self, mode: str) -> None:
        """
        Sets the filter mode. Can be either 'whitelist' or 'blacklist'.
        """
        if mode in {"whitelist", "blacklist", None}:
            self.filter_mode = mode
        else:
            raise ValueError("'{}' is not a valid filter mode".format(mode))


class Loader(FiltersMixin, IOTypeMixin, DirectionalMixin, Entity):
    """
    """
    def __init__(self, name: str = loaders[0], **kwargs):
        if name not in loaders:
            raise InvalidEntityID("'{}' is not a valid name for this type".format(name))
        super(Loader, self).__init__(name, **kwargs)

        for unused_arg in self.unused_args:
            warn_user("{} has no attribute '{}'".format(type(self), unused_arg))


class ElectricPole(CircuitConnectableMixin, PowerConnectableMixin, Entity):
    """
    """
    def __init__(self, name: str = electric_poles[0], **kwargs):
        if name not in electric_poles:
            raise InvalidEntityID("'{}' is not a valid name for this type".format(name))
        super(ElectricPole, self).__init__(name, **kwargs)


class Pipe(Entity):
    """
    """
    def __init__(self, name: str = pipes[0], **kwargs):
        if name not in pipes:
            raise InvalidEntityID("'{}' is not a valid name for this type".format(name))
        super(Pipe, self).__init__(name, **kwargs)

        for unused_arg in self.unused_args:
            warn_user("{} has no attribute '{}'".format(type(self), unused_arg))


class UndergroundPipe(DirectionalMixin, Entity):
    """
    """
    def __init__(self, name: str = underground_pipes[0], **kwargs):
        if name not in underground_pipes:
            raise InvalidEntityID("'{}' is not a valid name for this type".format(name))
        super(UndergroundPipe, self).__init__(name, **kwargs)

        for unused_arg in self.unused_args:
            warn_user("{} has no attribute '{}'".format(type(self), unused_arg))


class Pump(CircuitConditionMixin, CircuitConnectableMixin, DirectionalMixin, 
           Entity):
    """
    """
    def __init__(self, name: str = pumps[0], **kwargs):
        if name not in pumps:
            raise InvalidEntityID("'{}' is not a valid name for this type".format(name))
        super(Pump, self).__init__(name, **kwargs)

        for unused_arg in self.unused_args:
            warn_user("{} has no attribute '{}'".format(type(self), unused_arg))


class StraightRail(EightWayDirectionalMixin, Entity):
    """
    """
    def __init__(self, name: str = straight_rails[0], **kwargs):
        if name not in straight_rails:
            raise InvalidEntityID("'{}' is not a valid name for this type".format(name))
        super(StraightRail, self).__init__(name, **kwargs)

        for unused_arg in self.unused_args:
            warn_user("{} has no attribute '{}'".format(type(self), unused_arg))


class CurvedRail(EightWayDirectionalMixin, Entity):
    """
    """
    def __init__(self, name: str = curved_rails[0], **kwargs):
        if name not in curved_rails:
            raise InvalidEntityID("'{}' is not a valid name for this type".format(name))
        super(CurvedRail, self).__init__(name, **kwargs)

        for unused_arg in self.unused_args:
            warn_user("{} has no attribute '{}'".format(type(self), unused_arg))


class TrainStop(ColorMixin, CircuitConditionMixin, LogisticConditionMixin, 
                ControlBehaviorMixin, CircuitConnectableMixin, 
                EightWayDirectionalMixin, Entity):
    """
    """
    def __init__(self, name: str = train_stops[0], **kwargs):
        if name not in train_stops:
            raise InvalidEntityID("'{}' is not a valid name for this type".format(name))
        super(TrainStop, self).__init__(name, **kwargs)

        self.station = None
        if "station" in kwargs:
            self.set_station_name(kwargs["station"])
        self._add_export("station", lambda x: x is not None)

        self.manual_trains_limit = None
        if "manual_trains_limit" in kwargs:
            self.set_manual_trains_limit(kwargs["manual_trains_limit"])
        self._add_export("manual_trains_limit", lambda x: x is not None)

        for unused_arg in self.unused_args:
            warn_user("{} has no attribute '{}'".format(type(self), unused_arg))

    def set_station_name(self, name: str) -> None:
        """
        """
        # TODO: error checking
        self.station = name

    def set_manual_trains_limit(self, amount: int) -> None:
        """
        """
        # TODO: error checking
        self.manual_trains_limit = amount

    def set_read_from_train(self, value: bool) -> None:
        """
        """
        # TODO: error checking
        if value is None:
            self.control_behavior.pop("read_from_train", None)
        else:
            self.control_behavior["read_from_train"] = value

    def set_read_stopped_train(self, value: bool) -> None:
        """
        """
        # TODO: error checking
        if value is None:
            self.control_behavior.pop("read_stopped_train", None)
        else:
            self.control_behavior["read_stopped_train"] = value
        
        # This bit might be desirable, might not be
        # if value is True and \
        #    "train_stopped_signal" not in self.control_behavior:
        #     # Set default signal
        #     self.control_behavior["train_stopped_signal"] = signal_dict("signal-T")

    def set_train_stopped_signal(self, signal: str) -> None:
        """
        """
        # TODO: error checking
        if signal is None:
            self.control_behavior.pop("train_stopped_signal", None)
        else:
            self.control_behavior["train_stopped_signal"] = signal_dict(signal)

        # This bit might be desirable, might not be
        # if signal is not None and \
        #    "read_stopped_train" not in self.control_behavior:
        #     # Enable train signal reading
        #     self.control_behavior["read_stopped_train"] = True

    def set_trains_limit(self, value: bool) -> None:
        """
        """
        # TODO: error checking
        if value is None:
            self.control_behavior.pop("set_trains_limit", None)
        else:
            self.control_behavior["set_trains_limit"] = value

    def set_trains_limit_signal(self, signal: str) -> None:
        """
        """
        # TODO: error checking
        if signal is None:
            self.control_behavior.pop("trains_limit_signal", None)
        else:
            self.control_behavior["trains_limit_signal"] = signal_dict(signal)

    def set_read_trains_count(self, value: bool) -> None:
        """
        """
        # TODO: error checking
        if value is None:
            self.control_behavior.pop("read_trains_count", None)
        else:
            self.control_behavior["read_trains_count"] = value

    def set_trains_count_signal(self, signal: str) -> None:
        """
        """
        # TODO: error checking
        if signal is None:
            self.control_behavior.pop("trains_count_signal", None)
        else:
            self.control_behavior["trains_count_signal"] = signal_dict(signal)
        

class RailSignal(ReadRailSignalMixin, CircuitConditionMixin, 
                 ControlBehaviorMixin, CircuitConnectableMixin, 
                 EightWayDirectionalMixin, Entity):
    """
    """
    def __init__(self, name: str = rail_signals[0], **kwargs):
        if name not in rail_signals:
            raise InvalidEntityID("'{}' is not a valid name for this type".format(name))
        super(RailSignal, self).__init__(name, **kwargs)

        for unused_arg in self.unused_args:
            warn_user("{} has no attribute '{}'".format(type(self), unused_arg))

    def set_read_signal(self, value: bool) -> None:
        """
        """
        # TODO: error checking
        if value is None:
            self.control_behavior.pop("circuit_read_signal", None)
        else:
            self.control_behavior["circuit_read_signal"] = value

    def set_enable_disable(self, value: bool) -> None:
        """
        Overwritten method
        """
        # TODO: error checking
        if value is None:
            self.control_behavior.pop("circuit_close_signal", None)
        else:
            self.control_behavior["circuit_close_signal"] = value


class RailChainSignal(ReadRailSignalMixin, ControlBehaviorMixin, 
                      CircuitConnectableMixin, EightWayDirectionalMixin, 
                      Entity):
    """
    """
    def __init__(self, name: str = rail_chain_signals[0], **kwargs):
        if name not in rail_chain_signals:
            raise InvalidEntityID("'{}' is not a valid name for this type".format(name))
        super(RailChainSignal, self).__init__(name, **kwargs)

        for unused_arg in self.unused_args:
            warn_user("{} has no attribute '{}'".format(type(self), unused_arg))
    
    def set_blue_output_signal(self, signal: str) -> None:
        """
        """
        # TODO: error_checking
        if signal is None:
            self.control_behavior.pop("blue_output_signal", None)
        else:
            self.control_behavior["blue_output_signal"] = signal_dict(signal)


class Locomotive(ColorMixin, OrientationMixin, Entity):
    """
    """
    def __init__(self, name: str = locomotives[0], **kwargs):
        if name not in locomotives:
            raise InvalidEntityID("'{}' is not a valid name for this type".format(name))
        super(Locomotive, self).__init__(name, **kwargs)

        for unused_arg in self.unused_args:
            warn_user("{} has no attribute '{}'".format(type(self), unused_arg))


class CargoWagon(InventoryFilterMixin, OrientationMixin, Entity):
    """
    """
    def __init__(self, name: str = cargo_wagons[0], **kwargs):
        if name not in cargo_wagons:
            raise InvalidEntityID("'{}' is not a valid name for this type".format(name))
        super(CargoWagon, self).__init__(name, **kwargs)

        for unused_arg in self.unused_args:
            warn_user("{} has no attribute '{}'".format(type(self), unused_arg))


class FluidWagon(OrientationMixin, Entity):
    """
    """
    def __init__(self, name: str = fluid_wagons[0], **kwargs):
        if name not in fluid_wagons:
            raise InvalidEntityID("'{}' is not a valid name for this type".format(name))
        super(FluidWagon, self).__init__(name, **kwargs)

        for unused_arg in self.unused_args:
            warn_user("{} has no attribute '{}'".format(type(self), unused_arg))


class ArtilleryWagon(OrientationMixin, Entity):
    """
    """
    def __init__(self, name: str = artillery_wagons[0], **kwargs):
        if name not in artillery_wagons:
            raise InvalidEntityID("'{}' is not a valid name for this type".format(name))
        super(ArtilleryWagon, self).__init__(name, **kwargs)

        for unused_arg in self.unused_args:
            warn_user("{} has no attribute '{}'".format(type(self), unused_arg))


class LogisticStorageContainer(CircuitConnectableMixin, RequestFiltersMixin, 
                               InventoryMixin, Entity):
    """
    """
    def __init__(self, name: str = logistic_storage_containers[0], **kwargs):
        if name not in logistic_storage_containers:
            raise InvalidEntityID("'{}' is not a valid name for this type".format(name))
        super(LogisticStorageContainer, self).__init__(name, **kwargs)

        for unused_arg in self.unused_args:
            warn_user("{} has no attribute '{}'".format(type(self), unused_arg))


class LogisticBufferContainer(ModeOfOperationMixin, ControlBehaviorMixin, 
                              CircuitConnectableMixin, RequestFiltersMixin, 
                              InventoryMixin, Entity):
    """
    """
    def __init__(self, name: str = logistic_buffer_containers[0], **kwargs):
        if name not in logistic_buffer_containers:
            raise InvalidEntityID("'{}' is not a valid name for this type".format(name))
        super(LogisticBufferContainer, self).__init__(name, **kwargs)

        for unused_arg in self.unused_args:
            warn_user("{} has no attribute '{}'".format(type(self), unused_arg))


class LogisticRequestContainer(ModeOfOperationMixin, ControlBehaviorMixin, 
                               CircuitConnectableMixin, RequestFiltersMixin, 
                               InventoryMixin, Entity):
    """
    """
    def __init__(self, name: str = logistic_request_containers[0], **kwargs):
        if name not in logistic_request_containers:
            raise InvalidEntityID("'{}' is not a valid name for this type".format(name))
        super(LogisticRequestContainer, self).__init__(name, **kwargs)

        self.request_from_buffers = None
        if "request_from_buffers" in kwargs:
            self.set_request_from_buffers(kwargs["request_from_buffers"])
        self._add_export("request_from_buffers", lambda x: x is not None)

        for unused_arg in self.unused_args:
            warn_user("{} has no attribute '{}'".format(type(self), unused_arg))

    def set_request_from_buffers(self, value: bool) -> None:
        """
        Sets whether or not this requester can recieve items from buffer chests.
        """
        self.request_from_buffers = value


class Roboport(ControlBehaviorMixin, CircuitConnectableMixin, Entity):
    """
    """
    def __init__(self, name: str = roboports[0], **kwargs):
        if name not in roboports:
            raise InvalidEntityID("'{}' is not a valid name for this type".format(name))
        super(Roboport, self).__init__(name, **kwargs)

        for unused_arg in self.unused_args:
            warn_user("{} has no attribute '{}'".format(type(self), unused_arg))

    def set_read_logistics(self, value: bool) -> None:
        """
        """
        # TODO: error checking
        if value is None:
            self.control_behavior.pop("read_logistics", None)
        else:
            self.control_behavior["read_logistics"] = value

    def set_read_robot_stats(self, value: bool) -> None:
        """
        """
        # TODO: error checking
        if value is None:
            self.control_behavior.pop("read_robot_stats", None)
        else:
            self.control_behavior["read_robot_stats"] = value

    def set_available_logistics_signal(self, signal: str) -> None:
        """
        """
        if signal is None:
            self.control_behavior.pop("available_logistic_output_signal", None)
        else:
            self.control_behavior["available_logistic_output_signal"] = signal_dict(signal)

    def set_total_logistics_signal(self, signal: str) -> None:
        """
        """
        if signal is None:
            self.control_behavior.pop("total_logistic_output_signal", None)
        else:
            self.control_behavior["total_logistic_output_signal"] = signal_dict(signal)

    def set_available_construction_signal(self, signal: str) -> None:
        """
        """
        if signal is None:
            self.control_behavior.pop("available_construction_output_signal", None)
        else:
            self.control_behavior["available_construction_output_signal"] = signal_dict(signal)

    def set_total_construction_signal(self, signal: str) -> None:
        """
        """
        if signal is None:
            self.control_behavior.pop("total_construction_output_signal", None)
        else:
            self.control_behavior["total_construction_output_signal"] = signal_dict(signal)


class Lamp(CircuitConditionMixin, ControlBehaviorMixin, CircuitConnectableMixin,
           Entity):
    """
    """
    def __init__(self, name: str = lamps[0], **kwargs):
        if name not in lamps:
            raise InvalidEntityID("'{}' is not a valid name for this type".format(name))
        super(Lamp, self).__init__(name, **kwargs)

        for unused_arg in self.unused_args:
            warn_user("{} has no attribute '{}'".format(type(self), unused_arg))

    def set_enable_disable(self, value: bool) -> None:
        # TODO: handle this a little more elegantly
        # I dont want to change CircuitConditionMixin into two separate mixins
        # for this ONE entity
        raise NotImplementedError()

    def set_use_colors(self, value: bool) -> None:
        """
        """
        # TODO: error checking
        if value is None:
            self.control_behavior.pop("use_colors", None)
        else:
            self.control_behavior["use_colors"] = value


class ArithmeticCombinator(ControlBehaviorMixin, CircuitConnectableMixin, 
                           DirectionalMixin, Entity):
    """
    """
    def __init__(self, name: str = arithmetic_combinators[0], **kwargs):
        if name not in arithmetic_combinators:
            raise InvalidEntityID("'{}' is not a valid name for this type".format(kwargs["name"]))
        super().__init__(name, **kwargs)

        self.dual_circuit_connectable = True

        for unused_arg in self.unused_args:
            warn_user("{} has no attribute '{}'".format(type(self), unused_arg))

    def set_arithmetic_conditions(self, a: Union[str, int] = None, op: str = "*", b: Union[str, int] = 0, out: str = None):
        """
        """
        if "arithmetic_conditions" not in self.control_behavior:
            self.control_behavior["arithmetic_conditions"] = {}
        arithmetic_conditions = self.control_behavior["arithmetic_conditions"]
        # TODO: error checking
        # A
        if a is None:
            pass # Default
        elif isinstance(a, str):
            arithmetic_conditions["first_signal"] = signal_dict(a)
        elif isinstance(a, int):
            arithmetic_conditions["first_constant"] = a
        else:
            raise TypeError("First param is neither 'str', 'int' or 'None'")

        # op
        valid_operations = [
            "*", "/", "+", "-", "%", "^", "<<", ">>", "AND", "OR", "XOR"
        ]
        if op.upper() not in valid_operations:
            raise InvalidArithmeticOperation(op)
        arithmetic_conditions["operation"] = op.upper()

        # B
        if isinstance(b, str):
            arithmetic_conditions["second_signal"] = signal_dict(b)
        elif isinstance(b, int):
            arithmetic_conditions["second_constant"] = b
        else:
            raise TypeError("Second param is neither 'str' or 'int'")

        # out
        if out is None:
            pass # Default
        elif isinstance(out, str):
            arithmetic_conditions["output_signal"] = signal_dict(out)
        else:
            raise TypeError("Output param is neither 'str' or 'None'")

    def remove_arithmetic_conditions(self):
        """
        """
        self.control_behavior.pop("arithmetic_conditions", None)


class DeciderCombinator(ControlBehaviorMixin, CircuitConnectableMixin, 
                        DirectionalMixin, Entity):
    """
    """
    def __init__(self, name: str = decider_combinators[0], **kwargs):
        if name not in decider_combinators:
            raise InvalidEntityID("'{}' is not a valid name for this type".format(name))
        super(DeciderCombinator, self).__init__(name, **kwargs)

        self.dual_circuit_connectable = True

        for unused_arg in self.unused_args:
            warn_user("{} has no attribute '{}'".format(type(self), unused_arg))
    
    def set_decider_conditions(self, a, op, b, out):
        """
        """
        if "decider_conditions" not in self.control_behavior:
            self.control_behavior["decider_conditions"] = {}
        decider_conditions = self.control_behavior["decider_conditions"]
        # TODO: error checking
        # A
        if a is None:
            pass # Default
        elif isinstance(a, str):
            decider_conditions["first_signal"] = signal_dict(a)
        elif isinstance(a, int):
            decider_conditions["first_constant"] = a
        else:
            raise TypeError("First param is neither 'str', 'int' or 'None'")

        # op
        valid_comparisons =  [">", "<", "=", ">=", "<=", "!="]
        if op not in valid_comparisons:
            raise InvalidConditionOperation(op)
        actual_comparisons = [">", "<", "=", "≥",  "≤",  "≠"]
        index = valid_comparisons.index(op)
        op = actual_comparisons[index]
        decider_conditions["comparator"] = op

        # B
        if isinstance(b, str):
            decider_conditions["second_signal"] = signal_dict(b)
        elif isinstance(b, int):
            decider_conditions["second_constant"] = b
        else:
            raise TypeError("Second param is neither 'str' or 'int'")

        # out
        if out is None:
            pass # Default
        elif isinstance(out, str):
            decider_conditions["output_signal"] = signal_dict(out)
        else:
            raise TypeError("Output param is neither 'str' or 'None'")

    def set_copy_count_from_input(self, value: bool) -> None:
        """
        """
        if value is None:
            self.control_behavior["decider_conditions"].pop("copy_count_from_input", None)

        if "decider_conditions" not in self.control_behavior:
            self.control_behavior["decider_conditions"] = {}

        self.control_behavior["decider_conditions"]["copy_count_from_input"] = value

    def remove_decider_conditions(self):
        """
        """
        self.control_behavior.pop("decider_conditions", None)


class ConstantCombinator(ControlBehaviorMixin, CircuitConnectableMixin, 
                         DirectionalMixin, Entity):
    """
    TODO: maybe keep signal filters internally as an array of Signal objects,
    and then use Signal.to_dict() during that stage?
    """
    def __init__(self, name: str = constant_combinators[0], **kwargs):
        if name not in constant_combinators:
            raise InvalidEntityID("'{}' is not a valid name for this type".format(name))
        super(ConstantCombinator, self).__init__(name, **kwargs)

        for unused_arg in self.unused_args:
            warn_user("{} has no attribute '{}'".format(type(self), unused_arg))

    def set_signal(self, index: int, name: str, count: int = 0) -> None:
        """
        """
        if "filters" not in self.control_behavior:
            self.control_behavior["filters"] = []
        
        # TODO: error checking
        
        # Check to see if filters already contains an entry with the same index
        for i, filter in enumerate(self.control_behavior["filters"]):
            if index+1 == filter["index"]: # Index already exists in the list
                if name is None: # Delete the entry
                    del self.control_behavior["filters"][i]
                else: # Set the new value
                    self.control_behavior["filters"][i] = {
                        "index": index + 1,"signal": signal_dict(name), "count": count
                    }

                return

        # If no entry with the same index was found
        self.control_behavior["filters"].append({
            "index": index + 1, "signal": signal_dict(name), "count": count
        })

    def set_signals(self, signals: list) -> None:
        pass # TODO

    def get_signal(self, index: int) -> Signal:
        """
        """
        return None # TODO

    def clear_signals(self) -> None:
        """
        Clears all signals in the constant combinator, if any are present.
        """
        self.control_behavior.pop("filters", None)


class PowerSwitch(CircuitConditionMixin, LogisticConditionMixin, 
                  ControlBehaviorMixin, CircuitConnectableMixin, 
                  PowerConnectableMixin, DirectionalMixin, Entity):
    """
    """
    def __init__(self, name: str = power_switches[0], **kwargs):
        if name not in power_switches:
            raise InvalidEntityID("'{}' is not a valid name for this type".format(name))
        super(PowerSwitch, self).__init__(name, **kwargs)

        self.switch_state = None
        if "switch_state" in kwargs:
            self.set_switch_state(kwargs["switch_state"])
        self._add_export("switch_state", lambda x: x is not None)

        for unused_arg in self.unused_args:
            warn_user("{} has no attribute '{}'".format(type(self), unused_arg))

    def set_switch_state(self, value: bool) -> None:
        """
        """
        self.switch_state = value

    def _add_power_connection(self, target_entity: Entity, entity_id: Union[int, str], source_side: int = 1) -> None:
        """
        """
        # TODO: error checking
        if target_entity.dual_power_connectable:
            raise Exception("2 dual power connectable entities cannot connect")
        
        if source_side == 1:
            if "Cu0" not in self.connections:
                self.connections["Cu0"] = []

            # Check to see if the entity already exists within
            for connection in self.connections["Cu0"]:
                if connection["entity_id"] == entity_id:
                    return

            self.connections["Cu0"].append({"entity_id": entity_id, "wire_id": 0})
        elif source_side == 2:
            if "Cu1" not in self.connections:
                self.connections["Cu1"] = []

            # Check to see if the entity already exists within
            for connection in self.connections["Cu1"]:
                if connection["entity_id"] == entity_id:
                    return

            self.connections["Cu1"].append({"entity_id": entity_id, "wire_id": 0})
        else:
            raise ValueError("source_side neither 1 nor 2")


class ProgrammableSpeaker(CircuitConditionMixin, ControlBehaviorMixin, 
                          CircuitConnectableMixin, Entity):
    """
    """
    def __init__(self, name: str = programmable_speakers[0], **kwargs):
        if name not in programmable_speakers:
            raise InvalidEntityID("'{}' is not a valid name for this type".format(name))
        super(ProgrammableSpeaker, self).__init__(name, **kwargs)

        self.parameters = {}
        if "parameters" in kwargs:
            self.set_parameters(kwargs["parameters"])
        self._add_export("parameters", lambda x: len(x) != 0)

        self.alert_parameters = {}
        if "alert_parameters" in kwargs:
            self.set_alert_parameters(kwargs["alert_parameters"])
            self._normalize_alert_parameters()
        self._add_export("alert_parameters", lambda x: len(x) != 0)

        # Name translations for all of the instruments and their notes
        # maybe something like this?
        self.instruments = draftsman.data.instruments.instruments[self.name]

        for unused_arg in self.unused_args:
            warn_user("{} has no attribute '{}'".format(type(self), unused_arg))

    def set_parameters(self, parameters: dict) -> None:
        """
        """
        # TODO: error checking
        self.parameters = parameters

    def set_alert_parameters(self, alert_parameters: dict) -> None:
        """
        """
        # TODO: error checking
        self.alert_parameters = alert_parameters

    def set_volume(self, volume: float) -> None:
        """
        """
        # TODO: error checking
        if volume is None:
            self.parameters.pop("playback_volume", None)
        else:
            self.parameters["playback_volume"] = volume

    def set_global_playback(self, value: bool) -> None:
        """
        """
        # TODO: error checking
        if value is None:
            self.parameters.pop("playback_globally", None)
        else:
            self.parameters["playback_globally"] = value

    def set_show_alert(self, value: bool) -> None:
        """
        """
        # TODO: error checking
        if value is None:
            self.alert_parameters.pop("show_alert", None)
        else:
            self.alert_parameters["show_alert"] = value

    def set_polyphony(self, value: bool) -> None:
        """
        """
        # TODO: error checking
        if value is None:
            self.parameters.pop("allow_polyphony", None)
        else:
            self.parameters["allow_polyphony"] = value

    def set_show_alert_on_map(self, value: bool) -> None:
        """
        """
        # TODO: error checking
        if value is None:
            self.alert_parameters.pop("show_on_map", None)
        else:
            self.alert_parameters["show_on_map"] = value

    def set_alert_icon(self, signal: str) -> None:
        """
        """
        # TODO: error checking
        if signal is None:
            self.alert_parameters.pop("icon_signal_id", None)
        else:
            self.alert_parameters["icon_signal_id"] = signal_dict(signal)

    def set_alert_message(self, message: str) -> None:
        """
        """
        # TODO: error checking
        if message is None:
            self.alert_parameters.pop("alert_message", None)
        else:
            self.alert_parameters["alert_message"] = message

    def set_signal_value_is_pitch(self, value: bool) -> None:
        """
        """
        # TODO: error checking
        if "circuit_parameters" not in self.control_behavior:
            self.control_behavior["circuit_parameters"] = {}
        circuit_params = self.control_behavior["circuit_parameters"]

        if value is None:
            circuit_params.pop("signal_value_is_pitch", None)
        else:
            circuit_params["signal_value_is_pitch"] = value

    def set_instrument(self, instrument: Union[int, str]) -> None:
        """
        """
        # TODO: error checking
        if "circuit_parameters" not in self.control_behavior:
            self.control_behavior["circuit_parameters"] = {}
        circuit_params = self.control_behavior["circuit_parameters"]

        if instrument is None:
            circuit_params.pop("instrument_id", None)
        elif isinstance(instrument, int):
            circuit_params["instrument_id"] = instrument
        elif isinstance(instrument, str):
            instrument = self.instruments[instrument]["index"]
            circuit_params["instrument_id"] = instrument
        else:
            raise TypeError("instrument_id is neither int nor str")

        #self._normalize_circuit_parameters()

    def set_note(self, note: Union[int, str]) -> None:
        """
        """
        # TODO: error checking
        if "circuit_parameters" not in self.control_behavior:
            self.control_behavior["circuit_parameters"] = {}
        circuit_params = self.control_behavior["circuit_parameters"]

        if note is None:
            circuit_params.pop("note_id", None)
        elif isinstance(note, int):
            circuit_params["note_id"] = note
        elif isinstance(note, str):
            # Look for instrument
            instrument_index = circuit_params["instrument_id"] or 0
            # Get notes from that instrument
            instrument_notes = self.instruments[instrument_index].notes
            circuit_params["note_id"] = instrument_notes.index(note)
        else:
            raise TypeError("note_id is neither int nor str")


    def _normalize_circuit_parameters(self):
        """
        """
        # TODO: handle strings using self.instruments
        if "circuit_parameters" in self.control_behavior:
            circuit_params = self.control_behavior["circuit_parameters"]
            if "instrument_id" in circuit_params:
                instrument = circuit_params["instrument_id"]
                if isinstance(instrument, str):
                    instrument_id = self.instruments.index(instrument)
                    circuit_params["instrument_id"] = instrument_id
            if "note_id" in circuit_params:
                note = circuit_params["note_id"]
                if isinstance(note, str):
                    note_id = self.instruments[instrument].index(note)
                    circuit_params["note_id"] = note_id

        pass

    def _normalize_alert_parameters(self):
        """
        """
        if "icon_signal_id" in self.alert_parameters:
            id = self.alert_parameters["icon_signal_id"]
            if isinstance(id, str):
                self.alert_parameters["icon_signal_id"] = signal_dict(id)


class Boiler(DirectionalMixin, Entity):
    def __init__(self, name: str = boilers[0], **kwargs):
        if name not in boilers:
            raise InvalidEntityID("'{}' is not a valid name for this type".format(name))
        super(Boiler, self).__init__(name, **kwargs)

        for unused_arg in self.unused_args:
            warn_user("{} has no attribute '{}'".format(type(self), unused_arg))


class Generator(DirectionalMixin, Entity):
    def __init__(self, name: str, **kwargs):
        if name not in generators:
            raise InvalidEntityID("'{}' is not a valid name for this type".format(name))
        super(Generator, self).__init__(name, **kwargs)

        for unused_arg in self.unused_args:
            warn_user("{} has no attribute '{}'".format(type(self), unused_arg))


class SolarPanel(Entity):
    def __init__(self, name: str = solar_panels[0], **kwargs):
        if name not in solar_panels:
            raise InvalidEntityID("'{}' is not a valid name for this type".format(name))
        super(SolarPanel, self).__init__(name, **kwargs)

        for unused_arg in self.unused_args:
            warn_user("{} has no attribute '{}'".format(type(self), unused_arg))


class Accumulator(ControlBehaviorMixin, CircuitConnectableMixin, Entity):
    def __init__(self, name: str = accumulators[0], **kwargs):
        if name not in accumulators:
            raise InvalidEntityID("'{}' is not a valid name for this type".format(name))
        super(Accumulator, self).__init__(name, **kwargs)

        for unused_arg in self.unused_args:
            warn_user("{} has no attribute '{}'".format(type(self), unused_arg))

    def set_output_signal(self, signal: str) -> None:
        """
        """
        # TODO: error checking
        if signal is None:
            self.control_behavior.pop("output_signal", None)
        else:
            self.control_behavior["output_signal"] = signal_dict(signal)


class Reactor(Entity):
    def __init__(self, name: str = reactors[0], **kwargs):
        if name not in reactors:
            raise InvalidEntityID("'{}' is not a valid name for this type".format(name))
        super(Reactor, self).__init__(name, **kwargs)

        for unused_arg in self.unused_args:
            warn_user("{} has no attribute '{}'".format(type(self), unused_arg))


class HeatPipe(Entity):
    def __init__(self, name: str = heat_pipes[0], **kwargs):
        if name not in heat_pipes:
            raise InvalidEntityID("'{}' is not a valid name for this type".format(name))
        super(HeatPipe, self).__init__(name, **kwargs)

        for unused_arg in self.unused_args:
            warn_user("{} has no attribute '{}'".format(type(self), unused_arg))


class MiningDrill(RequestItemsMixin, CircuitReadResourceMixin, 
                  CircuitConditionMixin, LogisticConditionMixin, 
                  ControlBehaviorMixin, CircuitConnectableMixin, 
                  DirectionalMixin, Entity):
    def __init__(self, name: str = mining_drills[0], **kwargs):
        if name not in mining_drills:
            raise InvalidEntityID("'{}' is not a valid name for this type".format(name))
        super(MiningDrill, self).__init__(name, **kwargs)

        for unused_arg in self.unused_args:
            warn_user("{} has no attribute '{}'".format(type(self), unused_arg))


class OffshorePump(CircuitConditionMixin, LogisticConditionMixin, 
                   ControlBehaviorMixin, CircuitConnectableMixin, 
                   DirectionalMixin, Entity):
    def __init__(self, name: str = offshore_pumps[0], **kwargs):
        if name not in offshore_pumps:
            raise InvalidEntityID("'{}' is not a valid name for this type".format(name))
        super(OffshorePump, self).__init__(name, **kwargs)

        for unused_arg in self.unused_args:
            warn_user("{} has no attribute '{}'".format(type(self), unused_arg))


class Furnace(RequestItemsMixin, Entity):
    def __init__(self, name: str = furnaces[0], **kwargs):
        if name not in furnaces:
            raise InvalidEntityID("'{}' is not a valid name for this type".format(name))
        super(Furnace, self).__init__(name, **kwargs)

        for unused_arg in self.unused_args:
            warn_user("{} has no attribute '{}'".format(type(self), unused_arg))


class AssemblingMachine(RequestItemsMixin, RecipeMixin, Entity):
    def __init__(self, name: str = assembling_machines[0], **kwargs):
        if name not in assembling_machines:
            raise InvalidEntityID("'{}' is not a valid name for this type".format(name))
        super(AssemblingMachine, self).__init__(name, **kwargs)

        for unused_arg in self.unused_args:
            warn_user("{} has no attribute '{}'".format(type(self), unused_arg))


class Lab(Entity):
    def __init__(self, name: str = labs[0], **kwargs):
        if name not in labs:
            raise InvalidEntityID("'{}' is not a valid name for this type".format(name))
        super(Lab, self).__init__(name, **kwargs)

        for unused_arg in self.unused_args:
            warn_user("{} has no attribute '{}'".format(type(self), unused_arg))


class Beacon(RequestItemsMixin, Entity):
    def __init__(self, name: str = beacons[0], **kwargs):
        if name not in beacons:
            raise InvalidEntityID("'{}' is not a valid name for this type".format(name))
        super(Beacon, self).__init__(name, **kwargs)

        for unused_arg in self.unused_args:
            warn_user("{} has no attribute '{}'".format(type(self), unused_arg))


class RocketSilo(Entity):
    def __init__(self, name: str = rocket_silos[0], **kwargs):
        if name not in rocket_silos:
            raise InvalidEntityID("'{}' is not a valid name for this type".format(name))
        super(RocketSilo, self).__init__(name, **kwargs)

        self.auto_launch = None
        if "auto_launch" in kwargs:
            self.set_auto_launch(kwargs["auto_launch"])
        self._add_export("auto_launch", lambda x: x is not None)

        for unused_arg in self.unused_args:
            warn_user("{} has no attribute '{}'".format(type(self), unused_arg))

    def set_auto_launch(self, value: bool) -> None:
        """
        """
        # TODO: error checking
        self.auto_launch = value


class LandMine(Entity):
    def __init__(self, name: str = land_mines[0], **kwargs):
        if name not in land_mines:
            raise InvalidEntityID("'{}' is not a valid name for this type".format(name))
        super(LandMine, self).__init__(name, **kwargs)

        for unused_arg in self.unused_args:
            warn_user("{} has no attribute '{}'".format(type(self), unused_arg))


# Technically CircuitConnectable, but only when adjacent to a gate
class Wall(CircuitConditionMixin, ControlBehaviorMixin, CircuitConnectableMixin, 
           Entity):
    def __init__(self, name: str = walls[0], **kwargs):
        if name not in walls:
            raise InvalidEntityID("'{}' is not a valid name for this type".format(name))
        super(Wall, self).__init__(name, **kwargs)

        for unused_arg in self.unused_args:
            warn_user("{} has no attribute '{}'".format(type(self), unused_arg))

    def set_enable_disable(self, value: bool) -> None:
        """
        Overwritten
        """
        # TODO: check if we're adjacent to a gate
        # TODO: error checking
        if value is None:
            self.control_behavior.pop("circuit_open_gate", None)
        else:
            self.control_behavior["circuit_open_gate"] = value

    def set_read_gate(self, value: bool) -> None:
        """
        """
        # TODO: check if we're adjacent to a gate
        # TODO: error checking
        if value is None:
            self.control_behavior.pop("circuit_read_sensor", None)
        else:
            self.control_behavior["circuit_read_sensor"] = value

    def set_output_signal(self, signal: bool) -> None:
        """
        """
        # TODO: check if we're adjacent to a gate
        # TODO: error checking
        if signal is None:
            self.control_behavior.pop("output_signal", None)
        else:
            self.control_behavior["output_signal"] = signal_dict(signal)



class Gate(DirectionalMixin, Entity):
    def __init__(self, name: str = gates[0], **kwargs):
        if name not in gates:
            raise InvalidEntityID("'{}' is not a valid name for this type".format(name))
        super(Gate, self).__init__(name, **kwargs)

        for unused_arg in self.unused_args:
            warn_user("{} has no attribute '{}'".format(type(self), unused_arg))


class Turret(DirectionalMixin, Entity):
    def __init__(self, name: str = turrets[0], **kwargs):
        if name not in turrets:
            raise InvalidEntityID("'{}' is not a valid name for this type".format(name))
        super(Turret, self).__init__(name, **kwargs)

        for unused_arg in self.unused_args:
            warn_user("{} has no attribute '{}'".format(type(self), unused_arg))


class Radar(Entity):
    def __init__(self, name: str = radars[0], **kwargs):
        if name not in radars:
            raise InvalidEntityID("'{}' is not a valid name for this type".format(name))
        super(Radar, self).__init__(name, **kwargs)

        for unused_arg in self.unused_args:
            warn_user("{} has no attribute '{}'".format(type(self), unused_arg))


class ElectricEnergyInterface(Entity):
    def __init__(self, name: str = electric_energy_interfaces[0], **kwargs):
        if name not in electric_energy_interfaces:
            raise InvalidEntityID("'{}' is not a valid name for this type".format(name))
        super(ElectricEnergyInterface, self).__init__(name, **kwargs)

        self.buffer_size = None # TODO: default
        if "buffer_size" in kwargs:
            self.set_buffer_size(kwargs["buffer_size"])
        self._add_export("buffer_size", lambda x: x is not None)

        self.power_production = None # TODO: default
        if "power_production" in kwargs:
            self.set_power_production(kwargs["power_production"])
        self._add_export("power_production", lambda x: x is not None)

        self.power_usage = None # TODO: default
        if "power_production" in kwargs:
            self.set_power_usage(kwargs["power_usage"])
        self._add_export("power_usage", lambda x: x is not None)

        for unused_arg in self.unused_args:
            warn_user("{} has no attribute '{}'".format(type(self), unused_arg))

    def set_buffer_size(self, amount: int) -> None:
        """
        """
        self.buffer_size = amount

    def set_power_production(self, amount: int) -> None:
        """
        """
        self.power_production = amount

    def set_power_usage(self, amount: int) -> None:
        """
        """
        self.power_usage = amount


class LinkedContainer(Entity):
    def __init__(self, name: str = linked_containers[0], **kwargs):
        if name not in linked_containers:
            raise InvalidEntityID("'{}' is not a valid name for this type".format(name))
        super(LinkedContainer, self).__init__(name, **kwargs)

        self.link_id = 0
        if "link_id" in kwargs:
            self.set_link_id(kwargs["link_id"])
        self._add_export("link_id", lambda x: x != 0)

        for unused_arg in self.unused_args:
            warn_user("{} has no attribute '{}'".format(type(self), unused_arg))

    def set_links(self, id: int) -> None:
        """
        """
        # assert id in range(0, 2^32-1)
        if id is None:
            self.link_id = 0
        else:
            self.link_id = id

    def set_link(self, number: int, enabled: bool) -> None:
        """
        """
        assert number < 32
        if enabled:
            self.link_id |= (1 << number)
        else:
            self.link_id &= ~(1 << number)


class HeatInterface(Entity):
    def __init__(self, name: str = heat_interfaces[0], **kwargs):
        if name not in heat_interfaces:
            raise InvalidEntityID("'{}' is not a valid name for this type".format(name))
        super(HeatInterface, self).__init__(name, **kwargs)

        self.temperature = 0
        if "temperature" in kwargs:
            self.set_temperature(kwargs["temperature"])
        self._add_export("temperature", lambda x: x is not None and x != 0)

        self.mode = "at-least"
        if "mode" in kwargs:
            self.set_mode(kwargs["mode"])
        self._add_export("mode", lambda x: x is not None and x != "at-least")

        for unused_arg in self.unused_args:
            warn_user("{} has no attribute '{}'".format(type(self), unused_arg))

    def set_temperature(self, temperature: int) -> None:
        """
        """
        # assert 0 <= temperature <= 1000
        if temperature is None:
            self.temperature = 0
        else:
            self.temperature = temperature

    def set_mode(self, mode: str) -> None:
        """
        * "at-least"
        * "at-most"
        * "exactly"
        * "add"
        * "remove"
        """
        if mode is None:
            self.mode = "at-least"
        else:
            if mode not in {"at-least", "at-most", "exactly", "add", "remove"}:
                raise InvalidMode(mode)
            self.mode = mode


class LinkedBelt(DirectionalMixin, Entity):
    """
    Currently unimplemented. Need to analyze how mods use this entity, as I 
    can't seem to figure out the example one in the game.
    """
    def __init__(self, name: str = linked_belts[0], **kwargs):
        if name not in linked_belts:
            raise InvalidEntityID("'{}' is not a valid name for this type".format(name))
        super(LinkedBelt, self).__init__(name, **kwargs)

        for unused_arg in self.unused_args:
            warn_user("{} has no attribute '{}'".format(type(self), unused_arg))


class InfinityContainer(InfinitySettingsMixin, Entity):
    """
    """
    def __init__(self, name: str = infinity_containers[0], **kwargs):
        if name not in infinity_containers:
            raise InvalidEntityID("'{}' is not a valid name for this type".format(name))
        super(InfinityContainer, self).__init__(name, **kwargs)

        # TODO: Validate that self.infinity_settings matches this class' signature
        # because this uses the same mixin as infintypipe, but they have different
        # formats

        for unused_arg in self.unused_args:
            warn_user("{} has no attribute '{}'".format(type(self), unused_arg))
    
    def set_remove_unfiltered_items(self, value: bool) -> None:
        """
        """
        # TODO: error checking
        if value is None:
            self.infinity_settings.pop("remove_unfiltered_items", None)
        else:
            self.infinity_settings["remove_unfiltered_items"] = value

    def set_infinity_filters(self, filters: list) -> None:
        """
        """
        # TODO: error checking
        if filters is None:
            self.infinity_settings.pop("filters", None)
        else:
            self.infinity_settings["filters"] = filters

    def set_infinity_filter(self, index: int, name: str, count: int, mode: str) -> None:
        """
        """
        if "filters" not in self.infinity_settings:
            self.infinity_settings["filters"] = []

        # TODO: error checking
        # assert mode in ["at-least", "at-most", "exactly"]

        # Check to see if filters already contains an entry with the same index
        for i, filter in enumerate(self.infinity_settings["filters"]):
            if index == filter["index"]: # Index already exists in the list
                if name is None: # Delete the entry
                    del self.inventory["filters"][i]
                else: # Set the new value
                    self.inventory["filters"][i] = {
                        "name": name,
                        "count": count,
                        "mode": mode,
                        "index": index + 1
                    }
                    
                return

        # If no entry with the same index was found
        self.inventory["filters"].append({
            "name": name,
            "count": count,
            "mode": mode,
            "index": index + 1 
        })


class InfinityPipe(InfinitySettingsMixin, Entity):
    """
    """
    def __init__(self, name: str = infinity_pipes[0], **kwargs):
        if name not in infinity_pipes:
            raise InvalidEntityID("'{}' is not a valid name for this type".format(name))
        super(InfinityPipe, self).__init__(name, **kwargs)

        # TODO: Validate that self.infinity_settings matches this class' signature

        for unused_arg in self.unused_args:
            warn_user("{} has no attribute '{}'".format(type(self), unused_arg))

    def set_infinite_fluid(self, name: str = None, percentage: int = 0, mode: str = "at-least", temperature: int = 0) -> None:
        """
        """
        self.set_infinite_fluid_name(name)
        self.set_infinite_fluid_percentage(percentage)
        self.set_infinite_fluid_mode(mode)
        self.set_infinite_fluid_temperature(temperature)

    def set_infinite_fluid_name(self, name: str) -> None:
        """
        """
        if name is None:
            self.infinity_settings.pop("name", None)
        else:
            # TODO: error checking
            # assert name in items
            self.infinity_settings["name"] = name

    def set_infinite_fluid_percentage(self, percent: int):
        """
        """
        if percent is None:
            self.infinity_settings.pop("percentage", None)
        else:
            # TODO: error checking
            self.infinity_settings["percentage"] = percent

    def set_infinite_fluid_mode(self, mode: str) -> None:
        """
        """
        if mode is None:
            self.infinity_settings.pop("mode", None)
        else:
            if mode not in {"at-least", "at-most", "exactly"}:
                raise InvalidMode(mode)
            self.infinity_settings["mode"] = mode

    def set_infinite_fluid_temperature(self, temperature: int) -> None:
        """
        """
        if temperature is None:
            self.infinity_settings.pop("temperature", None)
        else:
            # TODO: error checking
            self.infinity_settings["temperature"] = temperature
        

class BurnerGenerator(DirectionalMixin, Entity):
    """
    TODO: think about, because burner generators from mods like Space 
    Exploration don't have orientation. Are they the same entity type?
    """
    def __init__(self, name: str = burner_generators[0], **kwargs):
        if name not in burner_generators:
            raise InvalidEntityID("'{}' is not a valid name for this type".format(name))
        super(BurnerGenerator, self).__init__(name, **kwargs)

        for unused_arg in self.unused_args:
            warn_user("{} has no attribute '{}'".format(type(self), unused_arg))


def new_entity(name: str, **kwargs):
    if name in containers:
        return Container(name, **kwargs)
    if name in storage_tanks:
        return StorageTank(name, **kwargs)
    if name in transport_belts:
        return TransportBelt(name, **kwargs)
    if name in underground_belts:
        return UndergroundBelt(name, **kwargs)
    if name in splitters:
        return Splitter(name, **kwargs)
    if name in inserters:
        return Inserter(name, **kwargs)
    if name in filter_inserters:
        return FilterInserter(name, **kwargs)
    if name in loaders:
        return Loader(name, **kwargs)
    if name in electric_poles:
        return ElectricPole(name, **kwargs)
    if name in pipes:
        return Pipe(name, **kwargs)
    if name in underground_pipes:
        return UndergroundPipe(name, **kwargs)
    if name in pumps:
        return Pump(name, **kwargs)
    if name in straight_rails:
        return StraightRail(name, **kwargs)
    if name in curved_rails:
        return CurvedRail(name, **kwargs)
    if name in train_stops:
        return TrainStop(name, **kwargs)
    if name in rail_signals:
        return RailSignal(name, **kwargs)
    if name in rail_chain_signals:
        return RailChainSignal(name, **kwargs)
    if name in locomotives:
        return Locomotive(name, **kwargs)
    if name in cargo_wagons:
        return CargoWagon(name, **kwargs)
    if name in fluid_wagons:
        return FluidWagon(name, **kwargs)
    if name in artillery_wagons:
        return ArtilleryWagon(name, **kwargs)
    if name in logistic_storage_containers:
        return LogisticStorageContainer(name, **kwargs)
    if name in logistic_buffer_containers:
        return LogisticBufferContainer(name, **kwargs)
    if name in logistic_request_containers:
        return LogisticRequestContainer(name, **kwargs)
    if name in roboports:
        return Roboport(name, **kwargs)
    if name in lamps:
        return Lamp(name, **kwargs)
    if name in arithmetic_combinators:
        return ArithmeticCombinator(name, **kwargs)
    if name in decider_combinators:
        return DeciderCombinator(name, **kwargs)
    if name in constant_combinators:
        return ConstantCombinator(name, **kwargs)
    if name in power_switches:
        return PowerSwitch(name, **kwargs)
    if name in programmable_speakers:
        return ProgrammableSpeaker(name, **kwargs)
    if name in boilers:
        return Boiler(name, **kwargs)
    if name in generators:
        return Generator(name, **kwargs)
    if name in solar_panels:
        return SolarPanel(name, **kwargs)
    if name in accumulators:
        return Accumulator(name, **kwargs)
    if name in reactors:
        return Reactor(name, **kwargs)
    if name in heat_pipes:
        return HeatPipe(name, **kwargs)
    if name in mining_drills:
        return MiningDrill(name, **kwargs)
    if name in offshore_pumps:
        return OffshorePump(name, **kwargs)
    if name in furnaces:
        return Furnace(name, **kwargs)
    if name in assembling_machines:
        return AssemblingMachine(name, **kwargs)
    if name in labs:
        return Lab(name, **kwargs)
    if name in beacons:
        return Beacon(name, **kwargs)
    if name in rocket_silos:
        return RocketSilo(name, **kwargs)
    if name in land_mines:
        return LandMine(name, **kwargs)
    if name in walls:
        return Wall(name, **kwargs)
    if name in gates:
        return Gate(name, **kwargs)
    if name in turrets:
        return Turret(name, **kwargs)
    if name in radars:
        return Radar(name, **kwargs)
    if name in electric_energy_interfaces:
        return ElectricEnergyInterface(name, **kwargs)
    if name in linked_containers:
        return LinkedContainer(name, **kwargs)
    if name in heat_interfaces:
        return HeatInterface(name, **kwargs)
    if name in linked_belts:
        return LinkedBelt(name, **kwargs)
    if name in infinity_containers:
        return InfinityContainer(name, **kwargs)
    if name in infinity_pipes:
        return InfinityPipe(name, **kwargs)
    if name in burner_generators:
        return BurnerGenerator(name, **kwargs)
    
    raise InvalidEntityID(name)