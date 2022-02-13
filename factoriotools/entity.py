# entity.py

# TODO: handle the difference between grid position and absolute position
# TODO: create verification for the initial load of an entity by making a schema for each entity class
# TODO: add `set_name` function in entity, so you can change an entity's type but keep its metadata
# TODO: value check everything

from typing import Any, Callable
from factoriotools.errors import (
    InvalidEntityID, InvalidSignalID, InvalidCircuitOperation
)
from factoriotools.signals import get_signal_type, item_signals
from factoriotools.entity_data import entity_dimensions

PULSE = 0
HOLD = 1

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

train_cars = {
    "locomotive", "cargo-wagon", "fluid-wagon", "artillery-wagon"
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
class DirectionalMixin:
    """ 
    Enables entities to be rotated. 
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.direction = 0
        if "direction" in kwargs:
            self.set_direction(kwargs["direction"])
        
        self._add_export("direction", lambda x: x != 0)

    def set_direction(self, direction: int) -> None:
        self.direction = direction

class EightWayDirectionalMixin:
    pass

class OrientationMixin:
    """ Used in trains to specify their direction. """
    def __init__(self, **kwargs):
        pass # TODO

    def set_orientation(self, orientation: float) -> None:
        self.orientation = orientation

class InventoryMixin:
    """
    Enables the entity to have inventory control.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bar = None
        if "bar" in kwargs:
            self.set_bar_index(kwargs["bar"])
        self._add_export("bar", lambda x: x is not None)

    def set_bar_index(self, position: int):
        """
        """
        self.bar = position

class InventoryFilterMixin:
    """
    Allows inventories to set content filters. Used in cargo wagons.
    """
    pass

class IOTypeMixin:
    """
    Gives an entity a type, which can either be 'input' or 'output'. Used on
    underground belts and loaders.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.type = "input" # Default
        if "type" in kwargs:
            self.type = kwargs["type"]
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
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.neighbours = []
        if "neighbours" in kwargs:
            self.neighbours = kwargs["neighbours"]
        self._add_export("neighbours", lambda x: len(x) != 0)

    def add_power_connection_point(self, target_id: int):
        """
        Adds a power wire between this entity and another power-connectable one.
        """
        pass # TODO

class CircuitConnectableMixin:
    """
    Enables the entity to be connected to circuit networks.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.circuit_connectable = True
        self.connections = {}
        if "connections" in kwargs:
            self.connections = kwargs["connections"]
        self._add_export("connections", lambda x: len(x) != 0)

    def add_circuit_connection_point(self, color: str, source_side: int, target_name: str, target_num: int, target_side: int = 1) -> None:
        """
        Constructs the `connections` dictionary in proper format for this 
        entity.

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
        if target_name in arithmetic_combinators or target_name in decider_combinators:
            entry = {"entity_id": target_num, "circuit_id": target_side}

        current_color.append(entry)
        

class ControlBehaviorMixin:
    """
    Enables the entity to specify control behavior.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.control_behavior = {}
        if "control_behavior" in kwargs:
            self.control_behavior = kwargs["control_behavior"]
            # Convert signals from string do dict representation, if necessary
            self._convert_signals()

        self._add_export("control_behavior", lambda x: len(x) != 0)

    def set_control_behavior(self, data: dict):
        self.control_behavior = data
        # Convert signals from string do dict representation
        self._convert_signals()

    # def set_circuit_condition(self, **kwargs):
    #     if "circuit_condition" not in self.control_behavior:
    #         self.control_behavior["circuit_condition"] = {}
    #     for k, v in kwargs.items():
    #         self.control_behavior["circuit_condition"][k] = v
    #     self._convert_signals()

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
            raise InvalidCircuitOperation(op)
        self.control_behavior["circuit_condition"]["comparator"] = op

        # B
        if isinstance(b, str):
            self.control_behavior["circuit_condition"]["second_signal"] = b
        elif isinstance(b, int):
            self.control_behavior["circuit_condition"]["constant"] = b
        else:
            raise TypeError("Second param is neither 'str' or 'int'")

        self._convert_signals()


    def set_enable_disable(self, value: bool) -> None:
        """
        """
        self.control_behavior["circuit_enable_disable"] = value

    def set_read_hand_contents(self, value: bool) -> None:
        """
        """
        self.control_behavior["circuit_read_hand_contents"] = value

    def set_read_mode(self, mode: int):
        """
        """
        self.control_behavior["circuit_contents_read_mode"] = mode

    def _convert_signals(self) -> None:
        """
        """
        if "circuit_condition" in self.control_behavior:
            circuit_condition = self.control_behavior["circuit_condition"]
            if "first_signal" in circuit_condition:
                # If its a string, change it, otherwise treat it as gospel
                if isinstance(circuit_condition["first_signal"], str):
                    name = circuit_condition["first_signal"]
                    circuit_condition["first_signal"] = {
                        "name": name,
                        "type": get_signal_type(name)
                    }
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
                    circuit_condition["second_signal"] = {
                        "name": name,
                        "type": get_signal_type(name)
                    }


class RequestFiltersMixin:
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if "request_filters" in kwargs:
            self.set_request_filters(kwargs["request_filters"])

    def set_request_filters(self, test):
        pass

class CircuitConditionMixin:
    pass

class ReadHandMixin:
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def set_read_hand(self, value: bool) -> None:
        pass

    def set_read_hand_mode(self, mode: int) -> None:
        pass

class StackSizeMixin:
    pass

class FilterMixin:
    pass

class RecipeMixin:
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.recipe = None
        if "recipe" in kwargs:
            self.set_recipe(kwargs["recipe"])
        self._add_export("recipe", lambda x: x is not None)

    def set_recipe(self, recipe: str):
        # if recipe not in recipe_names:
        #     raise InvalidRecipeID(recipe)
        self.recipe = recipe

class ItemRequestMixin:
    """
    NOTE: this is for module requests and stuff like that, not logistics!

    Think an assembling machine that needs speed modules inside of it
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
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


class Entity:
    def __init__(self, name: str, position: list = [0, 0], **kwargs):
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
        # Entity number (External) (only modified in Blueprint functions)
        self.entity_number = None
        self._add_export("entity_number", lambda x: x is not None)
        # (Absolute) Position (External)
        if isinstance(position, list):
            self.set_absolute_position(position[0], position[1])
        elif isinstance(position, dict):
            self.set_absolute_position(position["x"], position["y"])
        self._add_export("position")
        # Grid Position (Internal)
        if "grid_position" in kwargs:
            grid_position = kwargs["grid_position"]
            self.set_grid_position(grid_position[0], grid_position[1])
        # Width and Height (Internal)
        self.width, self.height = entity_dimensions[name]
        # Tags (External)
        self.tags = {}
        if "tags" in kwargs:
            self.tags = kwargs["tags"]
        self._add_export("tags", lambda x: x)

        # What can they have optionally?
        # direction
        # orientation
        # connections
        # control_behavior
        # items (requests)
        # recipe (that an assembling machine is set to)
        # bar (inventory limiter X)
        # inventory (Cargo wagon contents configuration)
        # infinity_settings 
        # type (underground input or output?)
        # input_priority (left or right?)
        # output_priority (left or right?)
        # filter (for splitter)
        # filters (for inserters)
        # filter_mode (whitelist or blacklist)
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
        """
        self.position = {"x": x, "y": y}

    def set_grid_position(self, x: int, y: int) -> None:
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

    def __repr__(self):
        return "<Entity>" + str(self.to_dict())


class Container(CircuitConnectableMixin, InventoryMixin, Entity):
    """
    * `wooden-chest`
    * `iron-chest`
    * `steel-chest`
    * `logistic-chest-buffer`
    * `logistic-chest-active-provider`
    * `logistic-chest-passive-provider`
    """
    def __init__(self, **kwargs):
        if kwargs["name"] not in containers:
            raise InvalidEntityID("'{}' is not a valid name for this type".format(kwargs["name"]))
        super(Container, self).__init__(**kwargs)


class StorageTank(CircuitConnectableMixin, Entity):
    """
    """
    def __init__(self, **kwargs):
        if kwargs["name"] not in storage_tanks:
            raise InvalidEntityID("'{}' is not a valid name for this type".format(kwargs["name"]))
        super(StorageTank, self).__init__(**kwargs)


class TransportBelt(ControlBehaviorMixin, CircuitConnectableMixin, DirectionalMixin, Entity):
    def __init__(self, **kwargs):
        if kwargs["name"] not in transport_belts:
            raise InvalidEntityID("'{}' is not a valid name for this type".format(kwargs["name"]))
        super(TransportBelt, self).__init__(**kwargs)


class UndergroundBelt(IOTypeMixin, DirectionalMixin, Entity):
    def __init__(self, **kwargs):
        if kwargs["name"] not in underground_belts:
            raise InvalidEntityID("'{}' is not a valid name for this type".format(kwargs["name"]))
        super(UndergroundBelt, self).__init__(**kwargs)


class Splitter(ControlBehaviorMixin, CircuitConnectableMixin, DirectionalMixin, Entity):
    pass


class Inserter(StackSizeMixin, ControlBehaviorMixin, CircuitConnectableMixin, DirectionalMixin, Entity):
    def __init__(self, **kwargs):
        if kwargs["name"] not in inserters:
            raise InvalidEntityID("'{}' is not a valid name for this type".format(kwargs["name"]))
        super(Inserter, self).__init__(**kwargs)


class FilterInserter(FilterMixin, StackSizeMixin, ControlBehaviorMixin, CircuitConnectableMixin, DirectionalMixin, Entity):
    def __init__(self, **kwargs):
        if kwargs["name"] not in filter_inserters:
            raise InvalidEntityID("'{}' is not a valid name for this type".format(kwargs["name"]))
        super(FilterInserter, self).__init__(**kwargs)


class Loader(DirectionalMixin, Entity):
    pass


class ElectricPole(CircuitConnectableMixin, PowerConnectableMixin, Entity):
    pass


class Pipe(CircuitConnectableMixin, Entity):
    pass


class UndergroundPipe(DirectionalMixin, Entity):
    pass


class Pump(DirectionalMixin, Entity):
    pass

# Do we need StraightRail and CurvedRail or can it be just Rail?
class StraightRail(EightWayDirectionalMixin, Entity):
    pass


class CurvedRail(EightWayDirectionalMixin, Entity):
    pass


class TrainStop(EightWayDirectionalMixin, Entity):
    pass


class RailSignal(EightWayDirectionalMixin, Entity):
    pass


class TrainCar(OrientationMixin, Entity):
    pass


# Requester Chest, Logistics Chest
class LogisticsRequestContainer(RequestFiltersMixin, CircuitConnectableMixin, InventoryMixin, Entity):
    def __init__(self, **kwargs):
        if kwargs["name"] not in logistic_containers:
            raise InvalidEntityID("'{}' is not a valid name for this type".format(kwargs["name"]))
        super().__init__(**kwargs)


class Roboport(CircuitConnectableMixin, InventoryMixin, Entity):
    pass


class Lamp(CircuitConnectableMixin, Entity):
    pass


class ArithmeticCombinator(CircuitConnectableMixin, Entity):
    def __init__(self, **kwargs):
        pass

    def set_arithmetic_conditions(self, a, op, b):
        pass


class DeciderCombinator(CircuitConnectableMixin, Entity):
    def __init__(self, **kwargs):
        pass
    
    def set_decider_conditions(self, a, op, b):
        pass


class ConstantCombinator(CircuitConnectableMixin, Entity):
    pass


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
    kwargs["name"] = name # TODO: see if we can get rid of this
    if name in containers:
        return Container(**kwargs)
    if name in storage_tanks:
        return StorageTank(**kwargs)
    if name in transport_belts:
        return TransportBelt(**kwargs)
    if name in underground_belts:
        return UndergroundBelt(**kwargs)
    if name in splitters:
        return Splitter(**kwargs)
    if name in inserters:
        return Inserter(**kwargs)
    if name in filter_inserters:
        return FilterInserter(**kwargs)
    if name in electric_poles:
        return ElectricPole(**kwargs)
    if name in pipes:
        return Pipe(**kwargs)
    if name in underground_pipes:
        return UndergroundPipe(**kwargs)
    if name in pumps:
        return Pump(**kwargs)
    if name in straight_rails:
        return StraightRail(**kwargs)
    if name in curved_rails:
        return CurvedRail(**kwargs)
    if name in train_stops:
        return TrainStop(**kwargs)
    if name in rail_signals:
        return RailSignal(**kwargs)
    if name in train_cars:
        return TrainCar(**kwargs)
    if name in logistic_containers:
        return LogisticsRequestContainer(**kwargs)
    if name in roboports:
        return Roboport(**kwargs)
    if name in lamps:
        return Lamp(**kwargs)
    if name in arithmetic_combinators:
        return ArithmeticCombinator(**kwargs)
    if name in decider_combinators:
        return DeciderCombinator(**kwargs)
    if name in constant_combinators:
        return ConstantCombinator(**kwargs)
    if name in power_switches:
        return PowerSwitch(**kwargs)
    if name in programmable_speakers:
        return ProgrammableSpeaker(**kwargs)
    if name in boilers:
        return Boiler(**kwargs)
    if name in generators:
        return Generator(**kwargs)
    if name in assembling_machines:
        return AssemblingMachine(**kwargs)
    
    raise InvalidEntityID("'{}'".format(name))