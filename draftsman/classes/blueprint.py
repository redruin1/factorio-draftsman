# blueprint.py
# -*- encoding: utf-8 -*-

# TODO: Add warnings for placement constraints on rails, rail signals and train stops


from __future__ import unicode_literals

from draftsman._factorio_version import __factorio_version_info__
from draftsman.classes.association import Association
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
    DataFormatError,
    InvalidConnectionError,
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
        Load the Blueprint with the contents of ``blueprint_string``. Raises
        ``draftsman.warning.DraftsmanWarning`` if there are any unrecognized
        keywords in the blueprint string.

        :param blueprint_string: Factorio-encoded blueprint string.

        :exception MalformedBlueprintStringError: If the input string is not
            decodable to a JSON object.
        :exception IncorrectBlueprintTypeError: If the input string is of a
            different type than the base class, such as a ``BlueprintBook``.
        """
        root = utils.string_to_JSON(blueprint_string)
        # Ensure that the blueprint string actually points to a blueprint
        if "blueprint" not in root:
            raise IncorrectBlueprintTypeError(
                "Root element of Blueprint string not 'blueprint'"
            )

        self.setup(**root["blueprint"])

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

    @utils.reissue_warnings
    def setup(self, **kwargs):
        """
        Setup the Blueprint's parameters with the input keywords as values.
        Raises ``draftsman.warning.DraftsmanWarning`` if any of the input
        keywords are unrecognized.

        :param kwargs: The dict of all keywords to set in the blueprint.

        :Example:

        .. code-block:: python

            blueprint = Blueprint()
            blueprint.setup(label="test", description="testing...")
            assert blueprint.label == "test"
            assert blueprint.description == "testing..."
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

        ### INTERNAL ###

        self._area = None
        self._tile_width = 0
        self._tile_height = 0

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
        The Blueprint's label (title).

        :getter: Gets the label, or ``None`` if not set.
        :setter: Sets the label of the ``Blueprint``.
        :type: ``str``

        :exception TypeError: When setting ``label`` to something other than
            ``str`` or ``None``.
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
        return self.root.get("label_color", None)

    @label_color.setter
    def label_color(self, value):
        # type: (dict) -> None
        if value is None:
            self.root.pop("label_color", None)
            return

        try:
            self.root["label_color"] = signatures.COLOR.validate(value)
        except SchemaError as e:
            six.raise_from(DataFormatError(e), None)

    # =========================================================================

    @property
    def icons(self):
        # type: () -> list
        """
        The icons of the Blueprint.

        Stored as a list of ``ICON`` objects, which are dicts that contain a
        ``SIGNAL_ID`` and an ``index`` key. Icons can be specified in this
        format, or they can be specified more succinctly with a simple list of
        signal names as strings.

        All signal entries must be a valid signal id. If the input format is a
        list of strings, the index of each item will be it's place in the list
        + 1. The number of entries cannot exceed 4, or else a
        ``DataFormatError`` is raised.

        :getter: Gets the list if icons, or ``None`` if not set.
        :setter: Sets the icons of the Blueprint. Removes the attribute if set
            to ``None``.
        :type: ``dict{"index": int, "signal": {"name": str, "type": str}}``

        :exception DataFormatError: If the set value does not match the
            specification above.
        """
        return self.root.get("icons", None)

    @icons.setter
    def icons(self, value):
        # type: (list[Union[dict, str]]) -> None
        if value is None:
            self.root.pop("icons", None)
            return
        try:
            self.root["icons"] = signatures.ICONS.validate(value)
        except SchemaError as e:
            six.raise_from(DataFormatError(e), None)

    # =========================================================================

    @property
    def description(self):
        # type: () -> str
        """
        The description of the Blueprint. Visible when hovering over it when
        inside someone's inventory.

        :getter: Gets the description, or ``None`` if not set.
        :setter: Sets the description of the Blueprint. Removes the attribute if
            set to ``None``.
        :type: ``str``

        :exception TypeError: If setting to anything other than a ``str`` or
            ``None``.
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
        The version of Factorio the Blueprint was created in/intended for.

        The Blueprint ``version`` is a 64-bit integer, which is a bitwise-OR
        of four 16-bit numbers. You can interpret this number more clearly by
        decoding it with :py:func:`draftsman.utils.decode_version`, or you can
        use the functions :py:func:`version_tuple` or :py:func:`version_string`
        which will give you a more readable output. This version number defaults
        to the version of Factorio that Draftsman is currently initialized with.

        The version can be set either as said 64-bit int, or a sequence of
        ints, usually a list or tuple, which is then encoded into the combined
        representation. The sequence is defined as:
        ``[major_version, minor_version, patch, development_release]``
        with ``patch`` and ``development_release`` defaulting to 0.

        .. seealso::

            `<https://wiki.factorio.com/Version_string_format>`_

        :getter: Gets the version, or ``None`` if not set.
        :setter: Sets the version of the Blueprint. Removes the attribute if set
            to ``None``.
        :type: ``int``

        :exception TypeError: If set to anything other than an ``int``, sequence
            of ``ints``, or ``None``.

        :example:

        .. code-block:: python

            blueprint.version = (1, 0) # version 1.0.0.0
            assert blueprint.version == 281474976710656
            assert blueprint.version_tuple() == (1, 0, 0, 0)
            assert blueprint.version_string() == "1.0.0.0"
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

        The value can be set either as a ``dict`` with ``"x"`` and ``"y"`` keys,
        or as a sequence of ints.

        :getter: Gets the size of the snapping grid, or ``None`` if not set.
        :setter: Sets the size of the snapping grid. Removes the attribute if
            set to ``None``
        :type: ``dict{"x": int, "y": int}``
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
        The absolute position of the snapping grid in the world. Only used if
        ``absolute_snapping`` is set to ``True`` or ``None``.

        :getter: Gets the absolute grid-position offset, or ``None`` if not set.
        :setter: Sets the a
        :type: ``dict{"x": int, "y": int}``
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
        The list of the Blueprint's entities. Internally the list is a custom
        class named :py:class:`draftsman.classes.EntityList`, which has all the
        normal properties of a regular list, as well as some extra features.
        For more information on ``EntityList``, check out this writeup
        :ref:`here <handbook.blueprints.blueprint_differences>`.
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
            value._parent = self  # Make sure the parent is correct
            self.root["entities"] = value
            # Add the new list entities to the hashmap
            self._entity_hashmap.clear()
            for entity in value:
                self._entity_hashmap.add(entity)
        else:
            raise TypeError("'entities' must be an EntityList, list, or None")

    def on_entity_insert(self, entitylike):
        # type: (EntityLike) -> None
        """
        Callback function for when an ``EntityLike`` is added to this
        Blueprint's ``entities`` list. Handles the addition of the entity into
        the  Blueprint's ``SpatialHashMap``, and recalculates it's dimensions.
        """
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
        """
        Callback function for when an entity is overwritten in a Blueprint's
        ``entities`` list. Handles the removal of the old ``EntityLike`` from
        the ``SpatialHashMap`` and adds the new one in it's stead.
        """
        # Remove the entity and its children
        self.entity_hashmap.recursively_remove(old_entitylike)
        # Add the new entity and its children
        self.entity_hashmap.recursively_add(new_entitylike)

    def on_entity_remove(self, entitylike):
        # type: (EntityLike) -> None
        """
        Callback function for when an entity is removed from a Blueprint's
        ``entities`` list. Handles the removal of the ``EntityLike`` from the
        ``SpatialHashMap``.
        """
        # Remove the entity and its children
        self.entity_hashmap.recursively_remove(entitylike)

    # =========================================================================

    @property
    def entity_hashmap(self):
        # type: () -> SpatialHashMap
        """
        The ``SpatialHashMap`` for ``entities``. Not exported; read only.
        """
        return self._entity_hashmap

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
        """
        The ``SpatialHashMap`` for ``entities``. Not exported; read only.
        """
        return self._tile_hashmap

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
        return self.root["schedules"]

    @schedules.setter
    def schedules(self, value):
        # type: (list) -> None
        if value is None:
            self.root["schedules"] = []
            return
        try:
            self.root["schedules"] = signatures.SCHEDULES.validate(value)
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

    def version_tuple(self):
        # type: () -> tuple(int, int, int, int)
        """
        Returns the version of the Blueprint as a 4-length tuple.

        :returns: a 4 length tuple in the format ``(major, minor, patch, dev_ver)``.
        """
        return utils.decode_version(self.root["version"])

    def version_string(self):
        # type: () -> str
        """
        Returns the version of the Blueprint in human-readable string.

        :returns: a ``str`` of 4 version numbers joined by a '.' character.
        """
        version_tuple = utils.decode_version(self.root["version"])
        return utils.version_tuple_to_string(version_tuple)

    def recalculate_area(self):
        # type: () -> None
        """
        Recalculates the ``area``, ``tile_width``, and ``tile_height``. Called
        automatically when an EntityLike or Tile object is altered or removed.
        Can be called by the end user, though it shouldn't be neccessary.
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

        :returns: The dict representation of the Blueprint.
        """
        # Create a new dict to return without modifying the original Blueprint
        # (We exclude "entities" and "tiles" because these objects are not
        # copyable for space and recursion depth reasons)
        out_dict = {
            x: self.root[x] for x in self.root if x not in {"entities", "tiles"}
        }

        # This associates each entity with a numeric index, which we use later
        flattened_list = utils.flatten_entities(self.root["entities"])

        # Convert all Entities into dicts
        out_dict["entities"] = []
        i = 0
        for entity in flattened_list:
            # Get a copy of the dict representation of the Entity
            # (At this point, Associations are not copied and still point to original)
            result = deepcopy(entity.to_dict())
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

        def throw_invalid_connection(entity):
            raise InvalidConnectionError(
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

    def to_string(self):  # pragma: no coverage
        # type: () -> str
        """
        Returns the Blueprint as an encoded Factorio blueprint string.

        :returns: The zlib-compressed, base-64 encoded string.
        """
        return utils.JSON_to_string(self.to_dict())

    def __setitem__(self, key, value):
        self.root[key] = value

    def __getitem__(self, key):
        return self.root[key]

    def __contains__(self, item):
        return item in self.root

    def __str__(self):  # pragma: no coverage
        return "<Blueprint>" + json.dumps(self.to_dict()["blueprint"], indent=2)
