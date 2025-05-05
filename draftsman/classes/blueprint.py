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
from draftsman.classes.entity_like import EntityLike
from draftsman.classes.entity_list import EntityList
from draftsman.classes.exportable import ValidationResult
from draftsman.classes.tile_list import TileList
from draftsman.classes.transformable import Transformable
from draftsman.classes.collection import EntityCollection, TileCollection
from draftsman.classes.schedule_list import ScheduleList
from draftsman.classes.spatial_data_structure import SpatialDataStructure
from draftsman.classes.spatial_hashmap import SpatialHashMap
from draftsman.classes.vector import Vector, PrimitiveVector
from draftsman.constants import Direction, LegacyDirection, ValidationMode
from draftsman.error import (
    DraftsmanError,
    UnreasonablySizedBlueprintError,
    DataFormatError,
    InvalidAssociationError,
)
from draftsman.serialization import draftsman_converters
from draftsman.signatures import (
    StockConnection
)
from draftsman.entity import Entity
from draftsman.tile import Tile
from draftsman.classes.schedule import Schedule
from draftsman.utils import (
    AABB,
    aabb_to_dimensions,
    encode_version,
    extend_aabb,
    flatten_entities,
    reissue_warnings,
)
from draftsman.validators import classvalidator, instance_of

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
    for i, wire in enumerate(wires):
        # print(wire)
        if isinstance(wire[0], int):
            entity1 = entities[wire[0] - 1]
            wire[0] = Association(entity1)
        if isinstance(wire[2], int):
            entity2 = entities[wire[2] - 1]
            wire[2] = Association(entity2)


def _convert_schedules_to_associations(schedules: ScheduleList, entities):
    for schedule in schedules:
        for i, locomotive in enumerate(schedule.locomotives):
            if isinstance(locomotive, int):
                entity: Entity = entities[locomotive - 1]
                schedule.locomotives[i] = Association(entity)


def _convert_stock_connections_to_associations(
    stock_connections: list[StockConnection], entities
):
    for connection in stock_connections:
        if isinstance(connection.stock, int):
            connection.stock = Association(entities[connection.stock - 1])
        if isinstance(connection.front, int):
            connection.front = Association(entities[connection.front - 1])
        if isinstance(connection.back, int):
            connection.back = Association(entities[connection.back - 1])


