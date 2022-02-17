# entity.py

# TODO: handle the difference between grid position and absolute position
# TODO: create verification for the initial load of an entity by making a schema for each entity class
# TODO: add `set_name` function in entity, so you can change an entity's type but keep its metadata
# TODO: value check everything
# TODO: make entity positions correct when rotating entities

# TODO: think about getters and setters:
# using entity.value = whatever is more succinct than entity.set_value(whatever)
# (except in the cases where we want more utility, like with control_behavior)
# However, we keep the error / warning checking in the setters to make them useful

# TODO: refine control_behavior, shit is unweildly and unintuitive
# TODO: add rail grid placing, add warnings/errors for rails that are placed an odd number of tiles apart
# in fact, a rails and rail entities have a whole lot of extra rules that need to be accounted for

from factoriotools.errors import (
    InvalidEntityID, InvalidItemID, InvalidSignalID, 
    InvalidArithmeticOperation, InvalidConditionOperation
)
from factoriotools.signals import Signal, item_signals, signal_dict#, get_signal_type
from factoriotools.entity_data import entity_dimensions

import copy
from enum import IntEnum
from typing import Any, Union, Callable

class ReadMode(IntEnum):
    PULSE = 0
    HOLD = 1

class ModeOfOperation(IntEnum):
    ENABLE_DISABLE = 0
    SET_FILTERS = 1
    NONE = 3

# from entity_data import *

containers = {
    "wooden-chest", "iron-chest", "steel-chest", "logistic-chest-buffer", 
    "logisitics-chest-passive-provider", "logistics-chest-active-provider"
}

storage_tanks = {
    "storage-tank"
}

transport_belts = {
    "transport-belt", "fast-transport-belt", "express-transport-belt"
}

underground_belts = {
    "underground-belt", "fast-underground-belt", "express-underground-belt"
}

splitters = {
    "splitter", "fast-splitter", "express-splitter"
}

inserters = {
    "burner-inserter", "inserter", "long-handed-inserter", "fast-inserter",
    "stack-inserter"
}

filter_inserters = {
    "filter-inserter", "stack-filter-inserter"
}

loaders = {
    "loader", "fast-loader", "express-loader"
} # No vanilla loaders that arent hidden

electric_poles = {
    "small-electric-pole", "medium-electric-pole", "big-electric-pole", 
    "substation"
}

pipes = {
    "pipe"
}

underground_pipes = {
    "pipe-to-ground"
}

pumps = {
    "pump"
}

straight_rails = {
    "straight-rail"
}

curved_rails = {
    "curved-rail"
}

train_stops = {
    "train-stop"
}

rail_signals = {
    "rail-signal", "rail-chain-signal"
}

locomotives = {
    "locomotive"
}

cargo_wagons = {
    "cargo-wagon"
}

fluid_wagons = {
    "fluid-wagon"
}

artillery_wagons = {
    "artillery-wagon"
}

logistic_containers = {
    "logistics-chest-requester", "logistics-chest-storage"
}

roboports = {
    "roboports"
}

lamps = {
    "small-lamp"
}

arithmetic_combinators = {
    "arithmetic-combinator"
}

decider_combinators = {
    "decider-combinator"
}

constant_combinators = {
    "constant-combinator"
}

power_switches = {
    "power-switch"
}

programmable_speakers = {
    "programmable-speaker"
}

boilers = {
    "boiler", "heat-exchanger"
}

generators = {
    "steam-engine", "steam-turbine"
}

solar_panels = {
    "solar-panel"
}

accumulators = {
    "accumulator"
}

reactors = {
    "nuclear-reactor"
}

mining_drills = {
    "burner-mining-drill", "electric-mining-drill", "pumpjack"
}

offshore_pumps = {
    "offshore-pump"
}

furnaces = {
    "stone-furnace", "steel-furnace", "electric-furnace"
}

