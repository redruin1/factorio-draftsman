# blueprint.py
# -*- encoding: utf-8 -*-

# TODO: convert to Vectors

"""
.. code-block:: python

    {
        "blueprint": {
            "item": "blueprint", # The associated item with this structure
            "label": str, # A user given name for this blueprint
            "label_color": { # The overall color of the label
                "r": float[0.0, 1.0] or int[0, 255], # red
                "g": float[0.0, 1.0] or int[0, 255], # green
                "b": float[0.0, 1.0] or int[0, 255], # blue
                "a": float[0.0, 1.0] or int[0, 255]  # alpha (optional)
            },
            "icons": [ # A set of signals to act as visual identification
                {
                    "signal": {"name": str, "type": str}, # Name and type of signal
                    "index": int, # In range [1, 4], starting top-left and moving across
                },
                ... # Up to 4 icons total
            ],
            "description": str, # A user given description for this blueprint
            "version": int, # The encoded version of Factorio this planner was created 
                            # with/designed for (64 bits)
            "snap-to-grid": { # The size of the grid to snap this blueprint to
                "x": int, # X dimension in units
                "y": int, # Y dimension in units
            }
            "absolute-snapping": bool, # Whether or not to use absolute placement 
                                       # (defaults to True)
            "position-relative-to-grid": { # The offset of the grid if using absolute
                                           # placement
                "x": int, # X offset in units
                "y": int, # Y offset in units
            }
            "entities": [ # A list of entities in this blueprint
                {
                    "name": str, # Name of the entity,
                    "entity_number": int, # Unique number associated with this entity 
                    "position": {"x": float, "y": float}, # Position of the entity
                    ... # Any associated Entity key/value
                },
                ...
            ]
            "tiles": [ # A list of tiles in this blueprint
                {
                    "name": str, # Name of the tile
                    "position": {"x": int, "y": int}, # Position of the tile
                },
                ...
            ],
            "schedules": [ # A list of the train schedules in this blueprint
                {
                    "schedule": [ # A list of schedule records
                        {
                            "station": str, # Name of the stop associated with these
                                            # conditions
                            "wait_conditions": [
                                {
                                    "type": str, # Name of the type of condition
                                    "compare_type": "and" or "or",
                                    "ticks": int, # If using "time" or "inactivity"
                                    "condition": CONDITION, # If a circuit condition is 
                                                            # needed
                                }
                            ],
                        },
                        ...
                    ]
                    "locomotives": [int, ...] # A list of ints, corresponding to
                                              # "entity_number" in "entities"
                },
                ...
            ]
            
        }
    }
"""


from __future__ import unicode_literals

from draftsman._factorio_version import __factorio_version_info__
from draftsman.classes.association import Association
from draftsman.classes.blueprintable import Blueprintable
from draftsman.classes.entitylike import EntityLike
from draftsman.classes.entitylist import EntityList
from draftsman.classes.tilelist import TileList
from draftsman.classes.transformable import Transformable
from draftsman.classes.collection import EntityCollection, TileCollection
from draftsman.classes.spatial_data_structure import SpatialDataStructure
from draftsman.classes.spatial_hashmap import SpatialHashMap
from draftsman.error import (
    DraftsmanError,
    UnreasonablySizedBlueprintError,
    DataFormatError,
    InvalidAssociationError,
)
from draftsman import signatures
from draftsman.tile import Tile
from draftsman import utils
from draftsman.warning import DraftsmanWarning

from builtins import int
import copy
import math
from schema import SchemaError
import six
from typing import Sequence, Union
import warnings


