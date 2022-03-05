# mixins.py

# TODO: add `set_name` function in entity, so you can change an entity's type but keep its metadata
# TODO: value check everything + warnings
# TODO: Add warnings for placement constraints on all entities
# TODO: documentation!
# TODO: "succinct" mode for to_dict(), integrate with better default setting/management
# TODO: verify that a json dict representation of an entity imported from factorio actually imports correctly into
#   every entity's constructor
# TODO: verify that a blueprint string made of each entity correctly imports into Factorio (how would I test that programmatically?)
# TODO: make sure that all functions that modify the entity preserve the entity's contents when they throw an error
# TODO: change all instances of signal_dict to signatures.SIGNAL_ID.validate()

from draftsman import signatures
from draftsman.constants import Direction, ReadMode, ModeOfOperation
from draftsman.errors import (
    InvalidItemID, InvalidSignalID, InvalidWireType, InvalidConnectionSide, 
    EntityNotCircuitConnectable, EntityNotPowerConnectable, InvalidRecipeID,
)
from draftsman.utils import warn_user, signal_dict

#from draftsman.data.entities import entity_dimensions, circuit_wire_distances, power_wire_distances, module_slots
from draftsman.data.signals import item_signals, fluid_signals
import draftsman.data.recipes
import draftsman.data.entities as entities

import math
from typing import Any, Union, Callable


def aabb_to_dimensions(aabb):
    x = math.ceil(aabb[2][1] - aabb[1][1])
    y = math.ceil(aabb[2][2] - aabb[1][2])
    return x, y

# TODO: alphabetize

# class EntityLike(metaclass=abc.ABCMeta):
#     def __init__(self, name: str, position: Union[list, dict] = [0, 0], **kwargs):
#         pass

#     def set_name():
#         pass

#     def set_id():
#         pass

#     @abc.abstractmethod
#     def to_dict():
#         pass


class Entity:
    def __init__(self, name:str, position:Union[list,dict] = [0, 0], **kwargs):
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
            self.set_id(kwargs["id"])
            self.unused_args.pop("id")

        # Populate the entity attributes from data.entities.raw
        #self._get_entity_attributes()
        self.collision_box = entities.raw[self.name]["collision_box"]

        # Width and Height (Internal)
        # TODO: change this to AABB
        self.tile_width, self.tile_height=aabb_to_dimensions(self.collision_box)
        if "tile_width" in entities.raw[self.name]:
            self.tile_width = entities.raw[self.name]["tile_width"]
        if "tile_height" in entities.raw[self.name]:
            self.tile_height = entities.raw[self.name]["tile_height"]

        # Power connectable? (Internal) (Overwritten if applicable)
        self.power_connectable = False
        # Dual power connectable? (Internal) (Overwritten if applicable)
        self.dual_power_connectable = False

        # Circuit connectable? (Interal) (Overwritten if applicable)
        self.circuit_connectable = False
        # Dual circuit connectable? (Internal) (Overwritten if applicable)
        self.dual_circuit_connectable = False

        # Double grid aligned?
        self.double_grid_aligned = False

        # (Absolute) Position (External)
        # Grid Position (Internal)
        position = signatures.POSITION.validate(position)
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
        self.id = signatures.STRING.validate(id)

    def set_absolute_position(self, x: float, y: float) -> None:
        """
        Sets the position of the object, or the position that Factorio uses. On
        most entities, the position of the object is located at the center.
        """
        self.position = signatures.ABS_POSITION.validate({"x": x, "y": y})
        grid_x = round(self.position["x"] - self.tile_width / 2.0)
        grid_y = round(self.position["y"] - self.tile_height / 2.0)
        self.grid_position = [grid_x, grid_y]

    def set_grid_position(self, x: int, y: int) -> None:
        """
        Sets the grid position of the object, or the tile coordinates of the
        object. Calculates the absolute position based off of the dimensions of
        the entity. If a tile is multiple tiles in width or height, the grid
        coordinate is the top left-most tile of the entity.
        """
        self.grid_position = signatures.GRID_POSITION.validate([x, y])
        absolute_x = self.grid_position[0] + self.tile_width / 2.0
        absolute_y = self.grid_position[1] + self.tile_height / 2.0
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