assembling_machines = {
    "assembling-machine-1", "assembling-machine-2", "assembling-machine-3",
    "chemical-plant", "oil-refinery", "centrifuge"
}

labs = {
    "lab"
}

beacons = {
    "beacon"
}

rocket_silos = {
    "rocket-silo"
}

land_mines = {
    "land-mine"
}

walls = {
    "stone-wall"
}

gates = {
    "gates"
}

ammo_turrets = {
    "gun-turret"
}

electric_turrets = {
    "laser-turret"
}

radars = {
    "radar"
}

# Mixins!
# TODO: organize
class Entity:
    def __init__(self, name: str, position: Union[list, dict] = [0, 0], **kwargs):
        # What do all entities have in common?
        # No id, because that's blueprint specific
        #if "id" in kwargs: 
        #    self.id = kwargs["id"]    # id, potentially

        # Create a set of keywords that transfer in to_dict function
        # Since some things we want to keep internal without sending to to_dict
        self.exports = dict()
        # Name (External)
        self.name = name 
        self._add_export("name")

        # Width and Height (Internal)
        # TODO: change this to AABB
        self.width, self.height = entity_dimensions[name]

        # Power connectable? (Internal) (Overwritten by mixin if applicable)
        self.power_connectable = False

        # Circuit connectable? (Interal) (Overwritten by mixin if applicable)
        self.circuit_connectable = False

        # Entity number (External) (only modified in Blueprint functions)
        #self.entity_number = None
        #self._add_export("entity_number", lambda x: x is not None)

        # (Absolute) Position (External)
        if isinstance(position, list):
            self.set_grid_position(position[0], position[1])
        elif isinstance(position, dict):
            self.set_absolute_position(position["x"], position["y"])
        self._add_export("position")

        # Grid Position (Internal)
        if "grid_position" in kwargs:
            grid_position = kwargs["grid_position"]
            self.set_grid_position(grid_position[0], grid_position[1])

        # Tags (External)
        self.tags = {}
        if "tags" in kwargs:
            self.tags = kwargs["tags"]
        self._add_export("tags", lambda x: x)

        # What can they have optionally?
        # orientation
        # inventory (Cargo wagon contents configuration)
        # infinity_settings 
        # input_priority (left or right?)
        # output_priority (left or right?)
        # filters (for inserters)
        # override_stack_size
        # drop_position (inserter)
        # pickup_position (inserter)
        # request_filters
        # request_from_buffers (boolean)
        # parameters (programmable speaker)
        # alert_parameters (programmable speaker)
        # auto_launch (with cargo, rocket silo)
        # variation
        # color (train station most normally, maybe other things)
        # station (name of the train station if train stop)

    def set_absolute_position(self, x: float, y: float) -> None:
        """
        Sets the position of the object, or the position that Factorio uses. On
        most entities, the position of the object is located at the center.
        """
        self.position = {"x": x, "y": y}

    def set_grid_position(self, x: int, y: int) -> None:
        """
        Sets the grid position of the object, or the tile coordinates of the
        object. Calculates the absolute position based off of the dimensions of
        the entity. If a tile is multiple tiles in width or height, the grid
        coordinate is the top left-most tile of the entity.
        """
        absolute_x = x + self.width / 2.0
        absolute_y = y + self.height / 2.0
        self.set_absolute_position(absolute_x, absolute_y)

    def set_tags(self, tags: dict) -> None:
        """
        """
        self.tags = tags

    def set_tag(self, tag: str, value: Any) -> None:
        """
        """
        self.tags[tag] = value

    def get_center(self) -> dict:
        pass

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
            try:
                # Try and get the element
                value = dict_self[name]
            except:
                continue
            # Does the value match the criteria to be included?
            if f is None or f(value):
                out[name] = value

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
        self.bar = None
        if "bar" in kwargs:
            self.set_bar_index(kwargs["bar"])
        self._add_export("bar", lambda x: x is not None)

    def set_bar_index(self, position: int) -> None:
        """
        Sets the inventory limiting bar.
        """
        self.bar = position


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

    def set_inventory(self, configuration: dict) -> None:
        """
        Sets the entire inventory configuration for the cargo wagon.
        """
        # Validate filter schema
        # TODO
        self.inventory = configuration

    def set_inventory_filter(self, index: int, name: str) -> None:
        """
        Sets the item filter at location `index` to `name`. If `name` is set to
        `None` the item filter at that location is removed.
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
                    self.inventory["filters"][i] = {"index": index,"name": name}
                    
                return

        # If no entry with the same index was found
        self.inventory["filters"].append({"index": index, "name": name})
            

    def set_bar(self, index: int) -> None:
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
    Gives an entity a type, which can either be 'input' or 'output'. Used on
    underground belts and loaders.
    """
    def __init__(self, name: str, **kwargs):
        super().__init__(name, **kwargs)
        self.type = "input" # Default
        if "type" in kwargs:
            self.set_io_type(kwargs["type"])
        self._add_export("type", lambda x: x is not None)

    def set_io_type(self, type: str):
        """
        Sets whether or not this entity is configured as 'input' or 'output';
        used on underground belts and loaders.
        """
        if type == "input" or type == "output":
            self.type = type
        else:
            raise ValueError("'type' must be one of 'input' or 'output'")


