# blueprint.py

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

import draftsman
from draftsman._factorio_version import __factorio_version_info__
from draftsman.classes.association import Association
from draftsman.classes.blueprintable import Blueprintable
from draftsman.classes.exportable import ValidationResult
from draftsman.classes.transformable import Transformable
from draftsman.classes.collection import EntityCollection, TileCollection
from draftsman.classes.schedule_list import ScheduleList
from draftsman.classes.vector import Vector
from draftsman.constants import LegacyDirection, ValidationMode
from draftsman.error import (
    DraftsmanError,
    UnreasonablySizedBlueprintError,
    InvalidAssociationError,
)
from draftsman.serialization import draftsman_converters
from draftsman.signatures import StockConnection
from draftsman.entity import Entity
from draftsman.classes.schedule import Schedule
from draftsman.utils import (
    AABB,
    aabb_to_dimensions,
    extend_aabb,
    flatten_entities,
)
from draftsman.validators import classvalidator, conditional, instance_of, try_convert

import attrs
from builtins import int
import copy
from typing import Any, Literal, Optional, Sequence, Union
from pydantic import (
    ConfigDict,
    Field,
    PrivateAttr,
    ValidationError,
    ValidationInfo,
    field_validator,
    field_serializer,
    model_validator,
)


def _convert_wires_to_associations(wires: list[list[int]], entities):
    for wire in wires:
        entity1 = entities[wire[0] - 1]
        wire[0] = Association(entity1)
        entity2 = entities[wire[2] - 1]
        wire[2] = Association(entity2)


def _convert_schedules_to_associations(schedules: ScheduleList, entities):
    for schedule in schedules:
        for i, locomotive in enumerate(schedule.locomotives):
            entity: Entity = entities[locomotive - 1]
            schedule.locomotives[i] = Association(entity)


def _convert_stock_connections_to_associations(
    stock_connections: list[StockConnection], entities
):
    for connection in stock_connections:
        connection.stock = Association(entities[connection.stock - 1])
        if isinstance(connection.front, int):
            connection.front = Association(entities[connection.front - 1])
        if isinstance(connection.back, int):
            connection.back = Association(entities[connection.back - 1])