################################################################################
# Mixins
################################################################################


class DirectionalMixin:
    """ 
    Enables entities to be rotated. 
    """
    def __init__(self, name: str, position: Union[list, dict] = [0, 0], **kwargs):
        super().__init__(name, **kwargs)

        # Rotated width and height
        self.rotated_width = self.tile_width
        self.rotated_height = self.tile_height

        self.direction = 0
        if "direction" in kwargs:
            self.set_direction(kwargs["direction"])
            self.unused_args.pop("direction")
        self._add_export("direction", lambda x: x != 0)

        # Now that we know the entity is rotatable, try calling the set_position
        # equivalents again to now handle the rotation
        position = signatures.POSITION.validate(position) # FIXME: technically redundant
        if isinstance(position, list):
            self.set_grid_position(position[0], position[1])
        elif isinstance(position, dict): # pragma: no branch
            self.set_absolute_position(position["x"], position["y"])


    def set_absolute_position(self, x: float, y: float) -> None:
        """
        Sets the position of the object, or the position that Factorio uses. On
        most entities, the position of the object is located at the center.
        """
        self.position = signatures.ABS_POSITION.validate({"x": x, "y": y})
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
        self.grid_position = signatures.GRID_POSITION.validate([x, y])
        absolute_x = self.grid_position[0] + self.rotated_width / 2.0
        absolute_y = self.grid_position[1] + self.rotated_height / 2.0
        self.position = {"x": absolute_x, "y": absolute_y}

    def set_direction(self, direction: int) -> None:
        """
        """
        self.direction = signatures.DIRECTION.validate(direction)
        if self.direction not in {0, 2, 4, 6}:
            warn_user("this entity only has 4-way rotation")
        if self.direction == Direction.EAST or self.direction == Direction.WEST:
            self.rotated_width = self.tile_height
            self.rotated_height = self.tile_width
        else:
            self.rotated_width = self.tile_width
            self.rotated_height = self.tile_height
        # Reset the grid/absolute positions in case the direction changed
        self.set_grid_position(self.grid_position[0], self.grid_position[1])


class EightWayDirectionalMixin:
    """
    Enables entities to be rotated across 8 directions.
    """
    def __init__(self, name: str, **kwargs):
        super().__init__(name, **kwargs)

        # Rotated width and height
        self.rotated_width = self.tile_width
        self.rotated_height = self.tile_height

        self.direction = 0
        if "direction" in kwargs:
            self.set_direction(kwargs["direction"])
            self.unused_args.pop("direction")
        self._add_export("direction", lambda x: x != 0)

    def set_absolute_position(self, x: float, y: float) -> None:
        """
        Sets the position of the object, or the position that Factorio uses. On
        most entities, the position of the object is located at the center.
        """
        self.position = signatures.ABS_POSITION.validate({"x": x, "y": y})
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
        self.grid_position = signatures.GRID_POSITION.validate([x, y])
        absolute_x = self.grid_position[0] + self.rotated_width / 2.0
        absolute_y = self.grid_position[1] + self.rotated_height / 2.0
        self.position = {"x": absolute_x, "y": absolute_y}

    def set_direction(self, direction: int) -> None:
        """
        """
        # TODO: add warnings if out of [0, 7] range
        self.direction = signatures.DIRECTION.validate(direction)
        if self.direction in {2, 3, 6, 7}:
            self.rotated_width = self.tile_height
            self.rotated_height = self.tile_width
        else:
            self.rotated_width = self.tile_width
            self.rotated_height = self.tile_height