class PowerConnectableMixin:
    def __init__(self, name: str, **kwargs):
        super().__init__(name, **kwargs)
        self.power_connectable = True
        self.neighbours = []
        if "neighbours" in kwargs:
            self.neighbours = kwargs["neighbours"]
        self._add_export("neighbours", lambda x: len(x) != 0)

    def add_power_connection(self, target_id: Union[int, str]) -> None:
        """
        Adds a power wire between this entity and another power-connectable one.
        """
        # TODO: raise error if target_id is not power connectable?
        if target_id not in self.neighbours:
            self.neighbours.append(target_id)

    def remove_power_connection_point(self, target_id: Union[int, str]) -> None:
        pass # TODO


class CircuitConnectableMixin:
    """
    Enables the entity to be connected to circuit networks.
    """
    def __init__(self, name: str, **kwargs):
        super().__init__(name, **kwargs)
        self.circuit_connectable = True
        self.connections = {}
        if "connections" in kwargs:
            self.connections = kwargs["connections"]
        self._add_export("connections", lambda x: len(x) != 0)

    def add_circuit_connection(self, other_entity: Entity, target_num: int, color: str, source_side: int = 1, target_side: int = 1) -> None:
        """
        Adds a connection between this entity and `other_entity`

        NOTE: this function only modifies the current entity; for completeness
        you should also connect the other entity to this one.
        """
        if str(source_side) not in self.connections:
            self.connections[str(source_side)] = dict()
        current_side = self.connections[str(source_side)]

        if color not in current_side:
            current_side[color] = list()
        current_color = current_side[color]

        # For most entities you dont need a target_side
        entry = {"entity_id": target_num}
        # However, for dual connection point targets you do
        if other_entity.name in arithmetic_combinators or \
           other_entity.name in decider_combinators:
            entry = {"entity_id": target_num, "circuit_id": target_side}

        current_color.append(entry)

    def remove_circuit_connection(self):
        """
        """
        pass # TODO
        

class ControlBehaviorMixin:
    """
    Enables the entity to specify control behavior.
    """
    def __init__(self, name: str, **kwargs):
        super().__init__(name, **kwargs)

        self.control_behavior = {}
        if "control_behavior" in kwargs:
            self.set_control_behavior(kwargs["control_behavior"])

        self._add_export("control_behavior", lambda x: len(x) != 0)

    def set_control_behavior(self, data: dict):
        self.control_behavior = data
        # Convert signals from string do dict representation
        #self._convert_signals()
        # Validate that they match using a schema
        #CONTROL_BEHAVIOR_SCHEMA.validate(self.control_behavior)

    def _normalize_control_behavior(self) -> None:
        """
        Unified function for rectifying ease of use format to strict blueprint
        format.
        """
        pass # TODO


