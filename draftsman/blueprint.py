# blueprint.py

# TODO: Add error checking
# Checking if the signals passed into setIcons are actual signals, etc.
# TODO: if blueprint
# TODO: Add warnings for placement constraints on rails and rail signals
# TODO: Add groups (back)
# TODO: Complete BlueprintBook
# TODO: figure out a way to make sure warnings from this class point to the correct calling function
#   (https://stackoverflow.com/questions/54399469/how-do-i-assign-a-stacklevel-to-a-warning-depending-on-the-caller)

from draftsman._factorio_version import __factorio_version_info__

# from draftsman.signatures import (
#     COLOR, 
#     ICON, 
#     BLUEPRINT, 
#     BLUEPRINT_BOOK
# )
from draftsman.constants import Direction
from draftsman.error import (
    IncorrectBlueprintTypeError, DuplicateIDError, 
    MalformedBlueprintStringError, InvalidSignalError, DraftsmanError,
    UnreasonablySizedBlueprintError
)
from draftsman.entity import Wall, new_entity
from draftsman.classes.entity import Entity
from draftsman.classes.entitylike import EntityLike
from draftsman import signatures
from draftsman.tile import Tile
import draftsman.utils as utils
from draftsman.warning import (
    HiddenEntityWarning, OverlappingEntitiesWarning, OverlappingTilesWarning, 
    UselessConnectionWarning
)

import draftsman.data.signals as signals

from collections.abc import MutableSequence
import copy
from io import FileIO
import json
import math
from schema import SchemaError
from typing import Union
import warnings


# def warning_not_filtered(warning_to_check):
#     """
#     Theoretically this would allow us to check if we need to do any error 
#     checking, but its frankly pretty non-standard and the performance gain isn't
#     noticable since we added the SpatialHashMap.
#     """
#     # Iterate over every filter
#     for filter in warnings.filters:
#         # If the filter does not ignore the current warning
#         if issubclass(warning_to_check, filter[2]) and filter[0] != "ignore":
#             return False
#     # Otherwise, none of the filters matched
#     return True


# class BiDict(dict):
#     def __init__(self, *args, **kwargs):
#         super(BiDict, self).__init__(*args, **kwargs)
#         self.inverse = {}
#         for key, value in self.items():
#             self.inverse[value] = key
#             # If we want multiple key -> value pairs:
#             #self.inverse.setdefault(value, []).append(key)

#     def __setitem__(self, key, value):
#         if key in self:
#             del self.inverse[self[key]]
#         #    self.inverse[self[key]].remove(key)
#         super(BiDict, self).__setitem__(key, value)
#         self.inverse[value] = key

#     # def __getitem__(self, key: Any) -> Any:
#     #     pass

#     def __delitem__(self, key):
#         if self[key] in self.inverse and not self.inverse[self[key]]:
#             del self.inverse[self[key]]
#         super(BiDict, self).__delitem__(key)


class IDList(list):
    """
    TODO: implement all list functions
    Maybe use abc.MutableSequence? But can I still modify append to take a 
    optional second argument?
    """
    def __init__(self, *args, **kwargs):
        super(IDList, self).__init__(*args, **kwargs)
        self.id_map = {}
        self.num_to_key = {}
        self.key_to_num = {}

    def append(self, item):
        super(IDList, self).append(item)
        if hasattr(item, "id"):
            key = getattr(item, "id")
            self.id_map[key] = item
            self.num_to_key[len(self) - 1] = key
            self.key_to_num[key] = len(self) - 1

    def clear(self):
        super(IDList, self).clear()
        self.id_map.clear()
        self.num_to_key.clear()
        self.key_to_num.clear()

    # def copy(self):
    #     return 0

    # def extend(self):
    #     pass

    # def index(self):
    #     pass

    # def insert(self):
    #     pass

    def pop(self, index):
        # TODO: add -1 as default arg and make it work properly
        # If index isn't a number, get it's numeric position
        try:
            index = self.key_to_num[index]
        except KeyError:
            pass

        key = self.num_to_key.get(index, None)
        if key is not None:
            # Remove the key associated with item number `index`
            del self.id_map[key]
            del self.num_to_key[index]
            del self.key_to_num[key]
        
        self._shift_key_indices(index)

        return super(IDList, self).pop(index)

    def remove(self, item):
        index = self.index(item)

        key = self.num_to_key.get(index, None)
        if key is not None:
            # Remove the key associated with item number `index`
            del self.id_map[key]
            del self.num_to_key[index]
            del self.key_to_num[key]

        self._shift_key_indices(index)

        super(IDList, self).remove(item)

    # def reverse(self):
    #     pass

    # def sort(self):
    #     pass

    def __getitem__(self, index):
        try:
            return super(IDList, self).__getitem__(index)
        except TypeError:
            return self.id_map[index]

    def __delitem__(self, index):
        # if index isn't a number, get it's numeric position
        self.pop(index)

    # def __contains__(self, __o: object) -> bool:
    #     return super().__contains__(__o) or __o in self.key_map

    def _shift_key_indices(self, index):
        # type: (int) -> None
        """
        Shifts the positions of all the elements above the current index down
        by one.
        """
        # Change the positions of any of the numeric links greater than
        # index to match their new offset positions
        for id in self.id_map:
            current_number = self.key_to_num[id]
            if current_number > index:
                self.key_to_num[id] -= 1
                del self.num_to_key[current_number]
                self.num_to_key[current_number - 1] = id


