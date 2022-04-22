# blueprint.py
# -*- encoding: utf-8 -*-

# TODO: Add warnings for placement constraints on rails and rail signals

"""
What are the parameters we need to check for when doing modifying entities within a blueprint?

id: when we change an entity's id, it has to change the key_map entry in KeyList.
position: when we change an entity's position, we have to check if the blueprint's dimensions/aabb changed.
    (And Group for that matter!)

TODO: documentation
"""

from __future__ import unicode_literals

from draftsman._factorio_version import __factorio_version_info__
from draftsman.classes.entitylike import EntityLike
from draftsman.classes.entitylist import EntityList
from draftsman.classes.tilelist import TileList
from draftsman.classes.transformable import Transformable
from draftsman.classes.collection import EntityCollection, TileCollection
from draftsman.classes.spatialhashmap import SpatialHashMap
from draftsman.error import (
    DraftsmanError,
    IncorrectBlueprintTypeError,
    UnreasonablySizedBlueprintError,
)
from draftsman import signatures
from draftsman.tile import Tile
from draftsman import utils
from draftsman.warning import DraftsmanWarning

from draftsman.data.signals import signal_dict

from builtins import int
from copy import deepcopy
import json
import math
from schema import SchemaError
import six
from typing import Sequence, Union
import warnings

# import weakref


class Blueprint(Transformable, TileCollection, EntityCollection):
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
        self._tile_hashmap = SpatialHashMap()
        self._entity_hashmap = SpatialHashMap()

        # Data lists
        if "entities" in kwargs:
            # self.root["entities"] = EntityList(self, kwargs.pop("entities"))
            self.entities = EntityList(self, kwargs.pop("entities"))
        else:
            # self.root["entities"] = EntityList(self)
            self.entities = EntityList(self)

        if "tiles" in kwargs:
            # self.root["tiles"] = TileList(self, kwargs.pop("tiles"))
            self.tiles = TileList(self, kwargs.pop("tiles"))
        else:
            # self.root["tiles"] = TileList(self)
            self.tiles = TileList(self)

        if "schedules" in kwargs:
            # self.root["schedules"] = kwargs.pop("schedules")
            self.schedules = kwargs.pop("schedules")
        else:
            # self.root["schedules"] = []
            self.schedules = []

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
                out["signal"] = signal_dict(six.text_type(signal))
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
            self._entity_hashmap.clear()
            self.root["entities"].clear()
        elif isinstance(value, list):
            self._entity_hashmap.clear()
            self.root["entities"] = EntityList(self, value)
        elif isinstance(value, EntityList):
            # TODO: what to do with entity_hashmap?
            value._parent = self  # Make sure the parent is correct
            self.root["entities"] = value
        else:
            raise TypeError("'entities' must be an EntityList, list, or None")

    def on_entity_insert(self, entitylike):
        # type: (EntityLike) -> None
        """ """
        # Add to hashmap (as well as any children)
        self.entity_hashmap.recursively_add(entitylike)

        # Update dimensions
        self._area = utils.extend_aabb(self._area, entitylike.get_area())
        (
            self._tile_width,
            self._tile_height,
        ) = utils.aabb_to_dimensions(self.area)
        # Check the blueprint for unreasonable size
        if self.tile_width > 10000 or self.tile_height > 10000:
            raise UnreasonablySizedBlueprintError(
                "Current blueprint dimensions ({}, {}) exceeds the maximum size"
                " (10,000 x 10,000)".format(self.tile_width, self.tile_height)
            )

    def on_entity_set(self, old_entitylike, new_entitylike):
        # type: (EntityLike, EntityLike) -> None
        """ """
        # Remove the entity and its children
        self.entity_hashmap.recursively_remove(old_entitylike)
        # Add the new entity and its children
        self.entity_hashmap.recursively_add(new_entitylike)

    def on_entity_remove(self, entitylike):
        # type: (EntityLike) -> None
        """ """
        # Remove the entity and its children
        self.entity_hashmap.recursively_remove(entitylike)

    # =========================================================================

    @property
    def entity_hashmap(self):
        # type: () -> SpatialHashMap
        return self._entity_hashmap

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
        elif isinstance(value, TileList):
            value._parent = self  # Make sure the parent is correct
            self.root["tiles"] = value
        else:
            raise TypeError("'tiles' must be a TileList, list, or None")

    # =========================================================================

    @property
    def tile_hashmap(self):
        # type: () -> SpatialHashMap
        return self._tile_hashmap

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
        # Create a copy ourself to modify
        copied_self = deepcopy(self)
        out_dict = copied_self.root

        # Generate a flat list of entities recursively, with any custom
        # modifications applied
        def flatten_entities(entities):
            out = []
            for entity in entities:
                result = entity.get()
                if isinstance(result, list):
                    out.extend(flatten_entities(result))
                else:
                    out.append(result)
            return out

        flattened_list = flatten_entities(copied_self.entities)

        # Preserve associations between copied schedules so that they point to
        # the correct entities
        out_dict["schedules"] = copied_self.schedules

        # Now convert all entities into their dict representation and place them
        # in their final location
        out_dict["entities"] = []
        i = 0
        for entity in flattened_list:
            result = entity.to_dict()
            if not isinstance(result, dict):
                raise DraftsmanError(
                    "{}.to_dict() must return a dict".format(type(entity).__name__)
                )
            out_dict["entities"].append(result)
            out_dict["entities"][i]["entity_number"] = i + 1
            i += 1

        # Convert all tiles into dicts
        # TODO: maybe handle TileLike?
        out_dict["tiles"] = []
        for tile in self.tiles:
            out_dict["tiles"].append(deepcopy(tile.to_dict()))

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
                                if isinstance(old, EntityLike):
                                    point["entity_id"] = flattened_list.index(old) + 1

                    elif side in {"Cu0", "Cu1"}:  # pragma: no branch
                        connection_points = connections[side]
                        for point in connection_points:
                            old = point["entity_id"]
                            if isinstance(old, EntityLike):
                                point["entity_id"] = flattened_list.index(old) + 1

            if "neighbours" in entity:  # Power pole connections
                neighbours = entity["neighbours"]
                for i, neighbour in enumerate(neighbours):
                    if isinstance(neighbour, EntityLike):
                        neighbours[i] = flattened_list.index(neighbour) + 1

        # Change all locomotive names to use entity_number
        for schedule in out_dict["schedules"]:
            for i, locomotive in enumerate(schedule["locomotives"]):
                if isinstance(locomotive, EntityLike):
                    schedule["locomotives"][i] = flattened_list.index(locomotive) + 1

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