class CircuitConditionMixin: # (ControlBehaviorMixin)
    """
    Allows the Entity to have an circuit enable condition. Used in Pumps, 
    Inserters, Belts, etc.
    """
    def __init__(self, name: str, **kwargs):
        super().__init__(name, **kwargs)

        self.control_behavior = {}
        if "control_behavior" in kwargs:
            self.control_behavior = kwargs["control_behavior"]
            # Convert signals from string do dict representation, if necessary
            self._normalize_circuit_condition()
        self._add_export("control_behavior", lambda x: len(x) != 0)

    def set_enabled_condition(self, a = None, op = "<", b = 0):
        self.control_behavior["circuit_condition"] = {}
        # Check the inputs
        # A
        if a is None:
            pass # Keep the first signal empty
        elif isinstance(a, str):
            self.control_behavior["circuit_condition"]["first_signal"] = a
        elif isinstance(a, int):
            raise TypeError("'circuit_conditions' cannot have a constant first")
        else:
            raise TypeError("First param is neither 'str', 'int' or 'None'")
        
        # op
        valid_comparisons =  [">", "<", "=", ">=", "<=", "!="]
        if op not in valid_comparisons:
            raise InvalidConditionOperation(op)
        self.control_behavior["circuit_condition"]["comparator"] = op

        # B
        if isinstance(b, str):
            self.control_behavior["circuit_condition"]["second_signal"] = b
        elif isinstance(b, int):
            self.control_behavior["circuit_condition"]["constant"] = b
        else:
            raise TypeError("Second param is neither 'str' or 'int'")

        self._normalize_circuit_condition()

    def remove_enabled_condition(self):
        """
        """
        self.control_behavior.pop("circuit_condition", None)

    def set_enable_disable(self, value: bool) -> None:
        """
        """
        self.control_behavior["circuit_enable_disable"] = value

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

        print(self.control_behavior)


class CircuitReadHandMixin: # (ControlBehaviorMixin)
    def __init__(self, name: str, **kwargs):
        super().__init__(name, **kwargs)

    def set_read_hand_contents(self, value: bool) -> None:
        """
        """
        self.control_behavior["circuit_read_hand_contents"] = value

    def set_read_mode(self, mode: ReadMode):
        """
        """
        self.control_behavior["circuit_hand_read_mode"] = mode


class StackSizeMixin: # (ControlBehaviorMixin)
    """
    """
    def __init__(self, name: str, **kwargs):
        super().__init__(name, **kwargs)
        self.override_stack_size = None
        if "override_stack_size" in kwargs:
            self.set_stack_size_override(kwargs["override_stack_size"])
        self._add_export("override_stack_size", lambda x: x is not None)

        self._normalize_stack_signal()

    def set_stack_size_override(self, stack_size: int):
        """
        Sets an inserter's stack size override.
        """
        # TODO: error checking
        self.override_stack_size = stack_size

    def set_circuit_stack_size(self, enabled: bool):
        """
        Set if the inserter's stack size is controlled by circuit signal.
        """
        # TODO: error checking
        if enabled is None:
            self.control_behavior.pop("circuit_set_stack_size", None)
        else:
            self.control_behavior["circuit_set_stack_size"] = enabled

    def set_stack_control_signal(self, signal: str):
        """
        Specify the stack size input signal for the inserter if enabled.
        """
        # TODO: error checking
        if signal is None:
            self.control_behavior.pop("stack_control_input_signal")
        else:
            self.control_behavior["stack_control_input_signal"] = signal
            self._normalize_stack_signal()

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
        # TODO: error checking
        if mode is None or mode == ModeOfOperation.ENABLE_DISABLE:
            self.control_behavior.pop("circuit_mode_of_operation", None)
        else:
            self.control_behavior["circuit_mode_of_operation"] = mode