class Blueprint(Transformable, TileCollection, EntityCollection, Blueprintable):
    """
    Factorio Blueprint class. Contains and maintains a list of ``EntityLikes``
    and ``Tiles`` and a selection of other metadata. Inherits all the functions
    and attributes you would expect, as well as some extra functionality.
    """

    # =========================================================================
    # Constructors
    # =========================================================================

    @utils.reissue_warnings
    def __init__(self, blueprint=None):
        # type: (Union[str, dict]) -> None
        """
        Creates a ``Blueprint`` class. Will load the data from ``blueprint`` if
        provided, and otherwise initializes itself with defaults. ``blueprint``
        can be either an encoded blueprint string or a dict object containing
        the desired key-value pairs.

        :param blueprint_string: Either a Factorio-format blueprint string or a
            ``dict`` object with the desired keys in the correct format.
        """
        super(Blueprint, self).__init__(
            root_item="blueprint", item="blueprint", init_data=blueprint
        )

    @utils.reissue_warnings
    def setup(self, **kwargs):
        self._root = {}

        # Item (type identifier)
        self._root["item"] = "blueprint"
        kwargs.pop("item", None)

        ### METADATA ###
        self.label = kwargs.pop("label", None)
        self.label_color = kwargs.pop("label_color", None)
        self.description = kwargs.pop("description", None)
        self.icons = kwargs.pop("icons", None)

        if "version" in kwargs:
            self.version = kwargs.pop("version")
        else:
            self.version = utils.encode_version(*__factorio_version_info__)

        # Snapping grid parameters
        # Handle their true keys, as well as the Pythonic attribute label
        if "snap-to-grid" in kwargs:
            self.snapping_grid_size = kwargs.pop("snap-to-grid")
        elif "snapping_grid_size" in kwargs:
            self.snapping_grid_size = kwargs.pop("snapping_grid_size")

        if "snapping_grid_position" in kwargs:
            self.snapping_grid_position = kwargs.pop("snapping_grid_position")
        else:
            self.snapping_grid_position = None

        if "absolute-snapping" in kwargs:
            self.absolute_snapping = kwargs.pop("absolute-snapping")
        elif "absolute_snapping" in kwargs:
            self.absolute_snapping = kwargs.pop("absolute_snapping")

        if "position-relative-to-grid" in kwargs:
            self.position_relative_to_grid = kwargs.pop("position-relative-to-grid")
        elif "position_relative_to_grid" in kwargs:
            self.position_relative_to_grid = kwargs.pop("position_relative_to_grid")

        ### INTERNAL ###
        self._area = None
        self._tile_width = 0
        self._tile_height = 0

        ### DATA ###
        # Create spatial hashing objects to make spatial queries much quicker
        self._tile_map = SpatialHashMap()
        self._entity_map = SpatialHashMap()

        # Data lists
        if "entities" in kwargs:
            self._root["entities"] = EntityList(self, kwargs.pop("entities"))
        else:
            self._root["entities"] = EntityList(self)

        if "tiles" in kwargs:
            self._root["tiles"] = TileList(self, kwargs.pop("tiles"))
        else:
            self._root["tiles"] = TileList(self)

        if "schedules" in kwargs:
            self._root["schedules"] = kwargs.pop("schedules")
        else:
            self._root["schedules"] = []

        # Issue warnings for any keyword not recognized by Blueprint
        for unused_arg in kwargs:
            warnings.warn(
                "{} has no attribute '{}'".format(type(self), unused_arg),
                DraftsmanWarning,
                stacklevel=2,
            )

        # Convert circuit and power connections to Associations
        for entity in self.entities:
            if hasattr(entity, "connections"):  # Wire connections
                connections = entity.connections
                for side in connections:
                    if side in {"1", "2"}:
                        for color in connections[side]:
                            connection_points = connections[side][color]
                            for point in connection_points:
                                old = point["entity_id"] - 1
                                point["entity_id"] = Association(self.entities[old])

                    elif side in {"Cu0", "Cu1"}:  # pragma: no branch
                        connection_points = connections[side]
                        for point in connection_points:
                            old = point["entity_id"] - 1
                            point["entity_id"] = Association(self.entities[old])

            if hasattr(entity, "neighbours"):  # Power pole connections
                neighbours = entity.neighbours
                for i, neighbour in enumerate(neighbours):
                    neighbours[i] = Association(self.entities[neighbour - 1])

        # Change all locomotive numbers to use Associations
        for schedule in self.schedules:
            for i, locomotive in enumerate(schedule["locomotives"]):
                schedule["locomotives"][i] = Association(self.entities[locomotive - 1])

    # =========================================================================
    # Blueprint properties
    # =========================================================================

    @property
    def label_color(self):
        # type: () -> dict
        """
        The color of the Blueprint's label.

        The ``label_color`` parameter exists in a dict format with the "r", "g",
        "b", and an optional "a" keys. The color can be specified like that, or
        it can be specified more succinctly as a sequence of 3-4 numbers,
        representing the colors in that order.

        The value of each of the numbers (according to Factorio spec) can be
        either in the range of [0.0, 1.0] or [0, 255]; if all the numbers are
        <= 1.0, the former range is used, and the latter otherwise. If "a" is
        omitted, it defaults to 1.0 or 255 when imported, depending on the
        range of the other numbers.

        :getter: Gets the color of the label, or ``None`` if not set.
        :setter: Sets the label color of the ``Blueprint``.
        :type: ``dict{"r": number, "g": number, "b": number, Optional("a"): number}``

        :exception DataFormatError: If the input ``label_color`` does not match
            the above specification.

        :example:

        .. code-block:: python

            blueprint.label_color = (127, 127, 127)
            print(blueprint.label_color)
            # {'r': 127.0, 'g': 127.0, 'b': 127.0}
        """
        return self._root.get("label_color", None)

    @label_color.setter
    def label_color(self, value):
        # type: (dict) -> None
        if value is None:
            self._root.pop("label_color", None)
            return

        try:
            self._root["label_color"] = signatures.COLOR.validate(value)
        except SchemaError as e:
            six.raise_from(DataFormatError(e), None)

    # =========================================================================

    @property
    def snapping_grid_size(self):
        # type: () -> dict
        """
        Sets the size of the snapping grid to use. The presence of this entry
        determines whether or not the Blueprint will have a snapping grid or
        not.

        The value can be set either as a ``dict`` with ``"x"`` and ``"y"`` keys,
        or as a sequence of ints.

        :getter: Gets the size of the snapping grid, or ``None`` if not set.
        :setter: Sets the size of the snapping grid. Removes the attribute if
            set to ``None``
        :type: ``dict{"x": int, "y": int}``
        """
        return self._root.get("snap-to-grid", None)

    @snapping_grid_size.setter
    def snapping_grid_size(self, value):
        # type: (Union[dict, Sequence]) -> None
        if value is None:
            self._root.pop("snap-to-grid", None)
            return

        try:
            self._root["snap-to-grid"] = {
                "x": math.floor(value["x"]),
                "y": math.floor(value["y"]),
            }
        except TypeError:
            self._root["snap-to-grid"] = {
                "x": math.floor(value[0]),
                "y": math.floor(value[1]),
            }

    # =========================================================================

    @property
    def snapping_grid_position(self):
        # type: () -> list
        """
        Sets the position of the snapping grid. Offsets all of the
        positions of the entities by this amount, effectively acting as a
        translation in relation to the snapping grid.

        .. NOTE::

            This function does not offset each entities position until export!

        :getter: Gets the offset amount of the snapping grid, or ``None`` if not
            set.
        :setter: Sets the offset amount of the snapping grid. Removes the
            attribute if set to ``None``.
        :type: ``dict{"x": int, "y": int}``
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
        Whether or not the blueprint uses absolute positioning or relative
        positioning for the snapping grid. On import, a value of ``None`` is
        interpreted as a default ``True``.

        :getter: Gets whether or not this blueprint uses absolute positioning,
            or ``None`` if not set.
        :setter: Sets whether or not to use absolute-snapping. Removes the
            attribute if set to ``None``.
        :type: ``bool``

        :exception TypeError: If set to anything other than a ``bool`` or
            ``None``.
        """
        return self._root.get("absolute-snapping", None)

    @absolute_snapping.setter
    def absolute_snapping(self, value):
        # type: (bool) -> None
        if value is None:
            self._root.pop("absolute-snapping", None)
        elif isinstance(value, bool):
            self._root["absolute-snapping"] = value
        else:
            raise TypeError("'absolute_snapping' must be a bool or None")

    # =========================================================================

    @property
    def position_relative_to_grid(self):
        # type: () -> dict
        """
        The absolute position of the snapping grid in the world. Only used if
        ``absolute_snapping`` is set to ``True`` or ``None``.

        :getter: Gets the absolute grid-position offset, or ``None`` if not set.
        :setter: Sets the a
        :type: ``dict{"x": int, "y": int}``
        """
        return self._root.get("position-relative-to-grid", None)

    @position_relative_to_grid.setter
    def position_relative_to_grid(self, value):
        # type: (Union[dict, Sequence]) -> None
        if value is None:
            self._root.pop("position-relative-to-grid", None)
            return

        try:
            self._root["position-relative-to-grid"] = {
                "x": math.floor(value["x"]),
                "y": math.floor(value["y"]),
            }
        except TypeError:
            self._root["position-relative-to-grid"] = {
                "x": math.floor(value[0]),
                "y": math.floor(value[1]),
            }

    # =========================================================================

    @property
    def entities(self):
        # type: () -> EntityList
        """
        The list of the Blueprint's entities. Internally the list is a custom
        class named :py:class:`.EntityList`, which has all the normal properties
        of a regular list, as well as some extra features. For more information
        on ``EntityList``, check out this writeup
        :ref:`here <handbook.blueprints.blueprint_differences>`.
        Note - assigning to this triggers a deep copy, so use .append()
        or .extend() if you're building incrementally.
        """
        return self._root["entities"]

    @entities.setter
    def entities(self, value):
        # type: (list[EntityLike]) -> None
        self._entity_map.clear()

        if value is None:
            self._root["entities"].clear()
        elif isinstance(value, list):
            self._root["entities"] = EntityList(self, value)
        elif isinstance(value, EntityList):
            # Just don't ask
            self._root["entities"] = copy.deepcopy(value, memo={"new_parent": self})
        else:
            raise TypeError("'entities' must be an EntityList, list, or None")

        self.recalculate_area()

    def on_entity_insert(self, entitylike, merge):
        # type: (EntityLike, bool) -> EntityLike
        """
        Callback function for when an :py:class:`.EntityLike` is added to this
        Blueprint's :py:attr:`entities` list. Handles the addition of the entity
        into :py:attr:`entity_map`, and recalculates it's dimensions.

        :raises UnreasonablySizedBlueprintError: If inserting the new entity
            causes the blueprint to exceed 10,000 x 10,000 tiles in dimension.
        """
        # Here we issue warnings for overlapping entities, modify existing
        # entities if merging is enabled and delete excess entities in entitylike
        entitylike = self.entity_map.handle_overlapping(entitylike, merge)

        if entitylike is None:  # the entity has been entirely merged
            return entitylike  # early exit

        # Issue entity-specific warnings/errors if any exist for this entitylike
        entitylike.on_insert(self)

        # If no errors, add this to hashmap (as well as any of it's children)
        self.entity_map.recursive_add(entitylike)

        # Update dimensions of Blueprint
        self._area = utils.extend_aabb(self._area, entitylike.get_world_bounding_box())
        (
            self._tile_width,
            self._tile_height,
        ) = utils.aabb_to_dimensions(self._area)
        # Check the blueprint for unreasonable size
        if self._tile_width > 10000 or self._tile_height > 10000:
            raise UnreasonablySizedBlueprintError(
                "Current blueprint dimensions ({}, {}) exceeds the maximum size"
                " (10,000 x 10,000)".format(self._tile_width, self._tile_height)
            )

        return entitylike

    def on_entity_set(self, old_entitylike, new_entitylike):
        # type: (EntityLike, EntityLike) -> None
        """
        Callback function for when an :py:class:`.EntityLike` is overwritten in
        a Blueprint's :py:attr:`entities` list. Handles the removal of the old
        ``EntityLike`` from :py:attr:`entity_map` and adds the new one in it's
        stead.
        """
        # Remove the entity and its children
        self.entity_map.recursive_remove(old_entitylike)

        # Perform any remove checks on per entity basis
        old_entitylike.on_remove(self)

        # Check for overlapping entities
        self.entity_map.handle_overlapping(new_entitylike, False)

        # Issue entity-specific warnings/errors if any exist for this entitylike
        new_entitylike.on_insert(self)

        # Add the new entity and its children
        self.entity_map.recursive_add(new_entitylike)

        # Disdain
        # self.recalculate_area()

    def on_entity_remove(self, entitylike):
        # type: (EntityLike) -> None
        """
        Callback function for when an :py:class:`.EntityLike` is removed from a
        Blueprint's :py:attr:`entities` list. Handles the removal of the
        ``EntityLike`` from :py:attr:`entity_map`.
        """
        # Handle entity specific
        entitylike.on_remove(self)

        # Remove the entity and its children
        self.entity_map.recursive_remove(entitylike)

        # Perform any remove checks on per entity basis
        entitylike.on_remove(self)

        # This sucks lmao
        # self.recalculate_area()

    # =========================================================================

    @property
    def entity_map(self):
        # type: () -> SpatialDataStructure
        """
        An implementation of :py:class:`.SpatialDataStructure` for ``entities``.
        Not exported; read only.
        """
        return self._entity_map

    # =========================================================================

    @property
    def tiles(self):
        # type: () -> TileList
        """
        The list of the Blueprint's tiles. Internally the list is a custom
        class named :py:class:`~.TileList`, which has all the normal properties
        of a regular list, as well as some extra features.

        :example:

        .. code-block:: python

            blueprint.tiles.append("landfill")
            assert isinstance(blueprint.tiles[-1], Tile)
            assert blueprint.tiles[-1].name == "landfill"

            blueprint.tiles.insert(0, "refined-hazard-concrete", position=(1, 0))
            assert blueprint.tiles[0].position == {"x": 1.5, "y": 1.5}

            blueprint.tiles = None
            assert len(blueprint.tiles) == 0
        """
        return self._root["tiles"]

    @tiles.setter
    def tiles(self, value):
        # type: (list[Tile]) -> None
        self.tile_map.clear()

        if value is None:
            self._root["tiles"] = TileList(self)
        elif isinstance(value, list):
            self._root["tiles"] = TileList(self, value)
        elif isinstance(value, TileList):
            self._root["tiles"] = copy.deepcopy(value)
        else:
            raise TypeError("'tiles' must be a TileList, list, or None")

        self.recalculate_area()

    def on_tile_insert(self, tile, merge):
        # type: (Tile, bool) -> None
        """
        Callback function for when a :py:class:`.Tile` is added to this
        Blueprint's :py:attr:`tiles` list. Handles the addition of the tile
        into :py:attr:`tile_map`, and recalculates it's dimensions.

        :raises UnreasonablySizedBlueprintError: If inserting the new tile
            causes the blueprint to exceed 10,000 x 10,000 tiles in dimension.
        """
        # Handle overlapping and merging
        tile = self.tile_map.handle_overlapping(tile, merge)

        if tile is None:  # Tile was merged
            return tile  # early exit

        # Add to tile map
        self.tile_map.add(tile)

        # Update dimensions
        self._area = utils.extend_aabb(self._area, tile.get_world_bounding_box())
        (
            self._tile_width,
            self._tile_height,
        ) = utils.aabb_to_dimensions(self.area)

        # Check the blueprint for unreasonable size
        if self._tile_width > 10000 or self._tile_height > 10000:
            raise UnreasonablySizedBlueprintError(
                "Current blueprint dimensions ({}, {}) exceeds the maximum size"
                " (10,000 x 10,000)".format(self._tile_width, self._tile_height)
            )

        return tile

    def on_tile_set(self, old_tile, new_tile):
        # type: (Tile, Tile) -> None
        """
        Callback function for when a :py:class:`.Tile` is overwritten in a
        Blueprint's :py:attr:`tiles` list. Handles the removal of the old ``Tile``
        from :py:attr:`tile_map` and adds the new one in it's stead.
        """
        self.tile_map.remove(old_tile)
        self.tile_map.handle_overlapping(new_tile, False)
        self.tile_map.add(new_tile)

        # Unfortunately, this can't be here because we need to recalculate after
        # modifying the base list, which happens *after* this function finishes
        # self.recalculate_area() # TODO

    def on_tile_remove(self, tile):
        # type: (Tile) -> None
        """
        Callback function for when a :py:class:`.Tile` is removed from a
        Blueprint's :py:attr:`tiles` list. Handles the removal of the ``Tile``
        from the :py:attr:`tile_map`.
        """
        self.tile_map.remove(tile)

        # Disdain...
        # self.recalculate_area() # TODO

    # =========================================================================

    @property
    def tile_map(self):
        # type: () -> SpatialDataStructure
        """
        An implementation of :py:class:`.SpatialDataStructure` for ``tiles``.
        Not exported; read only.
        """
        return self._tile_map

    # =========================================================================

    @property
    def schedules(self):
        # type: () -> list
        """
        A list of the Blueprint's train schedules.

        .. NOTE::

            Currently there is no framework around creating schedules by script;
            It can still be done by manipulating the contents of this list, but
            an easier way to manipulate trains and their schedules is still
            under development.

        .. seealso::

            `<https://wiki.factorio.com/Blueprint_string_format#Schedule_object>`_

        :getter: Gets the schedules of the Blueprint.
        :setter: Sets the schedules of the Blueprint. Defaults to ``[]`` if set
            to ``None``.
        :type: ``list[SCHEDULE]``

        :exception DataFormatError: If set to anything other than a ``list`` of
            :py:data:`.SCHEDULE`.
        """
        return self._root["schedules"]

    @schedules.setter
    def schedules(self, value):
        # type: (list) -> None
        if value is None:
            self._root["schedules"] = []
            return
        try:
            self._root["schedules"] = signatures.SCHEDULES.validate(value)
        except SchemaError as e:
            six.raise_from(DataFormatError(e), None)

    # =========================================================================

    @property
    def area(self):
        # type: () -> list[list[float]]
        """
        The Axis-aligned Bounding Box of the Blueprint's dimensions. Not
        exported; for user aid. Read only.

        Stored internally as a list of two lists, where the first one represents
        the top-left corner (minimum) and the second the bottom-right corner
        (maximum). This attribute is updated every time an Entity or Tile is
        changed inside the Blueprint.

        :type: ``list[list[float, float], list[float, float]]``
        """
        return self._area

    # =========================================================================

    @property
    def tile_width(self):
        # type: () -> int
        """
        The width of the Blueprint's ``area``, rounded up to the nearest tile.
        Read only.

        :type: ``int``
        """
        return self._tile_width

    # =========================================================================

    @property
    def tile_height(self):
        # type: () -> int
        """
        The width of the Blueprint's ``area``, rounded up to the nearest tile.
        Read only.

        :type: ``int``
        """
        return self._tile_height

    # =========================================================================

    @property
    def double_grid_aligned(self):
        # type: () -> bool
        """
        Whether or not the blueprint is aligned with the double grid, which is
        the grid that rail entities use, like rails and train-stops. If the
        blueprint has any entities that are double-grid-aligned, the Blueprint
        is considered double-grid-aligned. Read only.

        :type: ``bool``
        """
        for entity in self.entities:
            if entity.double_grid_aligned:
                return True

        return False

    # =========================================================================
    # Utility functions
    # =========================================================================

    def recalculate_area(self):
        # type: () -> None
        """
        Recalculates the ``area``, ``tile_width``, and ``tile_height``. Called
        automatically when an EntityLike or Tile object is altered or removed.
        Can be called by the end user, though it shouldn't be neccessary.
        """
        self._area = None
        for entity in self.entities:
            self._area = utils.extend_aabb(self._area, entity.get_world_bounding_box())

        for tile in self.tiles:
            self._area = utils.extend_aabb(self._area, tile.get_world_bounding_box())

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

        :returns: The ``dict`` representation of the Blueprint.
        """
        # Create a new dict to return without modifying the original Blueprint
        # (We exclude "entities" and "tiles" because these objects are not
        # copyable for space and recursion depth reasons)
        out_dict = {
            x: self._root[x] for x in self._root if x not in {"entities", "tiles"}
        }

        # This associates each entity with a numeric index, which we use later
        flattened_list = utils.flatten_entities(self._root["entities"])

        # Convert all Entities into dicts
        out_dict["entities"] = []
        i = 0
        for entity in flattened_list:
            # Get a copy of the dict representation of the Entity
            # (At this point, Associations are not copied and still point to original)
            result = copy.deepcopy(entity.to_dict())
            if not isinstance(result, dict):
                raise DraftsmanError(
                    "{}.to_dict() must return a dict".format(type(entity).__name__)
                )
            # Add this to the output's entities and set it's entity_number
            out_dict["entities"].append(result)
            out_dict["entities"][i]["entity_number"] = i + 1
            i += 1

        # Convert all tiles into dicts
        # Maybe handle TileLike?
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

        def throw_invalid_connection(entity):
            raise InvalidAssociationError(
                "'{}' at {} is connected to an entity that no longer exists".format(
                    entity["name"], entity["position"]
                )
            )

        # Convert all associations to use their integer indices
        # (This could be nicer)
        for entity in out_dict["entities"]:
            if "connections" in entity:  # Wire connections
                connections = entity["connections"]
                for side in connections:
                    if side in {"1", "2"}:
                        for color in connections[side]:
                            connection_points = connections[side][color]
                            for point in connection_points:
                                old = point["entity_id"]
                                if old() is None:  # pragma: no coverage
                                    throw_invalid_connection(entity)
                                else:  # Association
                                    point["entity_id"] = flattened_list.index(old()) + 1

                    elif side in {"Cu0", "Cu1"}:  # pragma: no branch
                        connection_points = connections[side]
                        for point in connection_points:
                            old = point["entity_id"]
                            if old() is None:  # pragma: no coverage
                                throw_invalid_connection(entity)
                            else:  # Association
                                point["entity_id"] = flattened_list.index(old()) + 1

            if "neighbours" in entity:  # Power pole connections
                neighbours = entity["neighbours"]
                for i, neighbour in enumerate(neighbours):
                    if neighbour() is None:  # pragma: no coverage
                        throw_invalid_connection(entity)
                    else:  # Association
                        neighbours[i] = flattened_list.index(neighbour()) + 1

        # Change all locomotive names to use entity_number
        for schedule in out_dict["schedules"]:
            for i, locomotive in enumerate(schedule["locomotives"]):
                if locomotive() is None:  # pragma: no coverage
                    throw_invalid_connection(entity)
                else:  # Association
                    schedule["locomotives"][i] = flattened_list.index(locomotive()) + 1

        # Delete empty entries to compress as much as possible
        if len(out_dict["entities"]) == 0:
            del out_dict["entities"]
        if len(out_dict["tiles"]) == 0:
            del out_dict["tiles"]
        if len(out_dict["schedules"]) == 0:
            del out_dict["schedules"]

        return {"blueprint": out_dict}

    def __deepcopy__(self, memo):
        # type: (dict) -> Blueprint
        """
        TODO
        """
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result

        # Make sure we copy "_entity_hashmap" first so we don't get
        # OverlappingEntitiesWarnings
        v = getattr(self, "_entity_map")
        setattr(result, "_entity_map", copy.deepcopy(v, memo))
        result.entity_map.clear()

        # We copy everything else, save for the 'root' dictionary, because
        # deepcopying those depend on some of the other attributes, so we load
        # those first
        for k, v in self.__dict__.items():
            if k == "_entity_map" or k == "_root":
                continue
            else:
                setattr(result, k, copy.deepcopy(v, memo))

        # Finally we can copy the root (most notably EntityList)
        v = getattr(self, "_root")
        copied_dict = {}
        for rk, rv in v.items():
            if rk == "entities":
                # Create a copy of EntityList with copied self as new
                # parent so that `result.entities[0].parent` will be
                # `result`
                memo["new_parent"] = result  # This is hacky, but fugg it
                copied_dict[rk] = copy.deepcopy(rv, memo)
            else:
                copied_dict[rk] = copy.deepcopy(rv, memo)
        setattr(result, "_root", copied_dict)

        return result
