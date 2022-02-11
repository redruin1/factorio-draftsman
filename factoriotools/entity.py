# entity.py

# TODO: handle the difference between grid and position
# TODO: probably change the way exports works: instead of writing methods that create super() chains, store some metadata in the
# exports dictionary that tells what condition the item has to reach in order for it to be included in the output dict

from typing import Any, Callable
from factoriotools.errors import InvalidEntityID, InvalidSignalID
from factoriotools.signals import get_signal_type, item_signals
from factoriotools.entity_data import entity_dimensions

PULSE = 0
HOLD = 1

storage_containers = {
    "wooden-chest", "iron-chest", "steel-chest", "storage-tank"
}

logistics_storage_containers = {
    "logistics-chest-requester", "logistics-chest-storage"
}

transport_belts = {
    "transport-belt", "fast-transport-belt", "express-transport-belt"
}

inserters = {
    "burner-inserter", "inserter", "long-handed-inserter", "fast-inserter",
    "stack-inserter"
}

filter_inserters = {
    "filter-inserter", "stack-filter-inserter"
}

assembling_machines = {
    "assembling-machine-1", "assembling-machine-2", "assembling-machine-3"
}

multiple_connection_point_entities = {
    "decider-combinator", "arithmetic-combinator"
}

# mixins!
# TODO: organize alphabetically
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

# class OrientationMixin:
#     """ Used in trains to specify their direction. """
#     def __init__(self, **kwargs):
#         pass # TODO

#     def set_orientation(self, orientation: float) -> None:
#         self.orientation = orientation

class ContainerMixin:
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
    Allows inventories to set content filters
    """
    pass

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

    def set_circuit_condition(self, **kwargs):
        if "circuit_condition" not in self.control_behavior:
            self.control_behavior["circuit_condition"] = {}
        for k, v in kwargs.items():
            self.control_behavior["circuit_condition"][k] = v
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
            if "second_signal" in circuit_condition:
                # If its a string, change it, otherwise treat it as gospel
                if isinstance(circuit_condition["second_signal"], str):
                    name = circuit_condition["second_signal"]
                    circuit_condition["second_signal"] = {
                        "name": name,
                        "type": get_signal_type(name)
                    }

class PowerConnectableMixin:
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.neighbours = {}
        # TODO

    def add_power_connection_point(self, target_id: int):
        pass # TODO

class CircuitConnectableMixin:
    """
    Enables the entity to be connected to circuit networks.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.circuit_connectable = True
        self.connections = {}
        # TODO: add kwargs support
        self._add_export("connections", lambda x: len(x) != 0)
        # Is the entity connectable with wires? (Internal)

    def add_circuit_connection_point(self, source_side: int, color: str, target_name: str, target_num: int, target_side: int = 1) -> None:
        """
        Constructs the `connections` dictionary in proper format
        """
        if str(source_side) not in self.connections:
            self.connections[str(source_side)] = dict()
        current_side = self.connections[str(source_side)]

        if color not in current_side:
            current_side[color] = list()
        current_color = current_side[color]

        entry = {"entity_id": target_num}
        if target_name in multiple_connection_point_entities:
            entry = {"entity_id": target_num, "circuit_id": target_side}

        current_color.append(entry)

    # def to_dict(self) -> dict:
    #     # Call parent to_dict (Entity by default)
    #     out = super().to_dict()
    #     # Delete connections if there's no useful information contained
    #     if len(out["connections"]) == 0:
    #         del out["connections"]

    #     return out
        

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
    def __init__(self, name: str, position: dict|list = [0, 0], **kwargs):
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

        self.tags = {}

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
        pass

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


# Wooden Chest, Iron Chest, Steel Chest, Buffer Chest, Passive Provider Chest, Active Provider Chest
class StorageContainer(CircuitConnectableMixin, ContainerMixin, Entity):
    def __init__(self, **kwargs):
        if kwargs["name"] not in storage_containers:
            raise InvalidEntityID("'{}' is not a valid name for this type".format(kwargs["name"]))
        super().__init__(**kwargs)


# Requester Chest, Logistics Chest
class LogisticsRequestContainer(RequestFiltersMixin, CircuitConnectableMixin, ContainerMixin, Entity):
    def __init__(self, **kwargs):
        if kwargs["name"] not in logistics_storage_containers:
            raise InvalidEntityID("'{}' is not a valid name for this type".format(kwargs["name"]))
        super().__init__(**kwargs)


class TransportBelt(ControlBehaviorMixin, CircuitConnectableMixin, DirectionalMixin, Entity):
    def __init__(self, **kwargs):
        if kwargs["name"] not in transport_belts:
            raise InvalidEntityID("'{}' is not a valid name for this type".format(kwargs["name"]))
        super(TransportBelt, self).__init__(**kwargs)


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


class AssemblingMachine(ItemRequestMixin, RecipeMixin, Entity):
    def __init__(self, **kwargs):
        if kwargs["name"] not in assembling_machines:
            raise InvalidEntityID("'{}' is not a valid name for this type".format(kwargs["name"]))
        super(AssemblingMachine, self).__init__(**kwargs)


def new_entity(name: str, **kwargs):
    kwargs["name"] = name # TODO: see if we can get rid of this
    if name in storage_containers:
        return StorageContainer(**kwargs)
    if name in logistics_storage_containers:
        return LogisticsRequestContainer(**kwargs)
    if name in transport_belts:
        return TransportBelt(**kwargs)
    if name in inserters:
        return Inserter(**kwargs)
    if name in filter_inserters:
        return FilterInserter(**kwargs)
    if name in assembling_machines:
        return AssemblingMachine(**kwargs)
    
    raise InvalidEntityID("'{}'".format(name))