def _normalize_internal_structure(
    input_root,
    entities_in,
    tiles_in,
    schedules_in,
    wires_in,
    stock_connections_in,
    *,
    version,
    exclude_defaults,
    exclude_none,
):
    # TODO make this a member of blueprint?
    def _throw_invalid_association(entity):
        raise InvalidAssociationError(  # pragma: no coverage
            "'{}' at {} is connected to an entity that no longer exists".format(
                entity["name"], entity["position"]
            )
        )

    # Entities
    flattened_entities = flatten_entities(entities_in)
    entities_out = []
    for i, entity in enumerate(flattened_entities):
        # Get a copy of the dict representation of the Entity
        # (At this point, Associations are not copied and still point to original)
        result = entity.to_dict(
            version=version,
            exclude_none=exclude_none,
            exclude_defaults=exclude_defaults,
            entity_number=i + 1,
        )
        if not isinstance(result, dict):
            raise DraftsmanError(
                "{}.to_dict() must return a dict".format(type(entity).__name__)
            )
        # Add this to the output's entities and set it's entity_number
        entities_out.append(result)
        # entities_out[i]["entity_number"] = i + 1

    # for entity in entities_out:
    #     if "connections" in entity:  # Wire connections
    #         connections = entity["connections"]
    #         for side in connections:
    #             if side in {"1", "2"}:
    #                 for color in connections[side]:
    #                     connection_points = connections[side][color]
    #                     for point in connection_points:
    #                         old = point["entity_id"]
    #                         # if isinstance(old, int):
    #                         #     continue
    #                         if old() is None:  # pragma: no coverage
    #                             _throw_invalid_association(entity)
    #                         else:  # Association
    #                             point["entity_id"] = flattened_entities.index(old()) + 1

    #             elif side in {"Cu0", "Cu1"}:  # pragma: no branch
    #                 connection_points = connections[side]
    #                 for point in connection_points:
    #                     old = point["entity_id"]
    #                     # if isinstance(old, int):
    #                     #     continue
    #                     if old() is None:  # pragma: no coverage
    #                         _throw_invalid_association(entity)
    #                     else:  # Association
    #                         point["entity_id"] = flattened_entities.index(old()) + 1

    #     if "neighbours" in entity:  # Power pole connections
    #         neighbours = entity["neighbours"]
    #         for i, neighbour in enumerate(neighbours):
    #             if neighbour() is None:  # pragma: no coverage
    #                 _throw_invalid_association(entity)
    #             else:  # Association
    #                 neighbours[i] = flattened_entities.index(neighbour()) + 1

    input_root["entities"] = entities_out

    # Tiles (TODO: should also be flattened)

    tiles_out = []
    for tile in tiles_in:
        tiles_out.append(tile.to_dict())

    input_root["tiles"] = tiles_out

    # Schedules (TODO: should also be flattened)

    # We also need to process any schedules that any subgroup might have, so
    # we recursively traverse the nested entitylike tree and append each
    # schedule to the output list
    # TODO: re-add the following
    # def recurse_schedules(entitylike_list):
    #     for entitylike in entitylike_list:
    #         if hasattr(entitylike, "schedules"):  # if a group
    #             # Add the schedules of this group
    #             out_dict["schedules"] += copy.deepcopy(entitylike.schedules)
    #             # Check through this groups entities to see if they have
    #             # schedules:
    #             recurse_schedules(entitylike.entities)

    schedules_out = []
    for schedule in schedules_in:
        schedules_out.append(schedule.to_dict())

    # Change all locomotive associations to use number
    for schedule in schedules_out:
        # Technically a schedule can have no locomotives:
        if "locomotives" in schedule:  # pragma: no branch
            for i, locomotive in enumerate(schedule["locomotives"]):
                if locomotive() is None:  # pragma: no coverage
                    _throw_invalid_association(locomotive)
                else:  # Association
                    schedule["locomotives"][i] = (
                        flattened_entities.index(locomotive()) + 1
                    )

    input_root["schedules"] = schedules_out

    # Wires
    def flatten_wires(entities_in):
        wires_out = []
        for entity in entities_in:
            if isinstance(entity, EntityCollection):
                wires_out.extend(entity.wires)
                wires_out.extend(flatten_wires(entity.entities))
            else:
                pass
        return wires_out

    flattened_wires = []
    flattened_wires.extend(wires_in)
    flattened_wires.extend(flatten_wires(entities_in))

    def get_index(assoc):
        if not isinstance(assoc, int):  # pragma: no branch
            # We would normally use index, but index uses `==` for comparisons,
            # wheras we want to use `is` for strict checking:
            try:
                return (
                    next(
                        i
                        for i, entity in enumerate(flattened_entities)
                        if entity is assoc()
                    )
                    + 1
                )
            except StopIteration:
                msg = "Association points to entity {} which does not exist in this blueprint".format(
                    assoc()
                )
                raise InvalidAssociationError(msg)
        return assoc  # pragma: no coverage

    wires_out = []
    for wire in flattened_wires:
        new_wire = [
            get_index(wire[0]),
            wire[1],
            get_index(wire[2]),
            wire[3],
        ]

        # Check to see if this wire already exists in the output, and neglect
        # adding it if so
        # TODO: this should happen earlier... somewhere...
        if new_wire not in wires_out:
            wires_out.append(new_wire)

    input_root["wires"] = wires_out

    # TODO: needs to be recursive, since theoretically groups could have stock
    # connections
    if "stock_connections" in input_root:  # pragma: no coverage
        for stock_connection in input_root["stock_connections"]:
            stock_connection["stock"] = get_index(stock_connection["stock"])
            if "front" in stock_connection:
                stock_connection["front"] = get_index(stock_connection["front"])
            if "back" in stock_connection:
                stock_connection["back"] = get_index(stock_connection["back"])