class FiltersMixin:
    def __init__(self, name: str, **kwargs):
        super().__init__(name, **kwargs)

        self.filters = None # maybe [] instead? which one is clearer?
        if "filters" in kwargs:
            self.set_item_filters(kwargs["filters"])
        self._add_export("filters", lambda x: x is not None)

    def set_item_filters(self, filters: list):
        """
        Sets the item filters for the inserter or loader.
        """
        # TODO: make sure the items are item signals
        if filters is not None:
            for item in filters:
                if item not in item_signals:
                    raise InvalidItemID(item)

        #self._convert_filters()
        #formatted = []
        for i in range(len(filters)):
            filters[i] = {"index": i + 1, "name": filters[i]}
        self.filters = filters

    def set_item_filter(self, index: int, item: str) -> None:
        pass # TODO


class RecipeMixin:
    def __init__(self, name: str, **kwargs):
        super().__init__(name, **kwargs)
        self.recipe = None
        if "recipe" in kwargs:
            self.set_recipe(kwargs["recipe"])
        self._add_export("recipe", lambda x: x is not None)

    def set_recipe(self, recipe: str):
        # if recipe not in recipe_names:
        #     raise InvalidRecipeID(recipe)
        self.recipe = recipe


class RequestFiltersMixin:
    """
    """
    def __init__(self, name: str, **kwargs):
        super().__init__(name, **kwargs)
        request_filters = None
        if "request_filters" in kwargs:
            self.set_request_filters(kwargs["request_filters"])
        self._add_export("request_filters", lambda x: x is not None)

    def set_request_filters(self, test):
        """
        """
        # TODO
        pass


class ItemRequestMixin: # is this redundant?
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

    def set_item_requests(self, items: dict):
        for name, amount in items.items():
            self.set_item_request(name, amount)

    def set_item_request(self, item, amount):
        if item not in item_signals:
            raise InvalidSignalID(item)
        self.items[item] = amount

    def remove_item_request(self, item):
        del self.items[item]


################################################################################


class Container(CircuitConnectableMixin, InventoryMixin, Entity):
    """
    * `wooden-chest`
    * `iron-chest`
    * `steel-chest`
    * `logistic-chest-buffer`
    * `logistic-chest-active-provider`
    * `logistic-chest-passive-provider`
    """
    def __init__(self, name: str, **kwargs):
        if name not in containers:
            raise InvalidEntityID("'{}' is not a valid name for this type".format(name))
        super(Container, self).__init__(name, **kwargs)


class StorageTank(CircuitConnectableMixin, Entity):
    """
    """
    def __init__(self, name: str, **kwargs):
        if name not in storage_tanks:
            raise InvalidEntityID("'{}' is not a valid name for this type".format(name))
        super(StorageTank, self).__init__(name, **kwargs)


class TransportBelt(CircuitReadHandMixin, CircuitConditionMixin, ControlBehaviorMixin, CircuitConnectableMixin, DirectionalMixin, Entity):
    def __init__(self, name: str, **kwargs):
        if name not in transport_belts:
            raise InvalidEntityID("'{}' is not a valid name for this type".format(name))
        super(TransportBelt, self).__init__(name, **kwargs)


class UndergroundBelt(IOTypeMixin, DirectionalMixin, Entity):
    """
    """
    def __init__(self, name: str, **kwargs):
        if name not in underground_belts:
            raise InvalidEntityID("'{}' is not a valid name for this type".format(name))
        super(UndergroundBelt, self).__init__(name, **kwargs)