class OrientationMixin:
    """ 
    Used in trains and wagons to specify their direction. 
    """
    def __init__(self, name: str, **kwargs):
        super().__init__(name, **kwargs)

        self.orientation = 0.0
        if "orientation" in kwargs:
            self.set_orientation(kwargs["orientation"])
            self.unused_args.pop("orientation")
        self._add_export("orientation", lambda x: x != 0)

    def set_orientation(self, orientation: float) -> None:
        """
        Sets the orientation of the train car. (0.0 -> 1.0)
        """
        self.orientation = signatures.ORIENTATION.validate(orientation)


class InventoryMixin:
    """
    Enables the entity to have inventory control.
    """
    def __init__(self, name: str, **kwargs):
        super().__init__(name, **kwargs)

        self.inventory_size = entities.raw[self.name]["inventory_size"]

        self.bar = None
        if "bar" in kwargs:
            self.set_bar_index(kwargs["bar"])
            self.unused_args.pop("bar")
        self._add_export("bar", lambda x: x is not None)

    def set_bar_index(self, index: int) -> None:
        """
        Sets the inventory limiting bar.
        """
        self.bar = signatures.BAR.validate(index)
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
            self.unused_args.pop("inventory")
        self._add_export("inventory", lambda x: len(x) != 0)

    def set_inventory(self, inventory: dict) -> None:
        """
        Sets the entire inventory configuration for the cargo wagon.
        """
        # Validate filter schema
        self.inventory = signatures.INVENTORY_FILTER.validate(inventory)

    def set_inventory_filter(self, index: int, item: str) -> None:
        """
        Sets the item filter at location `index` to `name`. If `name` is set to
        `None` the item filter at that location is removed.

        `index`: [0-39] (0-indexed) 
        """
        if "filters" not in self.inventory:
            self.inventory["filters"] = []

        index = signatures.INTEGER.validate(index)
        if item is not None and item not in item_signals: # FIXME
            raise InvalidItemID(item)

        # TODO: warn if index is ouside the range of the max filter slots
        # (which needs to be extracted)
        
        # Check to see if filters already contains an entry with the same index
        for i, filter in enumerate(self.inventory["filters"]):
            if filter["index"] == index + 1: # Index already exists in the list
                if item is None: # Delete the entry
                    del self.inventory["filters"][i]
                else: # Set the new value
                    #self.inventory["filters"][i] = {"index": index+1,"name": item}
                    self.inventory["filters"][i]["name"] = item
                return

        # If no entry with the same index was found
        self.inventory["filters"].append({"index": index + 1, "name": item})

    def set_inventory_filters(self, filters: list) -> None: 
        """
        Sets the item filters for the inserter or loader.
        """
        if filters is None:
            self.inventory.pop("filters", None)
            return

        # Make sure filters conforms
        # TODO

        # Make sure the items are item signals
        for item in filters:
            if isinstance(item, dict):
                item = item["name"]
            if item not in item_signals:
                raise InvalidItemID(item)

        for i in range(len(filters)):
            if isinstance(filters[i], str):
                self.set_inventory_filter(i, filters[i])
            else: # dict
                self.set_inventory_filter(i, filters[i]["name"])

    def set_bar_index(self, index: int) -> None:
        """
        Sets the bar of the train's inventory. Setting it to `None` removes the
        parameter from the configuration.
        """
        if index is None:
            self.inventory.pop("bar", None)
        else:
            self.inventory["bar"] = signatures.BAR.validate(index)
            if index >= 40: # TODO: make this number not hardcoded
                warn_user("Bar index is greater than 40")


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
        # if type in {"input", "output", None}:
        #     self.type = type
        # else:
        #     raise ValueError("`type` must be one of 'input', 'output' or 'None'")
        self.type = signatures.IO_TYPE.validate(type)