@draftsman.define
class Blueprint(Transformable, TileCollection, EntityCollection, Blueprintable):
    """
    Factorio Blueprint class. Contains and maintains a list of ``EntityLikes``
    and ``Tiles`` and a selection of other metadata. Inherits all the functions
    and attributes you would expect, as well as some extra functionality.
    """

    def __attrs_post_init__(self):
        # 1.0 code
        # Convert circuit and power connections to Associations
        # for entity in self.entities:
        #     if hasattr(entity, "connections"):  # Wire connections
        #         connections: Connections = entity.connections
        #         for side in connections.true_model_fields():
        #             if connections[side] is None:
        #                 continue

        #             if side in {"1", "2"}:
        #                 for color, _ in connections[side]:  # TODO fix
        #                     connection_points = connections[side][color]
        #                     if connection_points is None:
        #                         continue
        #                     for point in connection_points:
        #                         old = point["entity_id"] - 1
        #                         point["entity_id"] = Association(self.entities[old])

        #             elif side in {"Cu0", "Cu1"}:  # pragma: no branch
        #                 connection_points = connections[side]
        #                 if connection_points is None:
        #                     continue  # pragma: no coverage
        #                 for point in connection_points:
        #                     old = point["entity_id"] - 1
        #                     point["entity_id"] = Association(self.entities[old])

        #     if hasattr(entity, "neighbours"):  # Power pole connections
        #         neighbours = entity.neighbours
        #         for i, neighbour in enumerate(neighbours):
        #             neighbours[i] = Association(self.entities[neighbour - 1])

        _convert_wires_to_associations(self.wires, self.entities)
        _convert_schedules_to_associations(self.schedules, self.entities)
        _convert_stock_connections_to_associations(
            self.stock_connections, self.entities
        )

        # if self.validation:
        #     self.validate(mode=self.validation).reissue_all()

    # =========================================================================

    @property
    def root_item(self) -> Literal["blueprint"]:
        return "blueprint"

    # =========================================================================

    # TODO: this should be an evolve
    item: str = attrs.field(
        default="blueprint",
        validator=instance_of(str),
        metadata={
            "omit": False,
        },
    )
    # TODO: description

    # =========================================================================

    children: list[EntityCollection]

    # =========================================================================

    snapping_grid_size: Optional[Vector] = attrs.field(
        default=None,
        converter=try_convert(Vector.from_other),
        validator=instance_of(Optional[Vector]),
        metadata={"never_null": True},
    )
    """
    Sets the size of the snapping grid to use. The presence of this entry
    determines whether or not the Blueprint will have a snapping grid or
    not.

    The value can be set either as a ``dict`` with ``"x"`` and ``"y"`` keys,
    or as a sequence of ints.

    :getter: Gets the size of the snapping grid, or ``None`` if not set.
    :setter: Sets the size of the snapping grid. Removes the attribute if
        set to ``None``
    """

    # =========================================================================

    snapping_grid_position: Vector = attrs.field(
        factory=lambda: Vector(0, 0),
        eq=False,
        repr=False,
        converter=try_convert(Vector.from_other),
        validator=instance_of(Vector),
        metadata={"omit": True},
    )
    """
    Sets the position of the snapping grid. Offsets all of the
    positions of the entities by this amount, effectively acting as a
    translation in relation to the snapping grid.

    .. NOTE::

        This attribute does not offset each entities position until export!

    :getter: Gets the offset amount of the snapping grid, or ``None`` if not
        set.
    :setter: Sets the offset amount of the snapping grid. Removes the
        attribute if set to ``None``.
    """

    # =========================================================================

    absolute_snapping: bool = attrs.field(
        default=True,
        validator=instance_of(bool),
    )
    """
    Whether or not the blueprint uses absolute positioning or relative
    positioning for the snapping grid. On import, a value of ``None`` is
    interpreted as a default ``True``.

    :exception TypeError: If set to anything other than a ``bool`` or
        ``None``.
    """

    # =========================================================================

    position_relative_to_grid: Vector = attrs.field(
        factory=lambda: Vector(0, 0),
        converter=try_convert(Vector.from_other),
        validator=instance_of(Vector),
    )
    """
    The absolute position of the snapping grid in the world. Only used if
    ``absolute_snapping`` is set to ``True``.

    :getter: Gets the absolute grid-position offset.
    :setter: Sets the absolute grid-position offset. Is given a value of
        ``(0, 0)`` if set to ``None``
    """

    # =========================================================================

    @property
    def double_grid_aligned(self) -> bool:
        """
        Whether or not the blueprint is aligned with the double grid, which is
        the grid that rail entities use, like rails and train-stops. If the
        blueprint has any entities that are double-grid-aligned, the Blueprint
        is considered double-grid-aligned. Read only.
        """
        for entity in self.entities:
            if entity.double_grid_aligned:
                return True

        return False

    # =========================================================================
    # Utility functions
    # =========================================================================

    def get_world_bounding_box(self) -> Optional[AABB]:
        """
        Calculates the minimum AABB which encompasses all entities and tiles
        within this blueprint. If the blueprint is empty of entities or tiles,
        or if all of the entities contained within it have no known dimension,
        then this function returns ``None``.

        :returns: The smallest :py:class:`.AABB` which encompasses all entities
            and tiles currently contained.
        """
        area = None
        for entity in self.entities:
            area = extend_aabb(area, entity.get_world_bounding_box())

        for tile in self.tiles:
            area = extend_aabb(area, tile.get_world_bounding_box())

        return area

    def get_dimensions(self) -> tuple[int, int]:
        """
        Calculates the maximum extents of the blueprint along the x and y axis
        in tiles. Returns ``(0, 0)`` if the blueprint's world bounding box is
        ``None``.

        :returns: A 2-length tuple with the maximum tile width as the first
            entry and the maximum tile height as the second entry.
        """
        return aabb_to_dimensions(self.get_world_bounding_box())

    def validate(
        self, mode: ValidationMode = ValidationMode.STRICT, force: bool = False
    ) -> ValidationResult:
        result = super().validate(mode=mode, force=force)

        for class_validator in type(self).__attrs_class_validators__:
            class_validator(self, mode=mode)

        return result

    def to_dict(
        self,
        version: tuple[int, ...] = __factorio_version_info__,
        exclude_none: bool = True,
        exclude_defaults: bool = True,
    ) -> dict:
        result = super().to_dict(
            version=version,
            exclude_none=exclude_none,
            exclude_defaults=exclude_defaults,
        )

        # We then convert all the entities, tiles, and schedules to
        # 1-dimensional lists, flattening any Groups that this blueprint
        # contains, and swapping their Associations into integer indexes
        _normalize_internal_structure(
            result[self.root_item],
            self.entities,
            self.tiles,
            self.schedules,
            self.wires,
            self.stock_connections,
            version=version,
            exclude_none=exclude_none,
            exclude_defaults=exclude_defaults,
        )

        # Make sure that snapping_grid_position is respected
        # if self.snapping_grid_position is not None:
        # Offset Entities
        for entity in result["blueprint"]["entities"]:
            entity["position"]["x"] -= self.snapping_grid_position.x
            entity["position"]["y"] -= self.snapping_grid_position.y

        # Offset Tiles
        for tile in result["blueprint"]["tiles"]:
            tile["position"]["x"] -= self.snapping_grid_position.x
            tile["position"]["y"] -= self.snapping_grid_position.y

        # if "snap-to-grid" in result["blueprint"] and result["blueprint"][
        #     "snap-to-grid"
        # ] == {"x": 0, "y": 0}:
        #     del result["blueprint"]["snap-to-grid"]
        # if "position-relative-to-grid" in result["blueprint"] and result["blueprint"][
        #     "position-relative-to-grid"
        # ] == {"x": 0, "y": 0}:
        #     del result["blueprint"]["position-relative-to-grid"]

        if len(result["blueprint"]["entities"]) == 0:
            del result["blueprint"]["entities"]
        if len(result["blueprint"]["tiles"]) == 0:
            del result["blueprint"]["tiles"]
        if len(result["blueprint"]["schedules"]) == 0:
            del result["blueprint"]["schedules"]
        if len(result["blueprint"]["wires"]) == 0:
            del result["blueprint"]["wires"]

        return result

    # =========================================================================
    # Class validators
    # =========================================================================

    @classvalidator
    @conditional(ValidationMode.MINIMUM)
    def ensure_reasonable_size(self):
        tile_width, tile_height = self.get_dimensions()
        if tile_width > 10000 or tile_height > 10000:
            msg = "Current blueprint dimensions ({}, {}) exceeds the maximum size permitted by Factorio (10000, 10000)".format(
                tile_width, tile_height
            )
            raise UnreasonablySizedBlueprintError(msg)

    # =========================================================================

    def __deepcopy__(self, memo: dict) -> "Blueprint":
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result

        def swap_association(original_association):
            """
            Take an association which points to some entity in `self` and return
            a new association which points to the equivalent entity in `result`.
            """
            original_entity = original_association()
            copied_entity = memo[id(original_entity)]
            return Association(copied_entity)

        memo[
            "new_parent"
        ] = result  # TODO: this should really be fixed, because then we can use "deepcopy_func"
        for attr in attrs.fields(cls):
            if attr.name == "wires":  # special
                new_wires = copy.deepcopy(getattr(self, attr.name), memo)
                for wire in new_wires:
                    wire[0] = swap_association(wire[0])
                    wire[2] = swap_association(wire[2])

                object.__setattr__(result, attr.name, new_wires)
            elif attr.name == "schedules":
                new_schedules = copy.deepcopy(getattr(self, attr.name), memo)
                for schedule in new_schedules:  # pragma: no coverage
                    schedule: Schedule
                    schedule.locomotives = [
                        swap_association(loco) for loco in schedule.locomotives
                    ]

                object.__setattr__(result, attr.name, new_schedules)
            elif attr.name == "stock_connections":  # special
                new_connections: list[StockConnection] = copy.deepcopy(
                    getattr(self, attr.name), memo
                )
                for connection in new_connections:  # pragma: no coverage
                    connection.stock = swap_association(connection.stock)
                    if connection.front is not None:
                        connection.front = swap_association(connection.front)
                    if connection.back is not None:
                        connection.back = swap_association(connection.back)

                object.__setattr__(result, attr.name, new_connections)
            else:
                object.__setattr__(
                    result, attr.name, copy.deepcopy(getattr(self, attr.name), memo)
                )

        return result