class Splitter(ControlBehaviorMixin, CircuitConnectableMixin, DirectionalMixin, Entity):
    """
    """
    def __init__(self, name: str, **kwargs):
        if name not in splitters:
            raise InvalidEntityID("'{}' is not a valid name for this type".format(name))
        super(Splitter, self).__init__(name, **kwargs)

        self.input_priority = None
        if "input_priority" in kwargs:
            self.set_input_priority(kwargs["input_priority"])
        self._add_export("input_priority", lambda x: x is not None)

        self.output_priority = None
        if "output_priority" in kwargs:
            self.set_output_priority(kwargs["output_priority"])
        self._add_export("output_priority", lambda x: x is not None)

        self.filter = None
        if "filter" in kwargs:
            self.set_filter(kwargs["filter"])
        self._add_export("filter", lambda x: x is not None)

    def set_filter(self, item: str) -> None:
        """
        Sets the Splitter's filter to `item`. Default output side is left.
        """
        # TODO: uncomment
        # if item not in items:
        #     raise ValueError("'{}' is not a valid item name".format(item))

        self.filter = item

    def set_input_priority(self, side: str) -> None:
        """
        Sets the Splitter's input priority to either 'left' or 'right'.
        """
        if side not in {"left", "right", None}:
            raise ValueError("'{}' is not a valid input side".format(side))

        self.input_priority = side

    def set_output_priority(self, side: str) -> None:
        """
        Sets the Splitter's output priority to either 'left' or 'right'.
        """
        if side not in {"left", "right", None}:
            raise ValueError("'{}' is not a valid input side".format(side))

        self.output_priority = side


class Inserter(StackSizeMixin, CircuitReadHandMixin, ModeOfOperationMixin, CircuitConditionMixin, ControlBehaviorMixin, CircuitConnectableMixin, DirectionalMixin, Entity):
    """
    """
    def __init__(self, name: str, **kwargs):
        if name not in inserters:
            raise InvalidEntityID("'{}' is not a valid name for this type".format(name))
        super(Inserter, self).__init__(name, **kwargs)


class FilterInserter(FiltersMixin, StackSizeMixin, CircuitReadHandMixin, ModeOfOperationMixin, CircuitConditionMixin, ControlBehaviorMixin, CircuitConnectableMixin, DirectionalMixin, Entity):
    def __init__(self, name: str, **kwargs):
        if name not in filter_inserters:
            raise InvalidEntityID("'{}' is not a valid name for this type".format(name))
        super(FilterInserter, self).__init__(name, **kwargs)

        self.filter_mode = None
        if "filter_mode" in kwargs:
            self.set_filter_mode(kwargs["filter_mode"])
        self._add_export("filter_mode", lambda x: x is not None)

    def set_filter_mode(self, mode: str) -> None:
        """
        Sets the filter mode to either 'whitelist' or 'blacklist'.
        """
        if mode not in {"whitelist", "blacklist", None}:
            raise ValueError("'{}' is not a valid filter mode".format(mode))

        self.filter_mode = mode


class Loader(FiltersMixin, IOTypeMixin, DirectionalMixin, Entity):
    def __init__(self, name: str, **kwargs):
        if name not in loaders:
            raise InvalidEntityID("'{}' is not a valid name for this type".format(name))
        super(Loader, self).__init__(name, **kwargs)


class ElectricPole(CircuitConnectableMixin, PowerConnectableMixin, Entity):
    def __init__(self, name: str, **kwargs):
        if name not in electric_poles:
            raise InvalidEntityID("'{}' is not a valid name for this type".format(name))
        super(ElectricPole, self).__init__(name, **kwargs)


class Pipe(Entity):
    def __init__(self, name: str, **kwargs):
        if name not in pipes:
            raise InvalidEntityID("'{}' is not a valid name for this type".format(name))
        super(Pipe, self).__init__(name, **kwargs)


class UndergroundPipe(DirectionalMixin, Entity):
    def __init__(self, name: str, **kwargs):
        if name not in underground_pipes:
            raise InvalidEntityID("'{}' is not a valid name for this type".format(name))
        super(UndergroundPipe, self).__init__(name, **kwargs)


