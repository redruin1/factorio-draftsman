# blueprint.py
# -*- encoding: utf-8 -*-

# TODO: Add warnings for placement constraints on rails and rail signals
# TODO: Add groups (back)

"""
What are the parameters we need to check for when doing modifying entities within a blueprint?

id: when we change an entity's id, it has to change the key_map entry in KeyList.
position: when we change an entity's position, we have to check if the blueprint's dimensions/aabb changed.
    (And Group for that matter!)
"""

from __future__ import unicode_literals

from draftsman._factorio_version import __factorio_version_info__
from draftsman.classes.entitylike import EntityLike
from draftsman.classes.spatialhashmap import SpatialHashMap
from draftsman.constants import Direction
from draftsman.error import (
    IncorrectBlueprintTypeError,
    DuplicateIDError,
    DraftsmanError,
    UnreasonablySizedBlueprintError,
    BlueprintRotationError,
    BlueprintFlippingError,
)
from draftsman.entity import Wall, new_entity

from draftsman import signatures
from draftsman.tile import Tile
from draftsman import utils
from draftsman.warning import (
    HiddenEntityWarning,
    OverlappingEntitiesWarning,
    OverlappingTilesWarning,
    UselessConnectionWarning,
    DraftsmanWarning,
    RailAlignmentWarning,
)

try:  # pragma: no coverage
    from collections.abc import MutableSequence
except ImportError:  # pragma: no coverage
    from collections import MutableSequence
from builtins import int
import copy
import json
import math
from schema import SchemaError
import six
from typing import Any, Sequence, Union
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

# =============================================================================