Blueprint.add_schema(
    {
        "$id": "urn:factorio:blueprint",
        "type": "object",
        "description": "Blueprint string format for Factorio 1.X.",
        "properties": {
            "blueprint": {
                "type": "object",
                "properties": {
                    "item": {"const": "blueprint"},
                    "label": {"type": "string"},
                    "label_color": {"$ref": "urn:factorio:color"},
                    "description": {"type": "string"},
                    "icons": {
                        "type": "array",
                        "items": {"$ref": "urn:factorio:icon"},
                        "maxItems": 4,
                    },
                    "version": {"$ref": "urn:uint64"},
                    "snap-to-grid": {"$ref": "urn:factorio:position"},
                    "absolute-snapping": {"type": "boolean", "default": "true"},
                    "position-relative-to-grid": {"$ref": "urn:factorio:position"},
                    "entities": {
                        "type": "array",
                        "items": {
                            "oneOf": [
                                {"$ref": "urn:factorio:entity"}
                                # TODO
                            ]
                        },
                    },
                    "tiles": {"type": "array", "items": {"$ref": "urn:factorio:tile"}},
                    "schedules": {
                        "type": "array",
                        "items": {"$ref": "urn:factorio:schedule"},
                    },
                },
            },
        },
    },
    version=(1, 0),
)