class SpatialHashMap(object):
    def __init__(self, cell_size = 8):
        self.cell_size = cell_size
        self.map = {}

    def add(self, item):
        """
        """
        # get cells based off of collision_box
        cell_coords = self._cell_coords_from_aabb(item.get_area())
        for cell_coord in cell_coords:
            try:
                self.map[cell_coord].append(item)
            except KeyError:
                self.map[cell_coord] = [item]

    def remove(self, item):
        """
        """
        cell_coords = self._cell_coords_from_aabb(item.get_area())
        for cell_coord in cell_coords:
            try:
                cell = self.map[cell_coord]
                cell.remove(item)
                if not cell:
                    del self.map[cell_coord]
            except:
                pass

    def get_in_radius(self, radius, pos, limit = None):
        """
        """
        cell_coords = self._cell_coords_from_radius(radius, pos)
        items = []
        for cell_coord in cell_coords:
            if cell_coord in self.map:
                for item in self.map[cell_coord]:
                    item_pos = (item.position["x"], item.position["y"])
                    if utils.point_in_radius(item_pos, radius, pos):
                        if limit is not None and len(items) >= limit:
                            break
                        # Make sure we dont add the same item multiple times if 
                        # it is spread across multiple cells
                        try:
                            items.index(item)
                        except ValueError:
                            items.append(item)
        
        return items

    def get_on_point(self, pos, limit = None):
        """
        """
        cell_coord = self.map_coords(pos[0], pos[1])
        items = []
        if cell_coord in self.map:
            for item in self.map[cell_coord]:
                if utils.point_in_aabb(pos, item.get_area()):
                    if limit is not None and len(items) >= limit:
                        break
                    items.append(item)
        
        return items

    def get_in_area(self, area, limit = None):
        """
        """
        cell_coords = self._cell_coords_from_aabb(area)
        items = []
        for cell_coord in cell_coords:
            if cell_coord in self.map:
                for item in self.map[cell_coord]:
                    if utils.aabb_overlaps_aabb(item.get_area(), area):
                        if limit is not None and len(items) >= limit:
                            break
                        # Make sure we dont add the same item multiple times if 
                        # it is spread across multiple cells
                        try:
                            items.index(item)
                        except ValueError:
                            items.append(item)

        return items
    
    def map_coords(self, x, y):
        """
        """
        return (math.floor(x / self.cell_size), math.floor(y / self.cell_size))

    def _cell_coords_from_aabb(self, aabb):
        """
        """
        # Add a small error to under-round if aabb lands on cell boundary
        eps = 0.001
        grid_min = self.map_coords(aabb[0][0], aabb[0][1])
        grid_max = self.map_coords(aabb[1][0] - eps, aabb[1][1] - eps)

        grid_width = grid_max[0] - grid_min[0] + 1
        grid_height = grid_max[1] - grid_min[1] + 1

        cells = []
        for j in range(grid_min[1], grid_min[1] + grid_height):
            for i in range(grid_min[0], grid_min[0] + grid_width):
                cells.append((i, j))

        return cells

    def _cell_coords_from_radius(self, radius, pos):
        """
        """
        grid_min = self.map_coords(pos[0] - radius, pos[1] - radius)
        grid_max = self.map_coords(pos[0] + radius, pos[1] + radius)

        grid_width = grid_max[0] - grid_min[0] + 1
        grid_height = grid_max[1] - grid_min[1] + 1

        cells = []
        for j in range(grid_min[1], grid_min[1] + grid_height):
            for i in range(grid_min[0], grid_min[0] + grid_width):
                cell_aabb = [
                    [i * self.cell_size, j * self.cell_size],
                    [(i+1) * self.cell_size, (j+1) * self.cell_size]
                ]
                if utils.aabb_overlaps_circle(cell_aabb, pos, radius):
                    cells.append((i, j))

        return cells