class Pump(CircuitConditionMixin, CircuitConnectableMixin, DirectionalMixin, Entity):
    def __init__(self, name: str, **kwargs):
        if name not in pumps:
            raise InvalidEntityID("'{}' is not a valid name for this type".format(name))
        super(Pump, self).__init__(name, **kwargs)


class StraightRail(EightWayDirectionalMixin, Entity):
    def __init__(self, name: str, **kwargs):
        if name not in straight_rails:
            raise InvalidEntityID("'{}' is not a valid name for this type".format(name))
        super(StraightRail, self).__init__(name, **kwargs)


class CurvedRail(EightWayDirectionalMixin, Entity):
    def __init__(self, name: str, **kwargs):
        if name not in curved_rails:
            raise InvalidEntityID("'{}' is not a valid name for this type".format(name))
        super(CurvedRail, self).__init__(name, **kwargs)


class TrainStop(EightWayDirectionalMixin, Entity):
    pass


class RailSignal(EightWayDirectionalMixin, Entity):
    pass


class Locomotive(OrientationMixin, Entity):
    def __init__(self, name: str, **kwargs):
        if name not in locomotives:
            raise InvalidEntityID("'{}' is not a valid name for this type".format(name))
        super(Locomotive, self).__init__(name, **kwargs)


class CargoWagon(InventoryFilterMixin, OrientationMixin, Entity):
    def __init__(self, name: str, **kwargs):
        if name not in cargo_wagons:
            raise InvalidEntityID("'{}' is not a valid name for this type".format(name))
        super(CargoWagon, self).__init__(name, **kwargs)


class FluidWagon(OrientationMixin, Entity):
    def __init__(self, name: str, **kwargs):
        if name not in fluid_wagons:
            raise InvalidEntityID("'{}' is not a valid name for this type".format(name))
        super(FluidWagon, self).__init__(name, **kwargs)


class ArtilleryWagon(OrientationMixin, Entity):
    def __init__(self, name: str, **kwargs):
        if name not in artillery_wagons:
            raise InvalidEntityID("'{}' is not a valid name for this type".format(name))
        super(ArtilleryWagon, self).__init__(name, **kwargs)


class LogisticsRequestContainer(RequestFiltersMixin, CircuitConnectableMixin, InventoryMixin, Entity):
    def __init__(self, name: str, **kwargs):
        if name not in logistic_containers:
            raise InvalidEntityID("'{}' is not a valid name for this type".format(kwargs["name"]))
        super().__init__(name, **kwargs)


class Roboport(CircuitConnectableMixin, InventoryMixin, Entity): # FIXME InventoryMixin
    pass


class Lamp(CircuitConnectableMixin, Entity):
    pass


class ArithmeticCombinator(ControlBehaviorMixin, CircuitConnectableMixin, DirectionalMixin, Entity):
    def __init__(self, name: str, **kwargs):
        if name not in arithmetic_combinators:
            raise InvalidEntityID("'{}' is not a valid name for this type".format(kwargs["name"]))
        super().__init__(name, **kwargs)

    def set_arithmetic_conditions(self, a: Union[str, int] = None, op: str = "*", b: Union[str, int] = 0, out: str = None):
        self.control_behavior["arithmetic_conditions"] = {}
        arithmetic_conditions = self.control_behavior["arithmetic_conditions"]
        # TODO: error checking
        # A
        if a is None:
            pass # Default
        elif isinstance(a, str):
            arithmetic_conditions["first_signal"] = a
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
        arithmetic_conditions["comparator"] = op.upper()

        # B
        if isinstance(b, str):
            arithmetic_conditions["second_signal"] = b
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
        self.control_behavior.pop("arithmetic_conditions", None)