draftsman_converters.get_version((1, 0)).add_hook_fns(
    Blueprint,
    lambda fields: {
        ("blueprint", "item"): fields.item.name,
        ("blueprint", "label"): fields.label.name,
        ("blueprint", "label_color"): fields.label_color.name,
        ("blueprint", "description"): fields.description.name,
        ("blueprint", "icons"): fields.icons.name,
        ("blueprint", "version"): fields.version.name,
        ("blueprint", "snap-to-grid"): fields.snapping_grid_size.name,
        ("blueprint", "absolute-snapping"): fields.absolute_snapping.name,
        (
            "blueprint",
            "position-relative-to-grid",
        ): fields.position_relative_to_grid.name,
        ("blueprint", "entities"): fields.entities.name,
        ("blueprint", "tiles"): fields.tiles.name,
        None: fields.wires.name,
        ("blueprint", "schedules"): fields.schedules.name,
        None: fields.stock_connections.name,
    },
)


def structure_blueprint_1_0_factory(t: type):
    default_blueprint_hook = (
        draftsman_converters.get_version((1, 0)).get_converter().get_structure_hook(t)
    )

    def structure_blueprint_1_0(d: dict, _: type) -> Blueprint:
        """
        Converts a 1.0 Factorio blueprint string into Draftsman internal form,
        preferring modern format where possible.
        """
        # Swapping old entity names to new ones is not actually "conversion", this
        # would instead be "migration"
        # For example, these entities would exist just fine if we had an old version
        # of `factorio-data` loaded
        # In practice, we should just load these objects as generic `Entity`
        # instances with all of their data intact, and then the user would call a
        # separate function `migrate(version)` which would then swap/remove/update
        # entities
        legacy_entity_conversions = {
            "curved-rail": "legacy-curved-rail",
            "straight-rail": "legacy-straight-rail",
            "logistic-chest-requester": "requester-chest",
            "logistic-chest-buffer": "buffer-chest",
            "logistic-chest-storage": "storage-chest",
            "logistic-chest-active-provider": "active-provider-chest",
            "logistic-chest-passive-provider": "passive-provider-chest",
            "filter-inserter": "inserter",  # TODO: LegacyFilterInserter(?)
            "stack-inserter": "bulk-inserter",
            "stack-filter-inserter": "bulk-inserter",
        }
        # TODO: just use defines already...
        wire_types = {
            ("1", "red"): 1,
            ("1", "green"): 2,
            ("2", "red"): 3,
            ("2", "green"): 4,
            "Cu0": 5,
            "Cu1": 6,
        }
        # TODO: modifying in-place might be a bad idea; investigate
        blueprint_dict = d["blueprint"]
        # "Backport" the wires list to Factorio 1.0
        wires = blueprint_dict["wires"] = []
        # Iterate over every entity with connections
        if "entities" in blueprint_dict:
            for entity in blueprint_dict["entities"]:
                # Convert entities to their modern equivalents
                # if entity["name"] in legacy_entity_conversions:  # pragma: no coverage
                #     entity["name"] = legacy_entity_conversions[entity["name"]]

                # Swap from old 8-direction to modern 16-direction
                if "direction" in entity:  # pragma: no coverage
                    entity["direction"] = LegacyDirection(
                        entity["direction"]
                    ).to_modern()

                # Move connections
                if "connections" in entity:
                    connections = entity["connections"]
                    for side in {"1", "2"}:
                        if side not in connections:
                            continue

                        # print(connections)
                        # print(connections[side])
                        for color in connections[side]:
                            connection_points = connections[side][color]

                            for point in connection_points:
                                # print("point", point)
                                # print(wires)
                                entity_id = point["entity_id"]
                                circuit_id = str(point.get("circuit_id", 1))
                                # print(entity_id, circuit_id)
                                # Make sure we don't add the reverse as a duplicate
                                if [
                                    entity_id,
                                    wire_types[(circuit_id, color)],
                                    entity["entity_number"],
                                    wire_types[(side, color)],
                                ] not in wires:
                                    wires.append(
                                        [
                                            entity["entity_number"],
                                            wire_types[(side, color)],
                                            entity_id,
                                            wire_types[(circuit_id, color)],
                                        ]
                                    )

                    for side in {"Cu0", "Cu1"}:
                        if side not in connections:
                            continue
                        connection_points = connections[side]
                        for point in connection_points:
                            entity_id = point["entity_id"]
                            circuit_id = point.get("circuit_id", "Cu0")
                            # It's impossible to add a mirror power connection
                            # from the old format, so we don't have to check if
                            # it exists beforehand
                            wires.append(
                                [
                                    entity["entity_number"],
                                    wire_types[side],
                                    entity_id,
                                    wire_types[circuit_id],
                                ]
                            )

                    del entity["connections"]

                if "neighbours" in entity:
                    for neighbour in entity["neighbours"]:
                        # Make sure we don't add the reverse as a duplicate
                        if [
                            neighbour,
                            5,
                            entity["entity_number"],
                            5,
                        ] not in wires:
                            wires.append(
                                [
                                    entity["entity_number"],
                                    5,
                                    neighbour,
                                    5,
                                ]
                            )

                    del entity["neighbours"]

        # Schedules are split into "records" which holds stops and the new interrupts
        if "schedules" in blueprint_dict:
            for schedule in blueprint_dict["schedules"]:
                stop_data = schedule["schedule"]
                schedule["schedule"] = {"records": stop_data}

        # print("blueprint_dict", blueprint_dict)
        # import inspect
        # print(inspect.getsource(_default_blueprint_hook))
        return default_blueprint_hook(d, _)

    return structure_blueprint_1_0