class PowerConnectableMixin:
    def __init__(self, name: str, **kwargs):
        super().__init__(name, **kwargs)

        self.power_connectable = True

        #self.power_wire_max_distance = power_wire_distances[name]
        # self.maximum_wire_distance
        if "maximum_wire_distance" in entities.raw[self.name]:
            self.maximum_wire_distance = entities.raw[self.name]["maximum_wire_distance"]
        else:
            self.maximum_wire_distance = entities.raw[self.name]["wire_max_distance"]

        self.neighbours = []
        if "neighbours" in kwargs:
            self.set_neighbours(kwargs["neighbours"])
            self.unused_args.pop("neighbours")
        self._add_export("neighbours", lambda x: len(x) != 0)

    def set_neighbours(self, neighbours: list) -> None:
        """
        """
        self.neighbours = signatures.NEIGHBOURS.validate(neighbours)

    def add_power_connection(self, target: Entity, side: int = 1) -> None:
        """
        Adds a power wire between this entity and another power-connectable one.
        """
        if not target.power_connectable:
            raise EntityNotPowerConnectable(target.id)
        if self.dual_power_connectable and target.dual_power_connectable:
            raise Exception("2 dual power connectable entities cannot connect")

        # Issue a warning if the entities being connected are too far apart
        min_dist = min(self.maximum_wire_distance,
                       target.maximum_wire_distance)
        self_pos = [self.position["x"], self.position["y"]]
        target_pos = [target.position["x"], target.position["y"]]
        real_dist = math.dist(self_pos, target_pos)
        if real_dist > min_dist:
            warn_user("Distance between entities ({}) is greater than max ({})"
                      .format(real_dist, min_dist))

        # Only worried about self
        if self.dual_power_connectable: # power switch
            # Add copper circuit connection
            str_side = "Cu" + str(side - 1)
            if str_side not in self.connections:
                self.connections[str_side] = []

            entry = {"entity_id": target.id, "wire_id": 0}
            if entry not in self.connections[str_side]:
                self.connections[str_side].append(entry)
        else: # electric pole
            if not target.dual_power_connectable:
                if target.id not in self.neighbours:
                    self.neighbours.append(target.id)

        # Only worried about target
        if target.dual_power_connectable: # power switch
            # Add copper circuit connection
            str_side = "Cu" + str(side - 1)
            if str_side not in target.connections:
                target.connections[str_side] = []

            entry = {"entity_id": self.id, "wire_id": 0}
            if entry not in target.connections[str_side]:
                target.connections[str_side].append(entry)
        else: # electric pole
            if not self.dual_power_connectable:
                if self.id not in target.neighbours:
                    target.neighbours.append(self.id)

    def remove_power_connection(self, target: Entity, side: int = 1) -> None:
        """
        """

        # Only worried about self
        if self.dual_power_connectable: # power switch
            str_side = "Cu" + str(side - 1)
            entry = {"entity_id": target.id, "wire_id": 0}
            if str_side in self.connections:
                if entry in self.connections[str_side]:
                    self.connections[str_side].remove(entry)
                if len(self.connections[str_side]) == 0:
                    del self.connections[str_side]
        else: # electric pole
            if not target.dual_power_connectable:
                try:
                    self.neighbours.remove(target.id)
                except ValueError:
                    pass

         # Only worried about target
        if target.dual_power_connectable: # power switch
            str_side = "Cu" + str(side - 1)
            entry = {"entity_id": self.id, "wire_id": 0}
            if str_side in target.connections:
                if entry in target.connections[str_side]:
                    target.connections[str_side].remove(entry)
                if len(target.connections[str_side]) == 0:
                    del target.connections[str_side]
        else: # electric pole
            if not self.dual_power_connectable:
                try:
                    target.neighbours.remove(self.id)
                except ValueError:
                    pass