class EntityList(MutableSequence):
    """
    TODO
    """

    @utils.reissue_warnings
    def __init__(self, blueprint, initlist=None):
        # type: (Blueprint, Any) -> None
        self.data = []
        self.key_map = {}
        self.key_to_idx = {}
        self.idx_to_key = {}

        self._blueprint = blueprint

        if initlist is not None:
            for elem in initlist:
                if isinstance(elem, EntityLike):
                    self.append(elem)
                else:
                    name = elem.pop("name")
                    self.append(name, **elem)

    @utils.reissue_warnings
    def append(self, entity, **kwargs):
        # type: (EntityLike, **dict) -> None
        """
        Appends the EntityLike to the end of the sequence.
        """
        self.insert(len(self.data), entity, **kwargs)

    @utils.reissue_warnings
    def insert(self, idx, entity, **kwargs):
        # type: (int, EntityLike, **dict) -> None
        """
        Inserts an element into the EntityList. If the added entity has an "id"
        attribute, the key_map is automatically set to point to the same entity.
        """
        # Determine the id of the input entity
        entity_id = None
        if "id" in kwargs:
            entity_id = kwargs["id"]
        elif hasattr(entity, "id"):
            entity_id = entity.id

        # Convert to Entity if constructed via keyword
        if isinstance(entity, six.string_types):
            entity = new_entity(six.text_type(entity), **kwargs)

        # Make sure were not causing any problems by putting this entity in
        self.check_entity(entity)

        # DEEPCopy so we're not stupid
        entity_copy = copy.deepcopy(entity)

        # Manage the EntityList
        self.data.insert(idx, entity_copy)
        self._shift_key_indices(idx, 1)
        if entity_id:
            # self.key_map[entity_id] = entity_copy
            # self.key_to_idx[entity_id] = idx
            # self.idx_to_key[idx] = entity_id
            self.set_key(entity_id, entity_copy)

        # Keep a reference in each EntityLike of the blueprint it's in
        entity_copy._blueprint = self._blueprint

        # Add the entity to the hashmap
        self._blueprint.entity_hashmap.add(entity_copy)

        # Update dimensions
        self._blueprint._area = utils.extend_aabb(
            self._blueprint._area, entity_copy.get_area()
        )
        (
            self._blueprint._tile_width,
            self._blueprint._tile_height,
        ) = utils.aabb_to_dimensions(self._blueprint.area)

        # Check the blueprint for unreasonable size
        if self._blueprint.tile_width > 10000 or self._blueprint.tile_height > 10000:
            raise UnreasonablySizedBlueprintError(
                "Current blueprint dimensions ({}, {}) exceeds the maximum size"
                " (10,000 x 10,000)".format(
                    self._blueprint.tile_width, self._blueprint.tile_height
                )
            )

    def __getitem__(self, item):
        # type: (Union[int, slice, str]) -> Union[EntityLike, list[EntityLike]]
        if isinstance(item, (int, slice)):
            return self.data[item]  # Raises IndexError
        else:
            return self.key_map[item]  # Raises KeyError

    @utils.reissue_warnings
    def __setitem__(self, item, value):
        # type: (Union[int, str], EntityLike) -> None
        # TODO: maybe make it possible for this function to take string keys?

        # Get the key and index of the item
        idx, key = self.get_pair(item)

        # Remove the entity from the hashmap
        self._blueprint.entity_hashmap.remove(self.data[idx])

        # Make sure were not causing any problems by putting this entity in
        self.check_entity(value)

        # Set the new data association in the list side
        self.data[idx] = value

        # Add the new entity to the hashmap
        self._blueprint.entity_hashmap.add(value)

        # If the element has a new id, set it to that
        if key:
            self.remove_key(key)
        if value.id:
            key = getattr(value, "id")
            self.set_key(key, value)

        # Add a reference to the container in the object
        value._blueprint = self._blueprint

        self._blueprint.recalculate_area()

    def __delitem__(self, item):
        # type: (Union[int, str]) -> None
        if isinstance(item, slice):
            # Get slice parameters
            start, stop, step = item.indices(len(self))
            for i in range(start, stop, step):
                # Get pair
                idx, key = self.get_pair(i)
                # Remove from hashmap
                self._blueprint.entity_hashmap.remove(self.data[idx])
                # Remove key pair
                self.remove_key(key)

            for i in range(start, stop, step):
                # Shift elements above down by slice.step
                self._shift_key_indices(i, -step)

            # Delete all entries in the main list
            del self.data[item]
        else:
            # Get pair
            if isinstance(item, int):
                item %= len(self.data)
            idx, key = self.get_pair(item)
            # Remove from hashmap
            self._blueprint.entity_hashmap.remove(self.data[idx])
            # Delete from list
            del self.data[idx]
            # Remove key pair
            self.remove_key(key)
            # Shift all entries above down by one
            self._shift_key_indices(idx, -1)

    def __len__(self):
        # type: () -> int
        return len(self.data)

    def check_entity(self, entity):
        # type: (EntityLike) -> None
        """
        Check to see if adding the entity to the blueprint would cause any
        problems. Raises errors and warnings.
        """
        if not isinstance(entity, EntityLike):
            raise TypeError(
                "Cannot set entry in EntityList to anything other than an " "EntityLike"
            )

        if entity.id is not None and entity.id in self.key_map:
            raise DuplicateIDError(entity.id)

        # Warn if the placed entity is hidden
        if getattr(entity, "hidden", False):
            warnings.warn("{}".format(type(entity)), HiddenEntityWarning, stacklevel=2)

        # Warn if the added entity overlaps with anything already in the
        # blueprint
        results = self._blueprint.find_entities(entity.get_area())
        # print(offset_aabb)
        # if results:
        for result in results:
            result_layers = result.collision_mask
            entity_layers = entity.collision_mask
            if len(result_layers.intersection(entity_layers)) > 0:
                warnings.warn(
                    "Added entity {} ({}) at {} intersects {}".format(
                        entity.name, type(entity).__name__, entity.position, result
                    ),
                    OverlappingEntitiesWarning,
                    stacklevel=2,
                )

        # TODO: if the entity has any other restrictions placed on it, warn the
        # user

    def remove_key(self, key):
        # type: (str) -> None
        """
        Removes the key from the key mapping dicts.
        """
        if key is not None:
            idx = self.key_to_idx[key]
            del self.key_map[key]
            del self.key_to_idx[key]
            del self.idx_to_key[idx]

    def set_key(self, key, value):
        # type: (str, Any) -> None
        """
        Sets a key in the key mapping structures such that they point to
        `value`.
        """
        idx = self.data.index(value)
        self.key_map[key] = value
        self.key_to_idx[key] = idx
        self.idx_to_key[idx] = key

    def get_pair(self, item):
        # type: (Union[int, str]) -> tuple[int, str]
        """
        Gets the converse key or index and returns them both as a pair.
        """
        if isinstance(item, six.string_types):
            return (self.key_to_idx[six.text_type(item)], item)
        else:
            return (item, self.idx_to_key.get(item, None))

    def _shift_key_indices(self, idx, amt):
        # type: (int, int) -> None
        """
        Shifts all of the key mappings above `idx` down by `amt`. Used when
        inserting or removing elements before the end, which moves what index
        each key should point to.
        """
        for key in self.key_map:
            old_idx = self.key_to_idx[key]
            if old_idx >= idx:
                new_idx = old_idx + amt
                self.key_to_idx[key] = new_idx
                del self.idx_to_key[old_idx]
                self.idx_to_key[new_idx] = key


# =============================================================================