draftsman_converters.get_version((1, 0)).register_structure_hook(
    Blueprint, structure_blueprint_1_0_factory(Blueprint)
)

Blueprint.add_schema(
    {
        "$id": "urn:factorio:blueprint",
        "type": "object",
        "description": "Blueprint string format for Factorio 2.X.",
        "properties": {
            "blueprint": {
                "type": "object",
                "properties": {
                    "item": {"const": "blueprint"},
                    "label": {"type": "string"},
                    "label_color": {"$ref": "urn:factorio:color"},
                    "description": {"type": "string"},
                    "icons": {
                        "type": "array",
                        "items": {"$ref": "urn:factorio:icon"},
                        "maxItems": 4,
                    },
                    "version": {"$ref": "urn:uint64"},
                    "snap-to-grid": {"$ref": "urn:factorio:position"},
                    "absolute-snapping": {"type": "boolean", "default": "true"},
                    "position-relative-to-grid": {"$ref": "urn:factorio:position"},
                    "entities": {
                        "type": "array",
                        "items": {
                            "oneOf": [
                                {"$ref": "urn:factorio:entity"}
                                # TODO
                            ]
                        },
                    },
                    "tiles": {"type": "array", "items": {"$ref": "urn:factorio:tile"}},
                    "wires": {
                        "type": "array",
                        "items": {
                            "type": "array",
                            "prefixItems": [
                                {
                                    "$ref": "urn:uint64",
                                    "description": "'entity_number' of the first entity being connected.",
                                },
                                {
                                    "enum": [1, 2, 3, 4, 5, 6],
                                    "description": "What kind of connection the wire has to entity1. See 'wire_connection_types' in Factorio defines.",
                                },
                                {
                                    "$ref": "urn:uint64",
                                    "description": "'entity_number' of the second entity being connected.",
                                },
                                {
                                    "enum": [1, 2, 3, 4, 5, 6],
                                    "description": "What kind of connection the wire has to entity1. See 'wire_connection_types' in Factorio defines.",
                                },
                            ],
                            "items": False,
                        },
                    },
                    "schedules": {
                        "type": "array",
                        "items": {"$ref": "urn:factorio:schedule"},
                    },
                    "stock_connections": {
                        "type": "array",
                        "items": {"$ref": "urn:factorio:stock-connection"},
                    },
                },
            },
        },
    },
    version=(2, 0),
)

draftsman_converters.get_version((2, 0)).add_hook_fns(
    Blueprint,
    lambda fields: {
        ("blueprint", "item"): fields.item.name,
        ("blueprint", "label"): fields.label.name,
        ("blueprint", "label_color"): fields.label_color.name,
        ("blueprint", "description"): fields.description.name,
        ("blueprint", "icons"): fields.icons.name,
        ("blueprint", "version"): fields.version.name,
        ("blueprint", "snap-to-grid"): fields.snapping_grid_size.name,
        ("blueprint", "absolute-snapping"): fields.absolute_snapping.name,
        (
            "blueprint",
            "position-relative-to-grid",
        ): fields.position_relative_to_grid.name,
        ("blueprint", "entities"): fields.entities.name,
        ("blueprint", "tiles"): fields.tiles.name,
        ("blueprint", "wires"): fields.wires.name,
        ("blueprint", "schedules"): fields.schedules.name,
        ("blueprint", "stock_connections"): fields.stock_connections.name,
    },
)