class Blueprint(object):
    """
    Factorio Blueprint class.
    """
    def __init__(self, blueprint_string = None):
        # type: (str) -> None
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
            self.root = dict()
            self.root["item"] = "blueprint"
            self._setup_defaults()

        # Create a complimentary list to store entity IDs. These allow the user
        # to specify names to each component to aid in referencing specific 
        # component before their final numeric values are known.
        #self.entity_numbers = BiDict()
        #self.tile_numbers = BiDict()
        #self.schedule_numbers = BiDict()

        # Create a spatial hashing object to make spatial queries much quicker
        self.tile_hashmap = SpatialHashMap()
        self.entity_hashmap = SpatialHashMap()

    def load_from_string(self, blueprint_string):
        # type: (str) -> None
        """
        Load the Blueprint with the contents of `blueprint_string`.

        Args:
            blueprint_string (str): Factorio-encoded blueprint string
        """
        root = utils.string_2_JSON(blueprint_string)
        # Ensure that the blueprint string actually points to a blueprint
        if "blueprint" not in root:
            raise IncorrectBlueprintTypeError
        self.root = root["blueprint"]
        self._setup_defaults()

        # Convert entities from dicts to Entity objects
        self._load_entities_from_root()

    def load_from_file(self, blueprint_file):
        # type: (FileIO) -> None
        """
        Load the Blueprint with the contents file handle `blueprint_file`.

        Args:
            blueprint_file (file-object): File object to read the data from
        """
        root = utils.string_2_JSON(blueprint_file.read())
        if "blueprint" not in root:
            raise IncorrectBlueprintTypeError
        self.root = root["blueprint"]
        self._setup_defaults()

        # Convert entities from dicts to Entity objects
        self._load_entities_from_root()

    # =========================================================================
    # Blueprint properties
    # =========================================================================

    @property
    def label(self):
        # type: () -> str
        """
        Sets the Blueprint's label (title). Setting label to `None` deletes the
        parameter from the Blueprint.

        Args:
            label (str): The new title of the blueprint

        Raises:
            ValueError if `label` is not a string
        """
        return self.root.get("label", None)

    @label.setter
    def label(self, value):
        # type: (str) -> None
        if value is None:
            self.root.pop("label", None)
        elif isinstance(value, str):
            self.root["label"] = value
        else:
            raise TypeError("`label` must be a string")

    # def set_label(self, label):
    #     # type: (str) -> None
    #     if label is None:
    #         self.blueprint.pop("label", None)
    #     elif isinstance(label, str):
    #         self.blueprint["label"] = label
    #     else:
    #         raise ValueError("`label` must be a string")

    # =========================================================================

    @property
    def label_color(self):
        # type: () -> dict
        """
        Sets the color of the Blueprint's label (title).

        TODO: make a more consistent way to read and write this data
        TODO: handle int values in [0, 255] range

        Args:
            r (float): Red component, 0.0 - 1.0
            g (float): Green component, 0.0 - 1.0
            b (float): Blue component, 0.0 - 1.0
            a (float): Alpha component, 0.0 - 1.0

        Raises:
            SchemaError if any of the values cannot be resolved to floats
        """
        return self.root.get("label_color", None)

    @label_color.setter
    def label_color(self, value):
        # type: (dict) -> None
        if value is None:
            self.root.pop("label_color", None)
        try:
            self.root["label_color"] = signatures.USER_COLOR.validate(value)
        except SchemaError:
            # TODO: more verbose
            raise TypeError("Invalid Color format")


    # def set_label_color(self, r = 1.0, g = 1.0, b = 1.0, a = 1.0):
    #     # type: (float, float, float, float) -> None
        
    #     data = signatures.COLOR.validate({"r": r, "g": g, "b": b, "a": a})
    #     self.blueprint["label_color"] = data

    # =========================================================================

    @property
    def icons(self):
        # type: () -> list
        """
        Sets the icon or icons associated with the blueprint.
        
        Args:
            signals: List of signal names to set as icons

        Raises:
            InvalidSignalID if any signal is not a string or unknown
        """
        return self.root.get("icons", None)

    @icons.setter
    def icons(self, value):
        # type: (list[str]) -> None
        if value is None:
            self.root["icons"] = None
            return
        
        self.root["icons"] = list()
        for i, signal in enumerate(value):
            out = {"index": i + 1 }
            out["signal"] = utils.signal_dict(signal)
            # This is probably redundant
            out = signatures.ICON.validate(out)
            self.root["icons"].append(out)

    # def set_icons(self, *signals):
    #     # type: (list[str]) -> None
        
    #     # Reset the current icon list, or initialize it if it doesn't exist
    #     self.blueprint["icons"] = list()

    #     for i, signal in enumerate(signals):
    #         out = {"index": i + 1 }
    #         out["signal"] = utils.signal_dict(signal)
    #         # This is probably redundant
    #         out = signatures.ICON.validate(out)
    #         self.blueprint["icons"].append(out)

    # =========================================================================

    @property
    def description(self):
        # type: () -> str
        """
        Sets the description for the blueprint.
        """
        return self.root.get("description", None)

    @description.setter
    def description(self, value):
        # type: (str) -> None
        if value is None:
            self.root.pop("description", None)
        elif isinstance(value, str):
            self.root["description"] = value
        else:
            raise TypeError("'description' must be a string or None")

    # def set_description(self, description):
    #     # type: (str) -> None
        
    #     # TODO: error checking
    #     self.blueprint["description"] = description

    # =========================================================================

    def set_version(self, major, minor, patch = 0, dev_ver = 0):
        # type: (int, int, int, int) -> None
        """
        Sets the intended version of the Blueprint.

        Args:
            major (int): Major version number
            minor (int): Minor version number
            patch (int): Patch number
            dev_ver (int): Development version
        """
        self.root["version"] = utils.encode_version(major, minor, patch, dev_ver)

    # =========================================================================

    @property
    def snapping_grid_size(self):
        # type: () -> dict
        """
        Sets the size of the snapping grid to use. The presence of this entry
        determines whether or not the Blueprint will have a snapping grid or 
        not.
        """
        return self.root.get("snap-to-grid", None)

    @snapping_grid_size.setter
    def snapping_grid_size(self, value):
        # type: (tuple) -> None
        if value is None:
            self.root.pop("snap-to-grid", None)
        else:
            try:
                self.root["snap-to-grid"] = signatures.POSITION.validate(value)
            except SchemaError:
                # TODO: more verbose
                raise TypeError("Invalid snap-to-grid format")

    # def set_snapping_grid_size(self, x, y=None):
    #     # type: (int, int) -> None
        
    #     # TODO: error checking
    #     if x is None:
    #         self.blueprint.pop("snap-to-grid", None)
    #     else:
    #         if y is None:
    #             y = x
    #         self.blueprint["snap-to-grid"] = {"x": x, "y": y}

    # =========================================================================

    @property
    def snapping_grid_position(self):
        # type: () -> list
        """
        Sets the position of the snapping grid. Offsets all of the
        positions of the entities by this amount.

        NOTE: This function does not offset each entities position until export!
        """
        return self._snapping_grid_position

    @snapping_grid_position.setter
    def snapping_grid_position(self, value):
        # type: (tuple[int, int]) -> None
        # TODO: fix this to handle more flexibly
        if value is None or isinstance(value, (list, tuple)):
            self._snapping_grid_position = value
        else:
            raise TypeError(
                "'snapping_grid_position' must be a sequence or None"
            )

    # def set_snapping_grid_position(self, x, y=None):
    #     # type: (int, int) -> None
        
    #     # TODO: error checking
    #     if x is None:
    #         self.grid_position = None
    #     else:
    #         if y is None:
    #             y = x
    #         self.grid_position = [x, y]

    # =========================================================================

    @property
    def absolute_snapping(self):
        # type: () -> bool
        """
        Set whether or not the blueprint uses absolute positioning or relative
        positioning for the snapping grid.
        """
        return self.root.get("absolute-snapping", None)

    @absolute_snapping.setter
    def absolute_snapping(self, value):
        # type: (bool) -> None
        if value is None:
            self.root.pop("absolute-snapping", None)
        elif isinstance(value, bool):
            self.root["absolute-snapping"] = value
        else:
            raise TypeError("'absolute_snapping' must be a bool or None")

    # def set_absolute_snapping(self, value):
    #     # type: (bool) -> None
        
    #     # TODO: error checking
    #     self.blueprint["absolute-snapping"] = value

    # =========================================================================

    @property
    def position_relative_to_grid(self):
        # type: () -> dict
        """
        TODO
        """
        return self.root.get("position-relative-to-grid", None)

    @position_relative_to_grid.setter
    def position_relative_to_grid(self, value):
        # type: (tuple[int, int]) -> None
        if value is None:
            self.root.pop("position-relative-to-grid", None)
        else:
            try:
                # TODO: fix this as well
                value = signatures.POSITION.validate(value)
                self.root["position-relative-to-grid"] = value
            except SchemaError:
                raise TypeError("Invalid position format")

    # def set_position_relative_to_grid(self, x, y=0):
    #     # type: (int, int) -> None
    #     """
    #     """
    #     if x is None:
    #         self.blueprint.pop("position-relative-to-grid", None)
    #     else:
    #         self.blueprint["position-relative-to-grid"] = {"x": x, "y": y}

    # =========================================================================
    # Blueprint functions
    # =========================================================================

    def rotate(self, angle):
        # type: (int) -> None
        """
        Rotate the blueprint by `angle`, if possible. `angle` is specified in
        terms of Direction Enum, meaning that a rotation of 1 is 45 degrees
        clockwise. Will fail if attempting to rotate entities to a direction
        they are unable to exist as.
        """
        raise NotImplementedError # TODO

    def flip(self, axis="horizontal", center=None):
        # type: (str, float) -> None
        """
        Flip the blueprint across `axis`, if possible. Specifying `center`
        changes flip location.
        """
        raise NotImplementedError # TODO

    # =========================================================================
    # Entity functions
    # =========================================================================

    def add_entity(self, entity, **kwargs):
        # type: (Union[EntityLike, str], **dict) -> None
        """
        """
        entity_id = None
        if "id" in kwargs:
            entity_id = kwargs["id"]
        elif hasattr(entity, "id"):
            entity_id = entity.id
        
        if entity_id is not None:
            if entity_id in self.entities.id_map: # Same ID!
                raise DuplicateIDError(entity_id)

        if isinstance(entity, str):
            entity = new_entity(entity, **kwargs)

        # DEEPCopy so we're not stupid
        entity_copy = copy.deepcopy(entity)

        # FIXME: is this necessary?
        if "id" in kwargs:
            entity_copy.id = kwargs["id"]

        # Warn if the placed entity is hidden
        if hasattr(entity_copy, "hidden") and entity_copy.hidden:
            warnings.warn(
                "{}".format(type(entity)),
                HiddenEntityWarning,
                stacklevel = 2
            )

        # Warn if the added entity overlaps with anything already in the 
        # blueprint
        results = self.find_entities(entity.get_area())
        #print(offset_aabb)
        if results:
            warnings.warn(
                "Added entity {} ({}) at {} intersects {} other entity(s)"
                .format(
                    entity.name,
                    type(entity).__name__, 
                    entity.position,
                    len(results)
                ),
                OverlappingEntitiesWarning,
                stacklevel = 2
            )

        # TODO: if the entity has any other restrictions placed on it, warn the 
        # user     

        # Add the entity to entities
        self.entities.append(entity_copy, entity_id)
        self.entity_hashmap.add(entity_copy)

        # Update dimensions
        self.collision_box = utils.extend_aabb(self.collision_box, entity_copy.collision_box)
        self.width, self.height = utils.aabb_to_dimensions(self.collision_box)

    def set_entity_id(self, index, new_id):
        """
        Swap the entities
        """
        # Get the entity and its id
        entity = self.entities[index]
        old_id = self.entities[index].id
        # Remove the id_map entry to the entity
        del self.entities.id_map[old_id]
        # Set the new entity id and reference
        self.entities[index].id = new_id
        self.entities.id_map[new_id] = entity

    # def set_entity_id(self, entity_number, id):
    #     # type: (int, str) -> None
    #     """
    #     Adds an `id` to an already added Entity.
    #     TODO: investigate if this is necessary, why not just do
    #     `blueprint.entities[number].set_id("whatever")`?
    #     """
    #     self.entity_numbers[id] = entity_number

    # def find_entity_by_id(self, id):
    #     # type: (str) -> EntityLike
    #     """
    #     Gets the entity with the corresponding `id` assigned to it. If you want
    #     to get the entity by index, use `blueprint.entities[i]` instead.
    #     TODO: would still be nice to be able to access entities with ids as
    #     `blueprint.entities["entity_id"]` which would automatically get the 
    #     corresponding entity number
    #     """
    #     return self.entities[self.entity_numbers[id]]

    def find_entity(self, name, position):
        # type: (str, tuple) -> EntityLike
        """
        Finds an entity with `name` at a grid position `position`.
        """
        results = self.entity_hashmap.get_on_point(position)
        return filter(lambda x: x.name == name, results)[0]

    def find_entities(self, aabb = None):
        # type: (list) -> list[EntityLike]
        """
        Returns a list of all entities within the area `aabb`. Works similiarly
        to `LuaSurface.find_entities`. If no `aabb` is provided then the 
        function simply returns all the entities in the blueprint.
        """
        if aabb is None:
            return self.entities

        return self.entity_hashmap.get_in_area(aabb)

    def find_entities_filtered(self, **kwargs):
        # type: (**dict) -> list[EntityLike]
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
        * limit: maximum number of entities to return
        * invert: Boolean, whether or not to invert the search selection
        """

        search_region = []
        if "position" in kwargs:
            if "radius" in kwargs:
                # Intersect entities with circle
                search_region = self.entity_hashmap.get_in_radius(kwargs["position"], kwargs["radius"])
            else:
                # Intersect entities with point
                search_region = self.entity_hashmap.get_on_point(kwargs["position"])
        elif "area" in kwargs:
            # Intersect entities with area
            search_region = self.entity_hashmap.get_in_area(kwargs["area"])
        else:
            search_region = self.entities

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

        # Keep track of how many
        limit = kwargs.pop("limit", None)

        count = 0
        def test(entity, count):
            if limit is not None and count >= limit:
                return False
            if names is not None and entity.name not in names:
                return False
            if types is not None and entity.type not in types:
                return False
            if directions is not None and entity.direction not in directions:
                return False
            count += 1 # FIXME: this probably doesnt work
            return True

        if "invert" in kwargs:
            return list(filter(lambda entity: not test(entity, count), search_region))
        else:
            return list(filter(lambda entity: test(entity, count), search_region))

    def pop_entity(self, entity_id):
        # type: (Union[int, str]) -> EntityLike
        """
        Removes and returns the entity at `entity_id` in `self.entities`. 
        `entity_id` can be either an int (its position in the list) or a string
        (its id).
        """
        if isinstance(entity_id, str):
            entity_id = self.entities.key_to_num[entity_id]
        
        self.entity_hashmap.remove(self.entities[entity_id])
        return self.entities.pop(entity_id)

    def remove_entity(self, entity):
        # type: (EntityLike) -> None
        """
        Removes the entity from the blueprint. `entity` must be equivalent to
        one of the entities located in the blueprint for the entity to be 
        removed.
        """
        self.entity_hashmap.remove(entity)
        self.entities.remove(entity)

    def add_power_connection(self, id1, id2, side = 1):
        # type: (Union[str, int], Union[str, int], int, int) -> None
        """
        Adds a copper wire power connection between two entities.
        """
        entity_1 = self.entities[id1]
        entity_2 = self.entities[id2]

        entity_1.add_power_connection(entity_2, side)

    def remove_power_connection(self, id1, id2, side = 1):
        # type: (Union[str, int], Union[str, int], int) -> None
        """
        Removes a copper wire power connection between two entities.
        """
        entity_1 = self.entities[id1]
        entity_2 = self.entities[id2]

        entity_1.remove_power_connection(entity_2, side)

    def add_circuit_connection(self, color, id1, id2, side1 = 1, side2 = 1):
        # type: (str, Union[str, int], Union[str, int], int, int) -> None
        """
        Adds a circuit wire connection between two entities.
        """
        if color not in {"red", "green"}:
            raise ValueError("'{}' is an invalid circuit wire color")

        entity_1 = self.entities[id1]
        entity_2 = self.entities[id2]

        # If either (or both) of the connected entities is a wall, make sure 
        # that they are both adjacent to a gate; If not, raise a warning
        if isinstance(entity_1, Wall) or isinstance(entity_2, Wall):
            if len(self.find_entities_filtered(
                position = entity_1.tile_position, radius = 1.25,
                type = "gate"
            )) == 0:
                warnings.warn(
                    "Circuit connected Wall entity has no adjacent gate",
                    UselessConnectionWarning,
                    stacklevel = 2
                )
            
        entity_1.add_circuit_connection(color, entity_2, side1, side2)

    def remove_circuit_connection(self, color, id1, id2, side1 = 1, side2 = 1):
        # type: (str, Union[str, int], Union[str, int], int, int) -> None
        """
        Adds a circuit wire connection between two entities.
        """
        
        entity_1 = self.entities[id1]
        entity_2 = self.entities[id2]

        entity_1.remove_circuit_connection(color, entity_2, side1, side2)

    # =========================================================================
    # Tile functions
    # =========================================================================

    def add_tile(self, tile_name, x, y, id = None):
        # type: (str, int, int, str) -> None
        """
        Add a tile to the Blueprint.
        """
        if id is not None:
            if id in self.tiles.id_map:
                raise DuplicateIDError(
                    "'{}' already used in blueprint tiles".format(id)
                )

        # if warning_not_filtered(OverlappingTilesWarning):
        tile = self.find_tile(x, y)
        if tile:
            warnings.warn(
                "Added tile overlaps '{}' tile at ({}, {});"
                .format(tile.name, tile.position["x"], tile.position["y"]),
                OverlappingTilesWarning,
                stacklevel = 2
            )
        
        new_tile = Tile(tile_name, x, y)
        self.tiles.append(new_tile)
        self.tile_hashmap.add(new_tile)

        # Update dimensions
        self.collision_box = utils.extend_aabb(self.collision_box, new_tile.collision_box)
        self.width, self.height = utils.aabb_to_dimensions(self.collision_box)

    def find_tile(self, x, y):
        # type: (int, int) -> Tile
        """
        """
        tiles = self.tile_hashmap.get_on_point((x + 0.5, y + 0.5))
        if len(tiles) != 0:
            return tiles[0]
            # for tile in tiles:
            #     if tile.position["x"] == x and tile.position["y"] == y:
            #         return tile
        else:
            return None

    # def find_tile_by_id(self, id):
    #     # type: (str) -> Tile
    #     """
    #     Gets the tile with the corresponding `id` assigned to it. If you want to
    #     get the tile by index, use `blueprint.tiles[i]` instead.
    #     """
    #     return self.tiles[self.tile_numbers[id]]

    def find_tiles_filtered(self, **kwargs):
        # type: (**dict) -> list[Tile]
        """
        Returns a filtered list of tiles within the blueprint. Works 
        similarly to `LuaSurface.find_tiles_filtered`. 

        Possible keywords include:
        * area: AABB to search in
        * position: grid position to search
        * radius: radius around position to search in
        * name: name or set of names, only entities with those names will be
        returned
        * limit: maximum number of entities to return
        """

        if "position" in kwargs and "radius" in kwargs:
            # Intersect entities with circle
            search_region = self.tile_hashmap.get_in_radius(kwargs["position"], kwargs["radius"])
        elif "area" in kwargs:
            # Intersect entities with area
            search_region = self.tile_hashmap.get_in_area(kwargs["area"])
        else:
            search_region = self.tiles

        if isinstance(kwargs.get("name", None), str):
            names = {kwargs.pop("name", None)}
        else:
            names = kwargs.pop("name", None)

        # Keep track of how many
        limit = kwargs.pop("limit", None)

        count = 0
        def test(entity, count):
            if limit is not None and count >= limit:
                return False
            if names is not None and entity.name not in names:
                return False
            count += 1 # FIXME: this probably doesnt work
            return True

        if "invert" in kwargs:
            return list(filter(lambda entity: not test(entity, count), search_region))
        else:
            return list(filter(lambda entity: test(entity, count), search_region))

    def remove_tile(self, name, x, y):
        # type: (str, int, int) -> Tile
        """
        """
        target_tile = Tile(name, x, y)
        self.tiles.remove(target_tile)
        self.tile_hashmap.remove(target_tile)

    # =========================================================================
    # Utility functions
    # =========================================================================

    def version_tuple(self):
        # type: () -> tuple(int, int, int, int)
        """
        Returns the version of the Blueprint as a 4-length tuple.
        """
        return utils.decode_version(self.root["version"])

    def version_string(self):
        # type: () -> str
        """
        Returns the version of the Blueprint in human-readable string.
        """
        version_tuple = utils.decode_version(self.root["version"])
        return utils.version_tuple_2_string(version_tuple)

    def to_dict(self):
        # type: () -> dict
        """
        Returns the blueprint as a dictionary. Intended for getting the 
        precursor to a Factorio blueprint string.
        """   

        out_dict = copy.deepcopy(self.root)

        # Convert entity objects into copies of their dict representation
        out_dict["entities"] = []
        i = 0
        for entity in self.entities:
            # out_dict["entities"][i] = copy.deepcopy(entity.to_dict())
            # out_dict["entities"][i]["entity_number"] = i + 1
            # Offset the entities position by snapping grid_position
            dict_result = entity.to_dict()
            if isinstance(dict_result, list):
                for result in dict_result:
                    out_dict["entities"].append(copy.deepcopy(result))
                    out_dict["entities"][i]["entity_number"] = i + 1
                    i += 1
                    # TODO: update entity_numbers with group elements
            elif isinstance(dict_result, dict):
                out_dict["entities"].append(copy.deepcopy(dict_result))
                out_dict["entities"][i]["entity_number"] = i + 1
                # Offset by snapping grid_position
                i += 1
            else:
                raise DraftsmanError(
                    "{}.to_dict() did not return either a dict or a"
                    "list of dicts".format(type(entity)))

        # Convert all tiles into dicts
        # TODO: maybe handle TileLike?
        for i, tile in enumerate(self.tiles):
            out_dict["tiles"][i] = copy.deepcopy(tile.to_dict())

        # Convert all schedules into dicts
        # TODO
        
        # Offset coordinate objects by snapping grid
        if self.grid_position is not None:
            # Offset Entities
            for entity in out_dict["entities"]:
                entity["position"]["x"] -= self.grid_position[0]
                entity["position"]["y"] -= self.grid_position[1]
            # Offset Tiles
            for tile in out_dict["tiles"]:
                tile["position"]["x"] -= self.grid_position[0]
                tile["position"]["y"] -= self.grid_position[1]

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
                                    point["entity_id"] = self.entities.key_to_num[old]+1
                    elif side in {"Cu0", "Cu1"}:
                        connection_points = connections[side]
                        for point in connection_points:
                            old = point["entity_id"]
                            if isinstance(old, str):
                                point["entity_id"] = self.entities.key_to_num[old]+1
            if "neighbours" in entity:
                neighbours = entity["neighbours"]
                for i, neighbour in enumerate(neighbours):
                    if isinstance(neighbour, str):
                        neighbours[i] = self.entities.key_to_num[neighbour]+1

        # Delete empty entries to compress as much as possible
        # TODO: use self.export dict instead
        # make another class, call it Exportable() and use it to subclass
        # EntityLike and Blueprint
        if len(out_dict["entities"]) == 0:
            del out_dict["entities"]
        if len(out_dict["tiles"]) == 0:
            del out_dict["tiles"]
        if len(out_dict["schedules"]) == 0:
            del out_dict["schedules"]

        # Make sure the final dictionary is valid
        #out_dict = signatures.BLUEPRINT.validate(out_dict)
        
        return out_dict

    def to_string(self):
        # type: () -> str
        """
        Returns the Blueprint as a Factorio blueprint string.
        """
        return utils.JSON_2_string({"blueprint": self.to_dict()})

    def __setitem__(self, key, value):
        self.root[key] = value

    def __getitem__(self, key):
        return self.root[key]

    def __str__(self):
        return "Blueprint" + json.dumps(self.to_dict(), indent=2)

    def _setup_defaults(self):
        """
        """
        # Init default values if none
        # These values always exist in a Blueprint object, but if they are empty
        # they are deleted from the final blueprint string
        if "entities" not in self.root:
            self.root["entities"] = IDList()
        if "tiles" not in self.root:
            self.root["tiles"] = IDList()
        if "schedules" not in self.root:
            self.root["schedules"] = list()
        if "version" not in self.root:
            maj, min, pat, dev = __factorio_version_info__
            self.root["version"] = utils.encode_version(maj, min, pat, dev)

        # Aliases
        self.entities   = self.root["entities"]
        self.tiles      = self.root["tiles"]
        self.schedules  = self.root["schedules"]

        # Internal stuff
        self.grid_position = None
        self.collision_box = [[0, 0], [0, 0]]
        self.width = 0
        self.height = 0

    def _load_entities_from_root(self):
        """
        Convert all entities to Entity objects and store them in a keylist.
        """
        loaded_entities = self.entities
        self.entities = IDList()
        for entity_dict in loaded_entities:
            rest_of_the_keys = copy.deepcopy(entity_dict)
            del rest_of_the_keys["name"] # TODO: change, this is clunky
            self.add_entity(entity_dict["name"], **rest_of_the_keys)