class CircuitConnectableMixin:
    """
    Enables the entity to be connected to circuit networks.
    """
    def __init__(self, name: str, **kwargs):
        super().__init__(name, **kwargs)

        self.circuit_connectable = True

        #self.circuit_wire_max_distance = circuit_wire_distances[name]
        # self.circuit_wire_max_distance
        # if not hasattr(self, "circuit_wire_max_distance"):
        #     self.circuit_wire_max_distance = self.maximum_wire_distance
        if "circuit_wire_max_distance" in entities.raw[self.name]:
            self.circuit_wire_max_distance = entities.raw[self.name]["circuit_wire_max_distance"]
        elif "maximum_wire_distance" in entities.raw[self.name]:
            self.circuit_wire_max_distance = entities.raw[self.name]["maximum_wire_distance"]
        elif "wire_max_distance" in entities.raw[self.name]:
            self.circuit_wire_max_distance = entities.raw[self.name]["wire_max_distance"]

        self.connections = {}
        if "connections" in kwargs:
            self.set_connections(kwargs["connections"])
            self.unused_args.pop("connections")
        self._add_export("connections", lambda x: len(x) != 0)

    def set_connections(self, connections: dict) -> None:
        """
        """
        self.connections = signatures.CONNECTIONS.validate(connections)

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
        self.control_behavior = signatures.CONTROL_BEHAVIOR.validate(behavior)

    def _set_condition(self, condition_name: str, a: str, op: str, b: Union[str, int]):
        self.control_behavior[condition_name] = {}
        condition = self.control_behavior[condition_name]
        # Check the inputs
        # A
        # if a is None:
        #     pass # Keep the first signal empty
        # elif isinstance(a, str):
        #     condition["first_signal"] = signal_dict(a)
        # elif isinstance(a, int):
        #     raise TypeError("normal conditions cannot have a constant first")
        # else:
        #     raise TypeError("`a` is neither 'str' nor 'None'")

        a = signatures.SIGNAL_ID.validate(a)
        op = signatures.COMPARATOR.validate(op)
        b = signatures.SIGNAL_ID_OR_CONSTANT.validate(b)

        # A
        if a is None:
            pass
        else:
            condition["first_signal"] = a
        
        # TODO: handle the case where the user inputs '≥'
        # Consider the case where someone is pulling the comparator from a 
        # blueprint string that already exists; it would be way easier to simply
        # insert it into the function without having to convert it back and 
        # forth

        # op
        condition["comparator"] = op

        # B
        if isinstance(b, dict):
            condition["second_signal"] = b
        else: # int
            condition["constant"] = b


class EnableDisableMixin: # (ControlBehaviorMixin)
    """
    Allows the entity to control whether or not it's circuit condition affects
    its operation. Usually used with CircuitConditionMixin
    """
    def set_enable_disable(self, value: bool) -> None:
        """
        """
        if value is None:
            self.control_behavior.pop("circuit_enable_disable", None)
        else:
            self.control_behavior["circuit_enable_disable"] = signatures.BOOLEAN.validate(value)


class CircuitConditionMixin: # (ControlBehaviorMixin)
    """
    Allows the Entity to have an circuit enable condition. Used in Pumps, 
    Inserters, Belts, etc.
    """
    def __init__(self, name: str, **kwargs):
        super().__init__(name, **kwargs)

    def set_enabled_condition(self, a: str = None, op: str = "<", b: Union[str, int] = 0):
        """
        """
        self._set_condition("circuit_condition", a, op, b)

    def remove_enabled_condition(self): # TODO: delete
        """
        """
        self.control_behavior.pop("circuit_condition", None)


class LogisticConditionMixin: # (ControlBehaviorMixin)
    def __init__(self, name: str, **kwargs):
        super().__init__(name, **kwargs)

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

    def remove_logistic_condition(self): # TODO: delete
        """
        """
        self.control_behavior.pop("logistic_condition", None)


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
        if value is None:
            self.control_behavior.pop("circuit_read_resources", None)
        else:
            self.control_behavior["circuit_read_resources"] = signatures.BOOLEAN.validate(value)

    def set_read_mode(self, mode: ReadMode):
        """
        """
        # TODO: make ReadMode MiningDrillReadMode
        if mode is None:
            self.control_behavior.pop("circuit_resource_read_mode", None)
        else:
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

    def set_stack_size_override(self, stack_size: int):
        """
        Sets an inserter's stack size override.
        """
        self.override_stack_size = signatures.INTEGER.validate(stack_size)

    def set_circuit_stack_size_enabled(self, enabled: bool):
        """
        Set if the inserter's stack size is controlled by circuit signal.
        """
        if enabled is None:
            self.control_behavior.pop("circuit_set_stack_size", None)
        else:
            self.control_behavior["circuit_set_stack_size"] = signatures.BOOLEAN.validate(enabled)

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
        else:
            self.control_behavior["red_output_signal"] = signal_dict(signal)

    def set_yellow_output_signal(self, signal: str) -> None:
        """
        """
        if signal is None:
            self.control_behavior.pop("yellow_output_signal", None)
        else:
            self.control_behavior["yellow_output_signal"] = signal_dict(signal)

    def set_green_output_signal(self, signal: str) -> None:
        """
        """
        if signal is None:
            self.control_behavior.pop("green_output_signal", None)
        else:
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