class DeciderCombinator(ControlBehaviorMixin, CircuitConnectableMixin, DirectionalMixin, Entity):
    def __init__(self, name: str, **kwargs):
        if name not in decider_combinators:
            raise InvalidEntityID("'{}' is not a valid name for this type".format(name))
        super(DeciderCombinator, self).__init__(name, **kwargs)
    
    def set_decider_conditions(self, a, op, b):
        """
        """
        pass # TODO

    def remove_decider_conditions(self):
        """
        """
        self.control_behavior.pop("decider_conditions", None)


class ConstantCombinator(ControlBehaviorMixin, CircuitConnectableMixin, DirectionalMixin, Entity):
    """
    TODO: maybe keep signal filters internally as an array of Signal objects,
    and then use Signal.to_dict() during that stage?
    """
    def __init__(self, name: str, **kwargs):
        if name not in constant_combinators:
            raise InvalidEntityID("'{}' is not a valid name for this type".format(name))
        super(ConstantCombinator, self).__init__(name, **kwargs)

    def set_signal(self, index: int, name: str, count: int = 0) -> None:
        """
        """
        if "filters" not in self.control_behavior:
            self.control_behavior["filters"] = []
        
        # TODO: error checking
        
        # Check to see if filters already contains an entry with the same index
        for i, filter in enumerate(self.control_behavior["filters"]):
            if index == filter["index"]: # Index already exists in the list
                if name is None: # Delete the entry
                    del self.inventory["filters"][i]
                else: # Set the new value
                    self.inventory["filters"][i] = {
                        "index": index + 1,"name": name, "count": count
                    }

                return

        # If no entry with the same index was found
        self.control_behavior["filters"].append({
            "index": index + 1, "name": name, "count": count
        })

    def get_signal(self, index: int) -> Signal:
        """
        """
        return None # TODO

    def clear_signals(self) -> None:
        """
        Clears all signals in the constant combinator, if any are present.
        """
        self.control_behavior.pop("filters", None)


class PowerSwitch(CircuitConnectableMixin, PowerConnectableMixin, Entity):
    pass


class ProgrammableSpeaker(CircuitConnectableMixin, Entity):
    pass


class Boiler(DirectionalMixin):
    pass


class Generator(Entity):
    pass


class SolarPanel(Entity):
    pass


class Accumulator(Entity):
    pass


class Reactor(Entity):
    pass


class HeatPipe(Entity):
    pass


class MiningDrill(DirectionalMixin, Entity):
    pass


class OffshorePump(DirectionalMixin, Entity):
    pass


class Furnace(Entity):
    pass


class AssemblingMachine(ItemRequestMixin, RecipeMixin, Entity):
    def __init__(self, **kwargs):
        if kwargs["name"] not in assembling_machines:
            raise InvalidEntityID("'{}' is not a valid name for this type".format(kwargs["name"]))
        super(AssemblingMachine, self).__init__(**kwargs)


class Lab(Entity):
    pass


class Beacon(Entity):
    pass


class RocketSilo(Entity):
    pass


class LandMine(Entity):
    pass


# Technically CircuitConnectable, but only when adjacent to a gate
class Wall(CircuitConnectableMixin, Entity):
    pass


class Gate(CircuitConnectableMixin, Entity):
    pass


class Turret(DirectionalMixin, Entity):
    pass


class Radar(Entity):
    pass


def new_entity(name: str, **kwargs):
    #kwargs["name"] = name # TODO: see if we can get rid of this
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
    if name in locomotives:
        return Locomotive(name, **kwargs)
    if name in cargo_wagons:
        return CargoWagon(name, **kwargs)
    if name in fluid_wagons:
        return FluidWagon(name, **kwargs)
    if name in artillery_wagons:
        return ArtilleryWagon(name, **kwargs)
    if name in logistic_containers:
        return LogisticsRequestContainer(name, **kwargs)
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
    if name in assembling_machines:
        return AssemblingMachine(name, **kwargs)
    
    raise InvalidEntityID(name)