class TileList(MutableSequence):
    def __init__(self, blueprint, initlist=None):
        # type: (Blueprint, list[Tile]) -> None
        self.data = []
        self._blueprint = blueprint
        if initlist is not None:
            for elem in initlist:
                self.append(elem)

    def append(self, tile, **kwargs):
        # type: (EntityLike, **dict) -> None
        """
        Appends the Tile to the end of the sequence.
        """
        self.insert(len(self.data), tile, **kwargs)

    def insert(self, idx, tile, **kwargs):
        # type: (int, EntityLike, **dict) -> None
        """
        Inserts an element into the TileList.
        """
        if isinstance(tile, six.string_types):
            tile_copy = Tile(six.text_type(tile), **kwargs)
        else:
            tile_copy = copy.deepcopy(tile)

        # Check tile
        self.check_tile(tile_copy)

        # Manage TileList
        self.data.insert(idx, tile_copy)

        # Keep a reference of the parent blueprint in the tile
        tile_copy._blueprint = self._blueprint

        # Add to hashmap
        self._blueprint.tile_hashmap.add(tile_copy)

        # Update dimensions
        self._blueprint._area = utils.extend_aabb(
            self._blueprint._area, tile_copy.get_area()
        )
        (
            self._blueprint._tile_width,
            self._blueprint._tile_height,
        ) = utils.aabb_to_dimensions(self._blueprint.area)

        # Check the blueprint for unreasonable size
        if self._blueprint.tile_width > 10000 or self._blueprint.tile_height > 10000:
            raise UnreasonablySizedBlueprintError(
                "Current blueprint dimensions ({}, {}) exceeds the maximum size"
                " (10,000 x 10,000)".format(
                    self._blueprint.tile_width, self._blueprint.tile_height
                )
            )

    def __getitem__(self, idx):
        return self.data[idx]

    def __setitem__(self, idx, value):
        # type: (int, Tile) -> None

        # Remove from hashmap
        self._blueprint.tile_hashmap.remove(self.data[idx])

        # Check tile
        self.check_tile(value)

        # Add a reference to the container in the object
        value._blueprint = self._blueprint

        # Manage the TileList
        self.data[idx] = value

        # Add to hashmap
        self._blueprint.tile_hashmap.add(value)

        self._blueprint.recalculate_area()

    def __delitem__(self, idx):
        del self.data[idx]

    def __len__(self):
        return len(self.data)

    def check_tile(self, tile):
        # type: (Tile) -> None
        if not isinstance(tile, Tile):
            raise TypeError(
                "Cannot set entry in TileList to anything other than a Tile"
            )

        x, y = (tile.position["x"], tile.position["y"])
        tile_in_same_spot = self._blueprint.find_tile(x, y)
        if tile_in_same_spot:
            warnings.warn(
                "Added tile overlaps '{}' tile at ({}, {});".format(
                    tile.name, tile.position["x"], tile.position["y"]
                ),
                OverlappingTilesWarning,
                stacklevel=2,
            )


# =============================================================================


# TODO
# class ScheduleList(MutableSequence):
#     """
#     """
#     def __init__(self, blueprint, initlist = None):
#         # type: (Blueprint, list) -> None
#         self.data = []

#         self._blueprint = blueprint

#         if initlist is not None:
#             for elem in initlist:
#                 self.append(elem)

#     def insert(self, idx, value):
#         # type: (int, dict) -> None
#         self.check_schedule(value)

#         self.data.insert(idx, value)

#     def __getitem__(self, item):
#         # type: (int) -> dict
#         return self.data[item]

#     def __setitem__(self, item, value):
#         # type: (int, dict) -> None
#         self.check_schedule(value)

#         self.data[item] = value

#     def __delitem__(self, item):
#         # type: (Union[int, slice]) -> None
#         del self.data[item]

#     def __len__(self):
#         # type: () -> int
#         return len(self.data)

#     def check_schedule(self, schedule):
#         # type: (dict) -> None
#         """
#         Check to make sure that a schedule matches the correct format.
#         """
#         # if not isinstance(schedule, Schedule):
#         #     return
#         try:
#             schedule = signatures.SCHEDULE.validate(schedule)
#         except SchemaError:
#             # TODO:
#             raise ValueError("Incorrect schedule format")

# =============================================================================