class RecipeMixin:
    def __init__(self, name: str, **kwargs):
        super().__init__(name, **kwargs)

        # List of all recipes that this machine can make
        self.recipes = draftsman.data.recipes.recipes[name]

        # Recipe that this machine is currently set to
        self.recipe = None
        if "recipe" in kwargs:
            self.set_recipe(kwargs["recipe"])
            self.unused_args.pop("recipe")
        self._add_export("recipe", lambda x: x is not None)

    def set_recipe(self, recipe: str):
        """
        """
        if recipe is None:
            self.recipe = None
        else:
            if recipe not in self.recipes:
                raise InvalidRecipeID(recipe)
            self.recipe = signatures.STRING.validate(recipe)


class RequestFiltersMixin:
    """
    Used to allow Logistics Containers to request items from the Logisitics
    network.
    """
    def __init__(self, name: str, **kwargs):
        super().__init__(name, **kwargs)

        # TODO: handle internal input format for set_request_filters()

        self.request_filters = None
        if "request_filters" in kwargs:
            self.set_request_filters(kwargs["request_filters"])
            self.unused_args.pop("request_filters")
        self._add_export("request_filters", lambda x: x is not None)

    def set_request_filter(self, index: int, item: str, count: int = 0) -> None:
        """
        """

        if self.request_filters is None:
            self.request_filters = []
        
        index = signatures.INTEGER.validate(index)
        if item is not None and item not in item_signals: # TODO: FIXME
            raise InvalidItemID(item)
        count = signatures.INTEGER.validate(count)

        # TODO: warn if index out of range (index < 0 or index > 1000 )

        # Check to see if filters already contains an entry with the same index
        for i, filter in enumerate(self.request_filters):
            if filter["index"] == index + 1: # Index already exists in the list
                if item is None: # Delete the entry
                    del self.request_filters[i]
                else: # Set the new name + value
                    # self.inventory["filters"][i] = {
                    #     "index": index+1, "name": name, "count": count
                    # }
                    self.request_filters[i]["name"] = item
                    self.request_filters[i]["count"] = count
                return

        # If no entry with the same index was found
        self.request_filters.append({
            "index": index+1, "name": item, "count": count
        })

    def set_request_filters(self, filters: list) -> None:
        """
        """

        # Validate filters
        filters = signatures.REQUEST_FILTERS.validate(filters)

        # Make sure the items are item signals
        for item in filters:
            if item[0] not in item_signals:
                raise InvalidItemID(item[0])

        # Make sure we dont wipe before throwing the error
        self.request_filters = []

        # for i in range(len(filters)):
        #     filters[i] = {"index": i + 1, "name": filters[i][0], "count": filters[i][1]}
        # self.request_filters = filters
        for i in range(len(filters)):
            self.set_request_filter(i, filters[i][0], filters[i][1])