def _normalize_internal_structure(
    input_root, entities_in, tiles_in, schedules_in, wires_in, stock_connections_in
):
    # TODO make this a member of blueprint?
    def _throw_invalid_association(entity):
        raise InvalidAssociationError(
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
        result = entity.to_dict(entity_number=i + 1) # TODO: needs arguments from parent
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
        if "locomotives" in schedule:
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
        if not isinstance(assoc, int):
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
        return assoc

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
    if "stock_connections" in input_root:
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

    # =========================================================================
    # Format
    # =========================================================================

    # class Format(DraftsmanBaseModel):
    #     # Private Internals (Not exported)
    #     _entities: EntityList = PrivateAttr()
    #     _tiles: TileList = PrivateAttr()
    #     _schedules: ScheduleList = PrivateAttr()
    #     _wires: list[tuple[Association, int, Association, int]] = PrivateAttr()

    #     class BlueprintObject(DraftsmanBaseModel):
    #         # Private Internals (Not exported)
    #         _snap_to_grid: Vector = PrivateAttr(Vector(0, 0))
    #         _snapping_grid_position: Vector = PrivateAttr(Vector(0, 0))
    #         _position_relative_to_grid: Vector = PrivateAttr(Vector(0, 0))

    #         item: Literal["blueprint"] = Field(
    #             ...,
    #             description="""
    #             The item that this BlueprintItem object is associated with.
    #             Always equivalent to 'blueprint'.
    #             """,
    #         )
    #         label: Optional[str] = Field(
    #             None,
    #             description="""
    #             A string title for this Blueprint.
    #             """,
    #         )
    #         label_color: Optional[Color] = Field(
    #             None,
    #             description="""
    #             The color to draw the label of this blueprint with, if 'label'
    #             is present. Defaults to white if omitted.
    #             """,
    #         )
    #         description: Optional[str] = Field(
    #             None,
    #             description="""
    #             A string description given to this Blueprint.
    #             """,
    #         )
    #         icons: Optional[list[Icon]] = Field(
    #             None,
    #             description="""
    #             A set of signal pictures to associate with this Blueprint.
    #             """,
    #             max_length=4,
    #         )
    #         version: Optional[uint64] = Field(
    #             None,
    #             description="""
    #             What version of Factorio this UpgradePlanner was made
    #             in/intended for. Specified as 4 unsigned 16-bit numbers combined,
    #             representing the major version, the minor version, the patch
    #             number, and the internal development version respectively. The
    #             most significant digits correspond to the major version, and the
    #             least to the development number.
    #             """,
    #         )

    #         snap_to_grid: Optional[IntPosition] = Field(
    #             IntPosition(x=1, y=1),
    #             alias="snap-to-grid",
    #             description="""
    #             The dimension of a square grid to snap this blueprint to, if
    #             present.
    #             """,
    #         )
    #         absolute_snapping: Optional[bool] = Field(
    #             True,
    #             alias="absolute-snapping",
    #             description="""
    #             Whether or not 'snap-to-grid' is relative to the global map
    #             coordinates, or to the position of the first blueprint built.
    #             """,
    #         )
    #         position_relative_to_grid: Optional[IntPosition] = Field(
    #             IntPosition(x=0, y=0),
    #             alias="position-relative-to-grid",
    #             description="""
    #             Any positional offset that the snapping grid has if
    #             'absolute-snapping' is true.
    #             """,
    #         )

    #         entities: Optional[list[dict]] = Field(
    #             [],
    #             description="""
    #             The list of all entities contained in the blueprint.
    #             """,
    #         )
    #         tiles: Optional[list[dict]] = Field(
    #             [],
    #             description="""
    #             The list of all tiles contained in the blueprint.
    #             """,
    #         )
    #         schedules: Optional[list[dict]] = Field(
    #             [],
    #             description="""
    #             The list of all schedules contained in the blueprint.
    #             """,
    #         )
    #         wires: Optional[list[list[int]]] = Field(
    #             [],
    #             description="""
    #             (2.0) The definitions of all wires in the blueprint, including
    #             both power and circuit connections.
    #             """,
    #         )
    #         stock_connections: Optional[list[dict]] = []  # TODO

    #         @field_validator("icons", mode="before")
    #         @classmethod
    #         def init_icons_from_list(cls, value: Any):
    #             if isinstance(value, (tuple, list)):
    #                 result = []
    #                 for i, elem in enumerate(value):
    #                     if isinstance(elem, str):
    #                         result.append({"signal": elem, "index": i + 1})
    #                     else:
    #                         result.append(elem)
    #                 return result
    #             else:
    #                 return value

    #         @field_serializer("snap_to_grid", when_used="unless-none")
    #         def serialize_snapping_grid(self, _):
    #             return self._snap_to_grid.to_dict()

    #         @field_serializer("position_relative_to_grid", when_used="unless-none")
    #         def serialize_position_relative(self, _):
    #             return self._position_relative_to_grid.to_dict()

    #     blueprint: BlueprintObject
    #     index: Optional[uint16] = Field(
    #         None,
    #         description="""
    #         The index of the blueprint inside a parent BlueprintBook's blueprint
    #         list. Only meaningful when this object is inside a BlueprintBook.
    #         """,
    #     )

    #     @model_validator(mode="after")
    #     def check_if_unreasonable_size(self, info: ValidationInfo):
    #         if not info.context:  # pragma: no coverage
    #             return self
    #         if info.context["mode"] <= ValidationMode.MINIMUM:
    #             return self

    #         blueprint: Blueprint = info.context["object"]

    #         # Check the blueprint for unreasonable size
    #         tile_width, tile_height = blueprint.get_dimensions()
    #         if tile_width > 10000 or tile_height > 10000:
    #             raise UnreasonablySizedBlueprintError(
    #                 "Current blueprint dimensions ({}, {}) exceeds the maximum size permitted by Factorio (10000, 10000)".format(
    #                     tile_width, tile_height
    #                 )
    #             )

    #         return self

    #     model_config = ConfigDict(title="Blueprint")

    # =========================================================================
    # Constructors
    # =========================================================================

    # @reissue_warnings
    # def __init__(
    #     self,
    #     blueprint: Union[str, dict] = None,
    #     index: Optional[uint16] = None,
    #     validate: Union[
    #         ValidationMode, Literal["none", "minimum", "strict", "pedantic"]
    #     ] = ValidationMode.STRICT,
    #     validate_assignment: Union[
    #         ValidationMode, Literal["none", "minimum", "strict", "pedantic"]
    #     ] = ValidationMode.STRICT,
    # ):
    #     """
    #     Creates a ``Blueprint`` class. Will load the data from ``blueprint`` if
    #     provided, and otherwise initializes itself with defaults. ``blueprint``
    #     can be either an encoded blueprint string or a dict object containing
    #     the desired key-value pairs.

    #     :param blueprint_string: Either a Factorio-format blueprint string or a
    #         ``dict`` object with the desired keys in the correct format.
    #     """
    #     self._root: __class__.Format

    #     super().__init__(
    #         root_item="blueprint",
    #         root_format=Blueprint.Format.BlueprintObject,
    #         item="blueprint",
    #         init_data=blueprint,
    #         index=index,
    #         validate=validate,
    #         entities=[],
    #         tiles=[],
    #         schedules=[],
    #     )

    #     self.validate_assignment = validate_assignment

    # @reissue_warnings
    # def setup(
    #     self,
    #     label: Optional[str] = None,
    #     label_color: Optional[Color] = None,
    #     description: Optional[str] = None,
    #     icons: Optional[list[Icon]] = None,
    #     version: Optional[uint64] = __factorio_version_info__,
    #     snapping_grid_size: Union[Vector, PrimitiveVector, None] = None,
    #     snapping_grid_position: Union[Vector, PrimitiveVector, None] = None,
    #     absolute_snapping: Optional[bool] = True,
    #     position_relative_to_grid: Union[Vector, PrimitiveVector, None] = None,
    #     entities: Union[EntityList, list[EntityLike]] = [],
    #     tiles: Union[TileList, list[Tile]] = [],
    #     schedules: Union[ScheduleList, list[Schedule]] = [],
    #     wires: Optional[list[list[int]]] = None,
    #     stock_connections: Optional[list[dict]] = None,  # TODO
    #     index: Optional[uint16] = None,
    #     validate: Union[
    #         ValidationMode, Literal["none", "minimum", "strict", "pedantic"]
    #     ] = ValidationMode.STRICT,
    #     **kwargs,
    # ):
    #     # self._root.blueprint = Blueprint.Format.BlueprintObject(item="blueprint")

    #     # Item (type identifier)
    #     kwargs.pop("item", None)

    #     ### METADATA ###
    #     self.label = label
    #     self.label_color = label_color
    #     self.description = description
    #     self.icons = icons

    #     self.version = version

    #     # Snapping grid parameters
    #     # Handle their true keys, as well as the Draftsman attribute label
    #     # self._root[self._root_item]["snap-to-grid"] = Vector(0, 0) # TODO: move
    #     if "snap-to-grid" in kwargs:
    #         self.snapping_grid_size = kwargs.pop("snap-to-grid")
    #     else:
    #         self.snapping_grid_size = snapping_grid_size

    #     # self._root[self._root_item]["snapping_grid_position"] = Vector(0, 0) # TODO: move
    #     self.snapping_grid_position = snapping_grid_position

    #     if "absolute-snapping" in kwargs:
    #         self.absolute_snapping = kwargs.pop("absolute-snapping")
    #     else:
    #         self.absolute_snapping = absolute_snapping

    #     # self._root[self._root_item]["position-relative-to-grid"] = Vector(0, 0) # TODO: move
    #     if "position-relative-to-grid" in kwargs:
    #         self.position_relative_to_grid = kwargs.pop("position-relative-to-grid")
    #     else:
    #         self.position_relative_to_grid = position_relative_to_grid

    #     ### DATA ###

    #     # Data lists
    #     # self._root[self._root_item]["entities"] = EntityList(
    #     #     self, entities
    #     # )
    #     self._root._entities = EntityList(
    #         self,
    #         entities,
    #     )

    #     # if "tiles" in kwargs:
    #     # self._root[self._root_item]["tiles"] = TileList(
    #     #     self, tiles
    #     # )
    #     self._root._tiles = TileList(
    #         self,
    #         tiles,
    #     )

    #     # self._root[self._root_item]["schedules"] = ScheduleList(
    #     #     schedules
    #     # )
    #     self._root._schedules = ScheduleList(schedules)

    #     self._root._wires = [] if wires is None else wires

    #     self.stock_connections = [] if stock_connections is None else stock_connections

    #     self.index = index

    #     # A bit scuffed, but
    #     for kwarg, value in kwargs.items():
    #         self._root[kwarg] = value

    #     # 1.0 code
    #     # Convert circuit and power connections to Associations
    #     # for entity in self.entities:
    #     #     if hasattr(entity, "connections"):  # Wire connections
    #     #         connections: Connections = entity.connections
    #     #         for side in connections.true_model_fields():
    #     #             if connections[side] is None:
    #     #                 continue

    #     #             if side in {"1", "2"}:
    #     #                 for color, _ in connections[side]:  # TODO fix
    #     #                     connection_points = connections[side][color]
    #     #                     if connection_points is None:
    #     #                         continue
    #     #                     for point in connection_points:
    #     #                         old = point["entity_id"] - 1
    #     #                         point["entity_id"] = Association(self.entities[old])

    #     #             elif side in {"Cu0", "Cu1"}:  # pragma: no branch
    #     #                 connection_points = connections[side]
    #     #                 if connection_points is None:
    #     #                     continue  # pragma: no coverage
    #     #                 for point in connection_points:
    #     #                     old = point["entity_id"] - 1
    #     #                     point["entity_id"] = Association(self.entities[old])

    #     #     if hasattr(entity, "neighbours"):  # Power pole connections
    #     #         neighbours = entity.neighbours
    #     #         for i, neighbour in enumerate(neighbours):
    #     #             neighbours[i] = Association(self.entities[neighbour - 1])

    #     # Change all locomotive numbers to use Associations
    #     for schedule in self.schedules:
    #         for i, locomotive in enumerate(schedule.locomotives):
    #             if isinstance(locomotive, int):
    #                 entity: Entity = self.entities[locomotive - 1]
    #                 schedule.locomotives[i] = Association(entity)

    #     # Change all wire numbers to use Associations
    #     for i, wire in enumerate(self.wires):
    #         if isinstance(wire[0], int):
    #             entity1 = self.entities[wire[0] - 1]
    #             wire[0] = Association(entity1)
    #         if isinstance(wire[2], int):
    #             entity2 = self.entities[wire[2] - 1]
    #             wire[2] = Association(entity2)
    #         # self.wires[i] = [Association(entity1), wire[1], Association(entity2), wire[3]]

    #     if validate:
    #         self.validate(mode=validate).reissue_all()

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
    # Blueprint properties
    # =========================================================================

    @property
    def root_item(self) -> Literal["blueprint"]:
        return "blueprint"

    # =========================================================================

    # TODO: this should be an evolve
    item: str = attrs.field(
        default="blueprint",
        # TODO: validators
        metadata={
            "omit": False,
            "location": (lambda cls: cls.root_item.fget(cls), "item"),
        },
    )
    # TODO: description

    # =========================================================================

    snapping_grid_size: Optional[Vector] = attrs.field(
        default=Vector(0, 0),
        converter=Vector.from_other,
        validator=instance_of(Vector),
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

    # @property
    # def snapping_grid_size(self) -> Optional[Vector]:
    #     """
    #     Sets the size of the snapping grid to use. The presence of this entry
    #     determines whether or not the Blueprint will have a snapping grid or
    #     not.

    #     The value can be set either as a ``dict`` with ``"x"`` and ``"y"`` keys,
    #     or as a sequence of ints.

    #     :getter: Gets the size of the snapping grid, or ``None`` if not set.
    #     :setter: Sets the size of the snapping grid. Removes the attribute if
    #         set to ``None``
    #     """
    #     # return self._root[self._root_item].get("snap-to-grid", None)
    #     return self._root.blueprint._snap_to_grid

    # @snapping_grid_size.setter
    # def snapping_grid_size(self, value: Union[Vector, PrimitiveVector, None]):
    #     # if self.validate_assignment:
    #     #     result = attempt_and_reissue(
    #     #         self,
    #     #         self.Format.BlueprintObject,
    #     #         self._root.blueprint,
    #     #         "snapping_grid_size",
    #     #         value
    #     #     )
    #     #     self._root[self._root_item]["snapping_grid_size"] = result
    #     # else:
    #     #     self._root[self._root_item]["snapping_grid_size"] = value
    #     if value is None:
    #         self._root.blueprint._snap_to_grid.update_from_other((0, 0), int)
    #     else:
    #         self._root.blueprint._snap_to_grid.update_from_other(value, int)

    # =========================================================================

    snapping_grid_position: Vector = attrs.field(
        default=Vector(0, 0),
        eq=False,
        repr=False,
        converter=Vector.from_other,
        validator=instance_of(Vector),
        metadata={"omit": True},
    )
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
    """

    # @property
    # def snapping_grid_position(self) -> Vector:
    #     """
    #     Sets the position of the snapping grid. Offsets all of the
    #     positions of the entities by this amount, effectively acting as a
    #     translation in relation to the snapping grid.

    #     .. NOTE::

    #         This function does not offset each entities position until export!

    #     :getter: Gets the offset amount of the snapping grid, or ``None`` if not
    #         set.
    #     :setter: Sets the offset amount of the snapping grid. Removes the
    #         attribute if set to ``None``.
    #     """
    #     # return self._root[self._root_item].get("snapping_grid_position", None)
    #     return self._root.blueprint._snapping_grid_position

    # @snapping_grid_position.setter
    # def snapping_grid_position(self, value: Union[Vector, PrimitiveVector, None]):
    #     # if value is None:
    #     #     self._root[self._root_item]["snapping_grid_position"].update_from_other((0, 0), int)
    #     # else:
    #     #     self._root[self._root_item]["snapping_grid_position"].update_from_other(value, int)
    #     if value is None:
    #         self._root.blueprint._snapping_grid_position.update_from_other((0, 0), int)
    #     else:
    #         self._root.blueprint._snapping_grid_position.update_from_other(value, int)

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

    # @property
    # def absolute_snapping(self) -> Optional[bool]:
    #     """
    #     Whether or not the blueprint uses absolute positioning or relative
    #     positioning for the snapping grid. On import, a value of ``None`` is
    #     interpreted as a default ``True``.

    #     :getter: Gets whether or not this blueprint uses absolute positioning,
    #         or ``None`` if not set.
    #     :setter: Sets whether or not to use absolute-snapping. Removes the
    #         attribute if set to ``None``.

    #     :exception TypeError: If set to anything other than a ``bool`` or
    #         ``None``.
    #     """
    #     return self._root[self._root_item].get("absolute-snapping", None)

    # @absolute_snapping.setter
    # def absolute_snapping(self, value: Optional[bool]):
    #     if self.validate_assignment:
    #         result = attempt_and_reissue(
    #             self,
    #             self.Format.BlueprintObject,
    #             self._root.blueprint,
    #             "absolute_snapping",
    #             value,
    #         )
    #         self._root[self._root_item]["absolute_snapping"] = result
    #     else:
    #         self._root[self._root_item]["absolute_snapping"] = value

    # =========================================================================

    position_relative_to_grid: Vector = attrs.field(
        default=Vector(0, 0),
        converter=Vector.from_other,
        validator=instance_of(Vector),  # TODO: on_setattr
    )
    """
    The absolute position of the snapping grid in the world. Only used if
    ``absolute_snapping`` is set to ``True`` or ``None``.

    :getter: Gets the absolute grid-position offset.
    :setter: Sets the absolute grid-position offset. Is given a value of
        ``(0, 0)`` if set to ``None``
    """

    # @property
    # def position_relative_to_grid(self) -> Optional[Vector]:
    #     """
    #     The absolute position of the snapping grid in the world. Only used if
    #     ``absolute_snapping`` is set to ``True`` or ``None``.

    #     :getter: Gets the absolute grid-position offset.
    #     :setter: Sets the absolute grid-position offset. Is given a value of
    #         ``(0, 0)`` if set to ``None``
    #     """
    #     # return self._root[self._root_item]["position-relative-to-grid"]
    #     return self._root.blueprint._position_relative_to_grid

    # @position_relative_to_grid.setter
    # def position_relative_to_grid(self, value: Union[Vector, PrimitiveVector, None]):
    #     # if value is None:
    #     #     self._root[self._root_item]["position-relative-to-grid"].update_from_other(
    #     #         (0, 0), int
    #     #     )
    #     # else:
    #     #     self._root[self._root_item]["position-relative-to-grid"].update_from_other(
    #     #         value, int
    #     #     )
    #     if value is None:
    #         self._root.blueprint._position_relative_to_grid.update_from_other(
    #             (0, 0), int
    #         )
    #     else:
    #         self._root.blueprint._position_relative_to_grid.update_from_other(
    #             value, int
    #         )

    # =========================================================================

    # def _set_entities(self, _: attrs.Attribute, value: Any):
    #     if value is None:
    #         return EntityList(self)
    #     elif isinstance(value, EntityList):
    #         return EntityList(self, value._root)
    #     else:
    #         return EntityList(self, value)

    # entities: EntityList = attrs.field(
    #     on_setattr=_set_entities,
    # )
    # """
    # The list of the Blueprint's entities. Internally the list is a custom
    # class named :py:class:`.EntityList`, which has all the normal properties
    # of a regular list, as well as some extra features. For more information
    # on ``EntityList``, check out this writeup
    # :ref:`here <handbook.blueprints.blueprint_differences>`.
    # """

    # @entities.default
    # def get_entities_default(self) -> EntityList:
    #     return EntityList(self)

    # @property
    # def entities(self) -> EntityList:
    #     """
    #     The list of the Blueprint's entities. Internally the list is a custom
    #     class named :py:class:`.EntityList`, which has all the normal properties
    #     of a regular list, as well as some extra features. For more information
    #     on ``EntityList``, check out this writeup
    #     :ref:`here <handbook.blueprints.blueprint_differences>`.

    #     :getter: Gets the EntityList object associated with this blueprint.
    #     :setter: Sets the EntityList object associated with this blueprint. If
    #         a regular list is passed in, it is converted to an EntityList, and
    #         setting to ``None`` clears the list.
    #     """
    #     # return self._root[self._root_item]["entities"]
    #     return self._root._entities

    # @entities.setter
    # @reissue_warnings
    # def entities(self, value: Union[EntityList, list[EntityLike], None]):
    #     if value is None:
    #         # self._root[self._root_item]["entities"].clear()
    #         self._root._entities.clear()
    #     elif isinstance(value, EntityList):
    #         # Just don't ask
    #         # self._root["entities"] = copy.deepcopy(value, memo={"new_parent": self})
    #         # self._root[self._root_item]["entities"] = EntityList(self, value._root)
    #         self._root._entities = EntityList(self, value._root)
    #     else:
    #         # self._root[self._root_item]["entities"] = EntityList(self, value)
    #         self._root._entities = EntityList(self, value)

    # =========================================================================

    def _set_tiles(self, _: attrs.Attribute, value: Any):
        if value is None:
            return TileList(self)
        elif isinstance(value, TileList):
            return TileList(self, value._root)
        else:
            return TileList(self, value)

    tiles: TileList = attrs.field(
        on_setattr=_set_tiles,
    )
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

    @tiles.default
    def get_tiles_default(self):
        return TileList(self)

    # @property
    # def tiles(self) -> TileList:
    #     """
    #     The list of the Blueprint's tiles. Internally the list is a custom
    #     class named :py:class:`~.TileList`, which has all the normal properties
    #     of a regular list, as well as some extra features.

    #     :example:

    #     .. code-block:: python

    #         blueprint.tiles.append("landfill")
    #         assert isinstance(blueprint.tiles[-1], Tile)
    #         assert blueprint.tiles[-1].name == "landfill"

    #         blueprint.tiles.insert(0, "refined-hazard-concrete", position=(1, 0))
    #         assert blueprint.tiles[0].position == {"x": 1.5, "y": 1.5}

    #         blueprint.tiles = None
    #         assert len(blueprint.tiles) == 0
    #     """
    #     # return self._root[self._root_item]["tiles"]
    #     return self._root._tiles

    # @tiles.setter
    # @reissue_warnings
    # def tiles(self, value: Union[TileList, list[Tile], None]):
    #     if value is None:
    #         # self._root[self._root_item]["tiles"].clear()
    #         self._root._tiles.clear()
    #     elif isinstance(value, TileList):
    #         # self._root[self._root_item]["tiles"] = TileList(self, value._root)
    #         self._root._tiles = TileList(self, value._root)
    #     else:
    #         # self._root[self._root_item]["tiles"] = TileList(self, value)
    #         self._root._tiles = TileList(self, value)

    # =========================================================================

    # def _set_schedules(self, _: attrs.Attribute, value: Any):
    #     # TODO: this needs to be more complex. What about associations already
    #     # set to one blueprint being copied over to another? Should probably
    #     # wipe the locomotives of each schedule when doing so
    #     if value is None:
    #         return ScheduleList()
    #     elif isinstance(value, ScheduleList):
    #         return value
    #     else:
    #         return ScheduleList(value)

    # schedules: ScheduleList = attrs.field(
    #     on_setattr=_set_schedules,
    # )
    # """
    # A list of the Blueprint's train schedules.

    # .. seealso::

    #     `<https://wiki.factorio.com/Blueprint_string_format#Schedule_object>`_

    # :getter: Gets the schedules of the Blueprint.
    # :setter: Sets the schedules of the Blueprint. Defaults to an empty
    #     :py:class:`.ScheduleList` if set to ``None``.

    # :exception ValueError: If set to anything other than a ``list`` of
    #     :py:class:`.Schedule` or .
    # """

    # @schedules.default
    # def _(self) -> ScheduleList:
    #     return ScheduleList()

    # @property
    # def schedules(self) -> ScheduleList:
    #     """
    #     A list of the Blueprint's train schedules.

    #     .. seealso::

    #         `<https://wiki.factorio.com/Blueprint_string_format#Schedule_object>`_

    #     :getter: Gets the schedules of the Blueprint.
    #     :setter: Sets the schedules of the Blueprint. Defaults to an empty
    #         :py:class:`.ScheduleList` if set to ``None``.

    #     :exception ValueError: If set to anything other than a ``list`` of
    #         :py:class:`.Schedule` or .
    #     """
    #     # return self._root[self._root_item]["schedules"]
    #     return self._root._schedules

    # @schedules.setter
    # @reissue_warnings
    # def schedules(self, value: Union[ScheduleList, list[Schedule], None]):
    #     # TODO: this needs to be more complex. What about associations already
    #     # set to one blueprint being copied over to another? Should probably
    #     # wipe the locomotives of each schedule when doing so
    #     if value is None:
    #         # self._root[self._root_item]["schedules"] = ScheduleList()
    #         self._root._schedules.clear()
    #     elif isinstance(value, ScheduleList):
    #         # self._root[self._root_item]["schedules"] = value
    #         self._root._schedules = value
    #     else:
    #         # self._root[self._root_item]["schedules"] = ScheduleList(value)
    #         self._root._schedules = ScheduleList(value)

    # =========================================================================

    wires: list[list[Association, int, Association, int]] = attrs.field(
        factory=list,
    )
    """
    A list of the wire connections in this blueprint.

    Wires are specified as a list of 4 integers; the first pair of numbers
    represents the first entity, and the second pair represents the second
    entity. The first number of each pair represents the ``entity_number``
    of the corresponding entity in the list, and the second number indicates
    what type of connection it is.

    When exported to JSON, the associations in each wire are resolved to 
    integers corresponding to the given ``"entity_number"`` in the resulting
    ``"entities"`` list.

    TODO: more detail

    :getter: Gets the wires of the Blueprint.
    :setter: Sets the wires of the Blueprint. Defaults to an empty list if
        set to ``None``.
    """

    # @property
    # def wires(self) -> list[list[int]]:
    #     """
    #     A list of the wire connections in this blueprint.

    #     Wires are specified as a list of 4 integers; the first pair of numbers
    #     represents the first entity, and the second pair represents the second
    #     entity. The first number of each pair represents the ``entity_number``
    #     of the corresponding entity in the list, and the second number indicates
    #     what type of connection it is.

    #     TODO: more detail

    #     :getter: Gets the wires of the Blueprint.
    #     :setter: Sets the wires of the Blueprint. Defaults to an empty list if
    #         set to ``None``.
    #     """
    #     return self._root._wires

    # @wires.setter
    # def wires(self, value: list[list[int]]) -> None:
    #     if value is None:
    #         self._root._wires = []
    #     else:
    #         self._root._wires = value

    # =========================================================================

    stock_connections: list[StockConnection] = attrs.field(  # TODO: annotations
        factory=list,
    )
    """
    TODO
    """

    # @property
    # def stock_connections(self) -> list[dict]:
    #     """
    #     TODO
    #     """
    #     return self._root.blueprint.stock_connections

    # @stock_connections.setter
    # def stock_connections(self, value: Optional[list[dict]]) -> None:
    #     if value is None:
    #         self._root.blueprint.stock_connections = []
    #     else:
    #         self._root.blueprint.stock_connections = value

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
        # Create a copy of root, since we don't want to clobber the original
        # data when creating a dict representation
        # We skip copying the special lists because we have to handle their
        # conversion specifically and carefully
        # root_copy = {
        #     self._root_item: {
        #         k: v
        #         for k, v in self._root[self._root_item].items()
        #         if k not in {"entities", "tiles", "schedules"}
        #     },
        # }
        # if self.index is not None:
        #     root_copy["index"] = self.index

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
        )

        # # Construct a model with the flattened data, not running any validation
        # # We do a number of submodels manually since model_construct is not
        # # recursive (woe be upon me)
        # out_model = Blueprint.Format.model_construct(**root_copy)
        # out_model.blueprint = Blueprint.Format.BlueprintObject.model_construct(
        #     **out_model.blueprint
        # )
        # if out_model.blueprint.icons is not None:
        #     out_model.blueprint.icons = Icons.model_construct(out_model.blueprint.icons)
        # if out_model.blueprint.snap_to_grid is not None:
        #     out_model.blueprint.snap_to_grid = (
        #         out_model.blueprint.snap_to_grid.to_dict()
        #     )
        # if out_model.blueprint.position_relative_to_grid is not None:
        #     out_model.blueprint.position_relative_to_grid = (
        #         out_model.blueprint.position_relative_to_grid.to_dict()
        #     )

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

        # # We then create an output dict
        # out_dict = out_model.model_dump(
        #     by_alias=True,
        #     exclude_none=True,
        #     exclude_defaults=True,
        #     warnings=False,  # until `model_construct` is properly recursive
        # )

        # print(result)
        # print(self.snapping_grid_size)
        # print(self.position_relative_to_grid)

        if "snap-to-grid" in result["blueprint"] and result["blueprint"][
            "snap-to-grid"
        ] == {"x": 0, "y": 0}:
            del result["blueprint"]["snap-to-grid"]
        if "position-relative-to-grid" in result["blueprint"] and result["blueprint"][
            "position-relative-to-grid"
        ] == {"x": 0, "y": 0}:
            del result["blueprint"]["position-relative-to-grid"]

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
    def ensure_reasonable_size(self, mode: Optional[ValidationMode] = None):
        mode = mode if mode is not None else self.validate_assignment
        if mode:
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

        memo["new_parent"] = result # TODO: this should really be fixed, because then we can use "deepcopy_func"
        for attr in attrs.fields(cls):
            if attr.name == "wires":  # special
                new_wires = copy.deepcopy(getattr(self, attr.name), memo)
                for wire in new_wires:
                    wire[0] = swap_association(wire[0])
                    wire[2] = swap_association(wire[2])

                object.__setattr__(result, attr.name, new_wires)
            elif attr.name == "schedules":
                new_schedules = copy.deepcopy(getattr(self, attr.name), memo)
                for schedule in new_schedules:
                    schedule: Schedule
                    schedule.locomotives = [swap_association(loco) for loco in schedule.locomotives]

                object.__setattr__(result, attr.name, new_schedules)
            elif attr.name == "stock_connections":  # special
                new_connections: list[StockConnection] = copy.deepcopy(
                    getattr(self, attr.name), memo
                )
                for connection in new_connections:
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


# TODO: this should be version 2.0
draftsman_converters.add_schema(
    {"$id": "factorio:blueprint"},
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
        ("blueprint", "schedules"): fields.schedules.name,
        ("blueprint", "wires"): fields.wires.name,
        ("blueprint", "stock_connections"): fields.stock_connections.name,
    },
)


def structure_blueprint_1_0_factory(t: type):
    default_blueprint_hook = (
        draftsman_converters.get_version((1, 0))
        .converters[(False, False)]
        .get_structure_hook(t)
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
                if entity["name"] in legacy_entity_conversions:
                    entity["name"] = legacy_entity_conversions[entity["name"]]

                # Swap from old 8-direction to modern 16-direction
                if "direction" in entity:
                    entity["direction"] = LegacyDirection(entity["direction"]).to_modern()

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
                            # Make sure we don't add the reverse as a duplicate
                            if [
                                entity_id,
                                wire_types[circuit_id],
                                entity["entity_number"],
                                wire_types[side],
                            ] not in wires:
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