class BlueprintBook:
    """
    Factorio Blueprint Book.
    """
    def __init__(self, blueprint_string):
        # type: (**dict) -> None
        # blueprint_string = None
        # blueprints = []
        # Maybe just have one positional argument blueprints that can either be
        # blueprint string or list of blueprint objects?
        # Ensure that the blueprint loaded is actually the correct object type

        # add blueprints
        self.root = dict()
        self.root["blueprint_book"] = dict()

        self.blueprints = []

        # TODO: validate that blueprints are actually blueprints
        if blueprint_string is not None:
            self.load_from_string(blueprint_string)

        self.blueprint_book = self.root

    def load_from_string(self, blueprint_string):
        # type: (str) -> None
        pass # TODO

    def load_from_file(self, blueprint_file):
        # type: (FileIO) -> None
        pass # TODO

    # def set_metadata(self, **kwargs): # TODO: test
    #     # type: (**dict) -> None
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
    #             self.object[key] = value

    # =========================================================================
    # BlueprintBook functions
    # =========================================================================

    def set_label(self, label):
        # type: (str) -> None
        """
        Sets the Blueprint's label (title).

        Args:
            label (str): The new title of the blueprint
        """
        self.root["label"] = label

    def set_label_color(self, r = 1.0, g = 1.0, b = 1.0, a = 1.0):
        # type: (float, float, float, float) -> None
        """
        Sets the color of the Blueprint's label (title).

        Args:
            r (float): Red component, 0.0 - 1.0
            g (float): Green component, 0.0 - 1.0
            b (float): Blue component, 0.0 - 1.0
            a (float): Alpha component, 0.0 - 1.0
        """
        self.root["label_color"] = {"r": r, "g": g, "b": b, "a": a}

    def set_icons(self, signal_list):
        # type: (list) -> None
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
        self.root["icons"] = list()

        for i, signal in enumerate(signal_list):
            out = {"index": i + 1 }
            out["signal"] = utils.signal_dict(signal)
            self.root["icons"].append(out)

    def set_active_index(self, index):
        """
        Sets the active index (the currently selected blueprint) in the 
        BlueprintBook.
        """
        self.root["active_index"] = index

    def set_version(self, major, minor, patch = 0, dev_ver = 0):
        # type: (int, int, int, int) -> None
        """
        Sets the intended version of the Blueprint.

        Args:
            major (int): Major version number
            minor (int): Minor version number
            patch (int): Patch number
            dev_ver (int): Development version
        """
        self.object["version"] = utils.encode_version(major, minor, patch, dev_ver)

    def add_blueprint(self, blueprint):
        # type: (Blueprint) -> None
        """
        """
        # TODO: error checking
        self.blueprints.append(blueprint)

    def set_blueprint(self, index, blueprint):
        # type: (int, Blueprint) -> None
        """
        """
        # TODO: error checking
        self.blueprints[index] = blueprint

    # def get_blueprint(self, index):
    #     # type: (int) -> Blueprint
    #     """
    #     TODO: keep this function? why not just 
    #     `blueprintbook.blueprints[number]`?
    #     """
    #     return self.blueprints[index]

    def version_tuple(self):
        # type: () -> tuple(int, int, int, int)
        """
        Returns the version of the BlueprintBook as a 4-length tuple.
        """
        return utils.decode_version(self.root["version"])

    def version_string(self):
        # type: () -> str
        """
        Returns the version of the BlueprintBook in human-readable string.
        """
        version_tuple = utils.decode_version(self.root["version"])
        return utils.version_tuple_2_string(version_tuple)

    # =========================================================================
    # Utility functions
    # =========================================================================

    def to_dict(self):
        # type: () -> dict
        pass # TODO

    def to_string(self):
        # type: () -> str
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
        return "BlueprintBook" + json.dumps(self.root, indent=2)


def get_blueprintable_from_string(blueprint_string):
    # type: (str) -> Union[Blueprint, BlueprintBook]
    """
    Gets a Blueprintable object based off of the `blueprint_string`. A 
    'Blueprintable object' in this context either a Blueprint or a 
    BlueprintBook, depending on the particular string you passed in. This 
    function allows you generically accept either Blueprint strings or 
    BlueprintBook strings.

    Returns:
        Either a Blueprint or a BlueprintBook, depending on the input string.

    Raises:
        NameError: if the blueprint_string cannot be resolved to be a valid
        Blueprint or BlueprintBook.
    """
    blueprintable = utils.string_2_JSON(blueprint_string)
    if "blueprint" in blueprintable:
        return Blueprint(blueprint_string)
    elif "blueprint_book" in blueprintable:
        return BlueprintBook(blueprint_string)
    else:
        raise MalformedBlueprintStringError