class RequestItemsMixin: # TODO: rename to RequestModulesMixin
    """
    NOTE: this is for module requests and stuff like that, not logistics!

    Think an assembling machine that needs speed modules inside of it
    """
    def __init__(self, name: str, **kwargs):
        super().__init__(name, **kwargs)

        # Get the total number of module slots
        try:
            self.total_module_slots = entities.raw[self.name]["module_specification"]["module_slots"]
        except KeyError:
            self.total_module_slots = 0

        # Keep track of the current module slots currently used
        self.module_slots_occupied = 0

        self.items = {}
        if "items" in kwargs:
            self.set_item_requests(kwargs["items"])
            self.unused_args.pop("items")
        self._add_export("items", lambda x: len(x) != 0)

    def set_item_requests(self, items: dict) -> None:
        """
        """
        if items is None:
            self.items = {}
            self.module_slots_occupied = 0
        else:
            for name, amount in items.items():
                self.set_item_request(name, amount)

    def set_item_request(self, item, amount):
        """
        """
        # TODO: check if entity can accept productivity modules
        # Also consider the case where the recipe changes on a assembling
        # machine; you have to retroactively issue a warning if the new recipe 
        # cannot use prod modules

        if item not in item_signals:
            raise InvalidSignalID(item)

        if amount is None:
            self.module_slots_occupied -= self.items.pop(item, None)
            return

        amount = signatures.INTEGER.validate(amount)
        
        self.items[item] = amount
        self.module_slots_occupied += amount
        if self.module_slots_occupied > self.total_module_slots:
            warn_user("Current number of module slots used ({}) greater than "
                      "max module capacity ({})"
                      .format(
                            self.module_slots_occupied,
                            self.total_module_slots
                        )
                      )


# class InfinitySettingsMixin:
#     def __init__(self, name: str, **kwargs):
#         super().__init__(name, **kwargs)

#         self.infinity_settings = {}
#         if "infinity_settings" in kwargs:
#             self.set_infinity_settings(kwargs["infinity_settings"])
#             self.unused_args.pop("infinity_settings")
#         self._add_export("infinity_settings", lambda x: len(x) != 0)

#     def set_infinity_settings(self, settings: dict) -> None:
#         """
#         """
#         if settings is None:
#             self.infinity_settings = {}
#         else:
#             self.infinity_settings = settings


class ColorMixin:
    def __init__(self, name: str, **kwargs):
        super().__init__(name, **kwargs)

        self.color = None
        if "color" in kwargs:
            color = signatures.USER_COLOR.validate(kwargs["color"])
            self.set_color(**color)
            self.unused_args.pop("color")
        self._add_export("color", lambda x: x is not None)

    def set_color(self, r: float, g: float, b: float, a: float = 1.0) -> None:
        """
        """
        self.color = signatures.COLOR.validate({"r": r, "g": g, "b": b, "a": a})

    def remove_color(self):
        """
        """
        self.color = None


class DoubleGridAlignedMixin:
    def __init__(self, name: str, **kwargs):
        super().__init__(name, **kwargs)

        self.double_grid_aligned = True

        if "position" in kwargs:
            position = kwargs["position"]
            if isinstance(position, list):
                self.set_grid_position(position[0], position[1])
            elif isinstance(position, dict): # pragma: no branch
                self.set_absolute_position(position["x"], position["y"])

    def set_absolute_position(self, x: float, y: float) -> None:
        """
        Overwritten
        """
        super().set_absolute_position(x, y)

        # if the grid alignment is off, warn the user
        if self.grid_position[0] % 2 == 1 or self.grid_position[1] % 2 == 1:
            cast_position = [math.floor(self.grid_position[0] / 2) * 2,
                             math.floor(self.grid_position[1] / 2) * 2]
            warn_user("Double grid-aligned entity is not placed along chunk "
                      "grid; entity's position will be cast from {} to {} when "
                      "imported".format(self.grid_position, cast_position))

    def set_grid_position(self, x: int, y: int) -> None:
        """
        """
        super().set_grid_position(x, y)

        if self.grid_position[0] % 2 == 1 or self.grid_position[1] % 2 == 1:
            cast_position = [math.floor(self.grid_position[0] / 2) * 2,
                             math.floor(self.grid_position[1] / 2) * 2]
            warn_user("Double grid-aligned entity is not placed along chunk "
                      "grid; entity's position will be cast from {} to {} when "
                      "imported".format(self.grid_position, cast_position))