class Blueprint(object):
    """
    Factorio Blueprint class.
    """

    # =========================================================================
    # Constructors
    # =========================================================================

    @utils.reissue_warnings
    def __init__(self, blueprint=None):
        # type: (dict) -> None
        """
        Creates a Blueprint class. Will load the data from `blueprint_string`
        if provided, otherwise initializes with defaults.

        Args:
            blueprint_string (str): Factorio-format blueprint string
        """
        if blueprint is None:
            self.setup()
        elif isinstance(blueprint, six.string_types):
            self.load_from_string(blueprint)
        elif isinstance(blueprint, dict):
            self.setup(**blueprint)
        else:
            raise TypeError("'blueprint' must be a str, dict, or None")

    @utils.reissue_warnings
    def load_from_string(self, blueprint_string):
        # type: (str) -> None
        """
        Load the Blueprint with the contents of `blueprint_string`.

        Args:
            blueprint_string (str): Factorio-encoded blueprint string
        """
        root = utils.string_to_JSON(blueprint_string)
        # Ensure that the blueprint string actually points to a blueprint
        if "blueprint" not in root:
            raise IncorrectBlueprintTypeError

        self.setup(**root["blueprint"])

    @utils.reissue_warnings
    def setup(self, **kwargs):
        """
        Setup the Blueprint's parameters as keywords.
        """
        self.root = dict()

        # Item (type identifier)
        self.root["item"] = "blueprint"
        kwargs.pop("item", None)

        ### METADATA ###

        if "label" in kwargs:
            self.label = kwargs.pop("label")

        if "label_color" in kwargs:
            self.label_color = kwargs.pop("label_color")

        if "icons" in kwargs:
            self.icons = kwargs.pop("icons")

        if "version" in kwargs:
            self.version = kwargs.pop("version")
        else:
            self.version = utils.encode_version(*__factorio_version_info__)

        # Snapping grid
        if "snap-to-grid" in kwargs:
            self.snapping_grid_size = kwargs.pop("snap-to-grid")
        elif "snapping_grid_size" in kwargs:
            self.snapping_grid_size = kwargs.pop("snapping_grid_size")

        self.snapping_grid_position = None
        if "snapping_grid_position" in kwargs:
            self.snapping_grid_position = kwargs.pop("snapping_grid_position")

        if "absolute-snapping" in kwargs:
            self.absolute_snapping = kwargs.pop("absolute-snapping")
        elif "absolute_snapping" in kwargs:
            self.absolute_snapping = kwargs.pop("absolute_snapping")

        if "position-relative-to-grid" in kwargs:
            self.position_relative_to_grid = kwargs.pop("position-relative-to-grid")
        elif "position_relative_to_grid" in kwargs:
            self.position_relative_to_grid = kwargs.pop("position_relative_to_grid")

        ### DATA ###

        # Create spatial hashing objects to make spatial queries much quicker
        self.tile_hashmap = SpatialHashMap()
        self.entity_hashmap = SpatialHashMap()

        # Data lists
        if "entities" in kwargs:
            self.root["entities"] = EntityList(self, kwargs.pop("entities"))
        else:
            self.root["entities"] = EntityList(self)

        if "tiles" in kwargs:
            self.root["tiles"] = TileList(self, kwargs.pop("tiles"))
        else:
            self.root["tiles"] = TileList(self)

        if "schedules" in kwargs:
            self.root["schedules"] = kwargs.pop("schedules")
        else:
            self.root["schedules"] = []

        ### INTERNAL ###

        self._area = None
        self._tile_width = 0
        self._tile_height = 0

        # Issue warnings for any keyword not recognized by Blueprint
        for unused_arg in kwargs:
            warnings.warn(
                "{} has no attribute '{}'".format(type(self), unused_arg),
                DraftsmanWarning,
                stacklevel=2,
            )

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
        elif isinstance(value, six.string_types):
            self.root["label"] = six.text_type(value)
        else:
            raise TypeError("`label` must be a string or None")

    # =========================================================================

    @property
    def label_color(self):
        # type: () -> dict
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
        return self.root.get("label_color", None)

    @label_color.setter
    def label_color(self, value):
        # type: (dict) -> None
        if value is None:
            self.root.pop("label_color", None)
            return

        try:
            self.root["label_color"] = signatures.COLOR.validate(value)
        except SchemaError:
            # TODO: more verbose
            raise TypeError("Invalid Color format")

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
        # type: (list[Union[dict, str]]) -> None
        if value is None:
            self.root.pop("icons", None)
            return

        self.root["icons"] = []
        for i, signal in enumerate(value):
            if isinstance(signal, six.string_types):
                out = {"index": i + 1}
                out["signal"] = utils.signal_dict(six.text_type(signal))
            elif isinstance(signal, dict):
                try:
                    out = signatures.ICON.validate(signal)
                except SchemaError:
                    # TODO: more verbose
                    raise ValueError("Incorrect icon format")
            else:
                raise TypeError("Icon entries must be either a str or a dict")

            self.root["icons"].append(out)

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
        elif isinstance(value, six.string_types):
            self.root["description"] = six.text_type(value)
        else:
            raise TypeError("'description' must be a string or None")

    # =========================================================================

    @property
    def version(self):
        # type: () -> int
        """
        The version of the Blueprint.
        """
        return self.root.get("version", None)

    @version.setter
    def version(self, value):
        # type: (Union[int, Sequence[int]]) -> None
        if value is None:
            self.root.pop("version", None)
        elif isinstance(value, int):
            self.root["version"] = value
        elif isinstance(value, Sequence):
            self.root["version"] = utils.encode_version(*value)
        else:
            raise TypeError("'version' must be an int, sequence of ints or None")

    # =========================================================================

    @property
    def snapping_grid_size(self):
        # type: () -> dict
        """
        Sets the size of the snapping grid to use. The presence of this entry
        determines whether or not the Blueprint will have a snapping grid or
        not.
        TODO: change the format to work with tuples
        """
        return self.root.get("snap-to-grid", None)

    @snapping_grid_size.setter
    def snapping_grid_size(self, value):
        # type: (Union[dict, Sequence]) -> None
        if value is None:
            self.root.pop("snap-to-grid", None)
            return

        try:
            self.root["snap-to-grid"] = {
                "x": math.floor(value["x"]),
                "y": math.floor(value["y"]),
            }
        except TypeError:
            self.root["snap-to-grid"] = {
                "x": math.floor(value[0]),
                "y": math.floor(value[1]),
            }

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
        # type: (Union[dict, Sequence]) -> None
        if value is None:
            self._snapping_grid_position = value
            return

        try:
            self._snapping_grid_position = {
                "x": math.floor(value["x"]),
                "y": math.floor(value["y"]),
            }
        except TypeError:
            self._snapping_grid_position = {
                "x": math.floor(value[0]),
                "y": math.floor(value[1]),
            }

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
        # type: (Union[dict, Sequence]) -> None
        if value is None:
            self.root.pop("position-relative-to-grid", None)
            return

        try:
            self.root["position-relative-to-grid"] = {
                "x": math.floor(value["x"]),
                "y": math.floor(value["y"]),
            }
        except TypeError:
            self.root["position-relative-to-grid"] = {
                "x": math.floor(value[0]),
                "y": math.floor(value[1]),
            }

    # =========================================================================

    @property
    def entities(self):
        # type: () -> EntityList
        """
        A list of the Blueprint's entities.

        An EntityList has all of the functionality of a normal list:

        `example`

        EntityList also allows the user to access entities by their id as index:

        `example`
        """
        return self.root["entities"]

    @entities.setter
    def entities(self, value):
        # type: (list[EntityLike]) -> None
        if value is None:
            self.root["entities"] = EntityList(self)
        elif isinstance(value, list):
            self.root["entities"] = EntityList(self, value)
        else:
            raise TypeError("'entities' must be a list or None")

    # =========================================================================

    @property
    def tiles(self):
        # type: () -> TileList
        """
        A list of the Blueprint's tiles.
        """
        return self.root["tiles"]

    @tiles.setter
    def tiles(self, value):
        # type: (list[Tile]) -> None
        if value is None:
            self.root["tiles"] = TileList(self)
        elif isinstance(value, list):
            self.root["tiles"] = TileList(self, value)
        else:
            raise TypeError("'tiles' must be a list or None")

    # =========================================================================

    @property
    def schedules(self):
        # type: () -> list
        """
        A list of the Blueprint's schedules.
        """
        return self.root["schedules"]

    @schedules.setter
    def schedules(self, value):
        # type: (list) -> None
        if value is None:
            self.root["schedules"] = []
        elif isinstance(value, list):
            try:
                self.root["schedules"] = signatures.SCHEDULES.validate(value)
            except SchemaError:
                # TODO: more verbose
                raise ValueError("Incorrect schedules format")
        else:
            raise TypeError("'schedules' must be a list or None")

    # =========================================================================

    @property
    def area(self):
        # type: () -> list[list[float]]
        """
        Read only
        """
        return self._area

    # =========================================================================

    @property
    def tile_width(self):
        # type: () -> int
        """
        Read only
        """
        return self._tile_width

    # =========================================================================

    @property
    def tile_height(self):
        # type: () -> int
        """
        Read only
        """
        return self._tile_height

    # =========================================================================

    # @property
    # def flippable(self):
    #     # type: () -> bool
    #     """
    #     Read only
    #     """
    #     for entity in self.entities:
    #         if not entity.flippable:
    #             return False

    #     return True

    # =========================================================================

    @property
    def double_grid_aligned(self):
        # type: () -> bool
        """
        Read only
        """
        for entity in self.entities:
            if entity.double_grid_aligned:
                return True

        return False

    # =========================================================================
    # Blueprint functions
    # =========================================================================

    def translate(self, x, y):
        # type: (int, int) -> None
        """
        Translates all entities and tiles in the blueprint by an amount.
        """
        # Warn if attempting to translate by an odd amount when containing
        # double-grid-aligned entities
        if self.double_grid_aligned and (x % 2 == 1 or y % 2 == 1):
            warnings.warn(
                "Attempting to translate an odd number of tiles when this "
                "blueprint contains double grid-aligned entities; Their "
                "positions will be cast to the nearest grid square on export",
                RailAlignmentWarning,
                stacklevel=2,
            )

        # Entities
        for entity in self.entities:
            # Remove from hashmap
            self.entity_hashmap.remove(entity)

            entity._blueprint = None

            # Change entity position
            entity.position = (entity.position["x"] + x, entity.position["y"] + y)

            entity._blueprint = self

            # Re-add to hashmap
            self.entity_hashmap.add(entity)

        # Tiles
        for tile in self.tiles:
            # Remove from hashmap
            self.tile_hashmap.remove(tile)

            tile._blueprint = None

            # Change entity position
            tile.position["x"] += x
            tile.position["y"] += y

            tile._blueprint = self

            # Re-add to hashmap
            self.tile_hashmap.add(tile)

        self.recalculate_area()

    def rotate(self, angle):
        # type: (int) -> None
        """
        Rotate the blueprint by `angle`, if possible. Operates the same as
        pressing 'r' with a blueprint selected.
        ``angle`` is specified in terms of Direction Enum, meaning that a
        rotation of 2 is 90 degrees clockwise.
        Because eight-way rotatable entities exist in a weird gray area, this
        function behaves like feature in game and only rotates on 90 degree
        intervals. Attempting to rotate the blueprint an odd amount raises
        an :py:class:`draftsman.error.RotationError`.
        """

        angle = angle % 8

        if angle % 2 == 1:
            raise BlueprintRotationError(
                "Blueprints cannot be rotated by an odd number"
            )

        matrices = {
            0: [1, 0, 0, 1],
            2: [0, 1, -1, 0],
            4: [-1, 0, 0, -1],
            6: [0, -1, 1, 0],
        }
        matrix = matrices[angle]

        for entity in self.entities:
            # Remove from hashmap
            self.entity_hashmap.remove(entity)

            # Make a (separate!) copy of the position to transform
            pos = [entity.position["x"], entity.position["y"]]

            entity._blueprint = None

            # Alter the direction
            if entity.rotatable:
                entity.direction += angle
            # Alter (both) the position(s)
            entity.position = (
                pos[0] * matrix[0] + pos[1] * matrix[2],
                pos[0] * matrix[1] + pos[1] * matrix[3],
            )

            entity._blueprint = self

            # Re-add to hashmap
            self.entity_hashmap.add(entity)

        for tile in self.tiles:
            # Remove from hashmap
            self.tile_hashmap.remove(tile)

            tile._blueprint = None

            # Make a (separate!) copy of the position to transform
            # With tiles we rotate from their center
            pos = [tile.position["x"] + 0.5, tile.position["y"] + 0.5]
            # Alter the position
            tile.position = (
                pos[0] * matrix[0] + pos[1] * matrix[2] - 0.5,
                pos[0] * matrix[1] + pos[1] * matrix[3] - 0.5,
            )

            tile._blueprint = self

            # Re-add to hashmap
            self.tile_hashmap.add(tile)

        self.recalculate_area()

    def flip(self, direction="horizontal"):
        # type: (str, float) -> None
        """
        Flip the blueprint across `axis`, if possible.

        .. WARNING::

            **This function is not "Factorio-safe" and is currently under
            development.** The function still operates, though it will not
            throw ``BlueprintFlippingError`` when the blueprint contains
            entities that cannot be flipped. Proceed with caution.
        """
        # Prevent the blueprint from being flipped if it contains entities that
        # cannot be flipped
        # if not self.flippable:
        #     raise BlueprintFlippingError("Blueprint cannot be flipped")

        if direction not in {"horizontal", "vertical"}:
            raise ValueError("'direction' must be either 'horizontal' or 'vertical'")

        matrices = {"horizontal": [-1, +1], "vertical": [+1, -1]}
        matrix = matrices[direction]

        for entity in self.entities:
            # Remove from hashmap
            self.entity_hashmap.remove(entity)

            entity._blueprint = None

            # Make a (separate!) copy of the position to transform
            pos = [entity.position["x"], entity.position["y"]]
            # Alter the direction
            if entity.rotatable:
                if direction == "horizontal":
                    entity.direction += ((-2 * (entity.direction - 4)) % 8) % 8
                else:  # direction == "vertical":
                    entity.direction += (((-2 * entity.direction) % 8) - 4) % 8

            # Alter (both) the position(s)
            entity.position = (pos[0] * matrix[0], pos[1] * matrix[1])

            entity._blueprint = self

            # Re-add to hashmap
            self.entity_hashmap.add(entity)

        for tile in self.tiles:
            # Remove from hashmap
            self.tile_hashmap.remove(tile)

            tile._blueprint = None

            # Make a (separate!) copy of the position to transform
            # With tiles we flip from their center
            pos = [tile.position["x"] + 0.5, tile.position["y"] + 0.5]
            # Alter the position
            tile.position = (pos[0] * matrix[0] - 0.5, pos[1] * matrix[1] - 0.5)

            tile._blueprint = self

            # Re-add to hashmap
            self.tile_hashmap.add(tile)

        self.recalculate_area()

    # =========================================================================
    # Entity functions
    # =========================================================================

    def find_entity(self, name, position):
        # type: (str, tuple) -> EntityLike
        """
        Finds an entity with `name` at a grid position `position`.
        """
        results = self.entity_hashmap.get_on_point(position)
        try:
            return list(filter(lambda x: x.name == name, results))[0]
        except IndexError:
            return None

    def find_entities(self, aabb=None):
        # type: (list) -> list[EntityLike]
        """
        Returns a list of all entities within the area `aabb`. Works similiarly
        to `LuaSurface.find_entities`. If no `aabb` is provided then the
        function simply returns all the entities in the blueprint.
        """
        if aabb is None:
            return list(self.entities)

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
                search_region = self.entity_hashmap.get_in_radius(
                    kwargs["radius"], kwargs["position"]
                )
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
        if isinstance(kwargs.get("direction", None), int):
            directions = {kwargs.pop("direction", None)}
        else:
            directions = kwargs.pop("direction", None)

        # Keep track of how many
        limit = kwargs.pop("limit", len(search_region))

        def test(entity):
            if names is not None and entity.name not in names:
                return False
            if types is not None and entity.type not in types:
                return False
            if (
                directions is not None
                and getattr(entity, "direction", None) not in directions
            ):
                return False
            return True

        if kwargs.get("invert", None):
            return list(filter(lambda entity: not test(entity), search_region))[:limit]
        else:
            return list(filter(lambda entity: test(entity), search_region))[:limit]

    def add_power_connection(self, id1, id2, side=1):
        # type: (Union[str, int], Union[str, int], int, int) -> None
        """
        Adds a copper wire power connection between two entities.
        """
        entity_1 = self.entities[id1]
        entity_2 = self.entities[id2]

        entity_1.add_power_connection(entity_2, side)

    def remove_power_connection(self, id1, id2, side=1):
        # type: (Union[str, int], Union[str, int], int) -> None
        """
        Removes a copper wire power connection between two entities.
        """
        entity_1 = self.entities[id1]
        entity_2 = self.entities[id2]

        entity_1.remove_power_connection(entity_2, side)

    def add_circuit_connection(self, color, id1, id2, side1=1, side2=1):
        # type: (str, Union[str, int], Union[str, int], int, int) -> None
        """
        Adds a circuit wire connection between two entities.
        """
        entity_1 = self.entities[id1]
        entity_2 = self.entities[id2]

        # TODO: If either (or both) of the entities are Walls, raise a warning
        # if they are not directly next to a gate

        entity_1.add_circuit_connection(color, entity_2, side1, side2)

    def remove_circuit_connection(self, color, id1, id2, side1=1, side2=1):
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

    def find_tile(self, x, y):
        # type: (int, int) -> Tile
        """ """
        tiles = self.tile_hashmap.get_on_point((x + 0.5, y + 0.5))
        try:
            return tiles[0]
        except IndexError:
            return None

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
            search_region = self.tile_hashmap.get_in_radius(
                kwargs["radius"], kwargs["position"]
            )
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
        limit = kwargs.pop("limit", len(search_region))

        def test(entity):
            if names is not None and entity.name not in names:
                return False
            return True

        if kwargs.get("invert", False):
            return list(filter(lambda entity: not test(entity), search_region))[:limit]
        else:
            return list(filter(lambda entity: test(entity), search_region))[:limit]

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
        return utils.version_tuple_to_string(version_tuple)

    def recalculate_area(self):
        # type: () -> None
        """
        Recalculates the dimensions of the area and tile_width and
        height. Called when an EntityLike or Tile object is altered or removed.
        """
        self._area = None
        for entity in self.entities:
            self._area = utils.extend_aabb(self._area, entity.get_area())

        for tile in self.tiles:
            self._area = utils.extend_aabb(self._area, tile.get_area())

        self._tile_width, self._tile_height = utils.aabb_to_dimensions(self._area)

        # Check the blueprint for unreasonable size
        if self.tile_width > 10000 or self.tile_height > 10000:
            raise UnreasonablySizedBlueprintError(
                "Current blueprint dimensions ({}, {}) exceeds the maximum size"
                " (10,000 x 10,000)".format(self.tile_width, self.tile_height)
            )

    def to_dict(self):
        # type: () -> dict
        """
        Returns the blueprint as a dictionary. Intended for getting the
        precursor to a Factorio blueprint string before encoding and compression
        takes place.
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
            # if isinstance(dict_result, list):
            #     for result in dict_result:
            #         out_dict["entities"].append(copy.deepcopy(result))
            #         out_dict["entities"][i]["entity_number"] = i + 1
            #         i += 1
            #         # TODO: update entity_numbers with group elements
            if isinstance(dict_result, dict):
                out_dict["entities"].append(copy.deepcopy(dict_result))
                out_dict["entities"][i]["entity_number"] = i + 1
                # Offset by snapping grid_position
                i += 1
            else:
                raise DraftsmanError(
                    "{}.to_dict() did not return either a dict or a"
                    "list of dicts".format(type(entity))
                )

        # Convert all tiles into dicts
        # TODO: maybe handle TileLike?
        out_dict["tiles"] = []
        for tile in self.tiles:
            out_dict["tiles"].append(copy.deepcopy(tile.to_dict()))

        # Convert all schedules into dicts
        # TODO

        # Offset coordinate objects by snapping grid
        if self.snapping_grid_position is not None:
            # Offset Entities
            for entity in out_dict["entities"]:
                entity["position"]["x"] -= self.snapping_grid_position["x"]
                entity["position"]["y"] -= self.snapping_grid_position["y"]
            # Offset Tiles
            for tile in out_dict["tiles"]:
                tile["position"]["x"] -= self.snapping_grid_position["x"]
                tile["position"]["y"] -= self.snapping_grid_position["y"]

        # Change all connections to use entity_number
        # This could be cleaner
        for entity in out_dict["entities"]:
            if "connections" in entity:  # Wire connections
                connections = entity["connections"]
                for side in connections:
                    if side in {"1", "2"}:
                        for color in connections[side]:
                            connection_points = connections[side][color]
                            for point in connection_points:
                                old = point["entity_id"]
                                if isinstance(old, six.text_type):
                                    point["entity_id"] = (
                                        self.entities.key_to_idx[old] + 1
                                    )

                    elif side in {"Cu0", "Cu1"}:  # pragma: no branch
                        connection_points = connections[side]
                        for point in connection_points:
                            old = point["entity_id"]
                            if isinstance(old, six.text_type):
                                point["entity_id"] = self.entities.key_to_idx[old] + 1

            if "neighbours" in entity:  # Power pole connections
                neighbours = entity["neighbours"]
                for i, neighbour in enumerate(neighbours):
                    if isinstance(neighbour, six.text_type):
                        neighbours[i] = self.entities.key_to_idx[neighbour] + 1

        # Change all locomotive names to use entity_number
        for schedule in out_dict["schedules"]:
            for i, locomotive in enumerate(schedule["locomotives"]):
                if isinstance(locomotive, six.text_type):
                    schedule["locomotives"][i] = (
                        self.entities.key_to_idx[locomotive] + 1
                    )

        # Delete empty entries to compress as much as possible
        if len(out_dict["entities"]) == 0:
            del out_dict["entities"]
        if len(out_dict["tiles"]) == 0:
            del out_dict["tiles"]
        if len(out_dict["schedules"]) == 0:
            del out_dict["schedules"]

        return {"blueprint": out_dict}

    def to_string(self):  # pragma: no coverage
        # type: () -> str
        """
        Returns the Blueprint as a Factorio blueprint string.
        """
        return utils.JSON_to_string(self.to_dict())

    def __setitem__(self, key, value):
        self.root[key] = value

    def __getitem__(self, key):
        return self.root[key]

    def __str__(self):  # pragma: no coverage
        return "<Blueprint>" + json.dumps(self.to_dict()["blueprint"], indent=2)
