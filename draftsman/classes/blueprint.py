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

# from draftsman._factorio_version import __factorio_version_info__
from draftsman.classes.blueprintable import Blueprintable
from draftsman.classes.entity_list import EntityList
from draftsman.classes.exportable import ValidationResult
from draftsman.classes.transformable import Transformable
from draftsman.classes.collection import Collection
from draftsman.classes.vector import Vector
from draftsman.constants import ValidationMode
from draftsman.error import (
    DraftsmanError,
    UnreasonablySizedBlueprintError,
    InvalidAssociationError,
)
from draftsman.serialization import draftsman_converters
from draftsman.entity import get_entity_class
from draftsman.utils import (
    AABB,
    aabb_to_dimensions,
    extend_aabb,
    flatten_entities,
    flatten_tiles,
    flatten_stock_connections,
)
from draftsman.validators import classvalidator, conditional, instance_of, try_convert

import attrs
from builtins import int
from typing import Literal, Optional


def _throw_invalid_association(entity):
    raise InvalidAssociationError(  # pragma: no coverage
        "'{}' at {} is connected to an entity that no longer exists".format(
            entity["name"], entity["position"]
        )
    )


@draftsman.define
class Blueprint(Transformable, Collection, Blueprintable):
    """
    Factorio Blueprint class. Contains and maintains a list of ``EntityLikes``
    and ``Tiles`` and a selection of other metadata. Inherits all the functions
    and attributes you would expect, as well as some extra functionality.
    """

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

        for group in self.groups:
            area = extend_aabb(area, group.get_world_bounding_box())

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
        self, mode: ValidationMode = ValidationMode.STRICT
    ) -> ValidationResult:
        result = super().validate(mode=mode)

        result += self.entities.validate(mode=mode)
        result += self.tiles.validate(mode=mode)
        # TODO: self.schedules.validate(mode=mode)

        for class_validator in type(self).__attrs_class_validators__:
            class_validator(self, mode=mode)  # TODO: pass in error/warning list

        return result

    def to_dict(
        self,
        version: Optional[tuple[int, ...]] = None,
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

        def flatten_collection(inst: Blueprint):
            schedules = [schedule for schedule in inst.schedules]
            wires = [wire for wire in inst.wires]
            for group in inst.groups:
                s, w = flatten_collection(group)
                schedules += s
                wires += w
            return schedules, wires

        flattened_entities = flatten_entities(self)
        flattened_tiles = flatten_tiles(self)
        (flattened_schedules, flattened_wires) = flatten_collection(self)

        entities_out = []
        for i, entity in enumerate(flattened_entities):
            # Get a copy of the dict representation of the Entity
            # (At this point, Associations are not copied and still point to original)
            serialized_entity = entity.to_dict(
                version=version,
                exclude_none=exclude_none,
                exclude_defaults=exclude_defaults,
                entity_number=i + 1,
            )
            if not isinstance(serialized_entity, dict):
                raise DraftsmanError(
                    "{}.to_dict() must return a dict".format(type(entity).__name__)
                )
            # Add this to the output's entities and set it's entity_number
            entities_out.append(serialized_entity)

        result[self.root_item]["entities"] = entities_out

        tiles_out = []
        for i, tile in enumerate(flattened_tiles):
            serialized_tile = tile.to_dict(
                version=version,
                exclude_none=exclude_none,
                exclude_defaults=exclude_defaults,
            )
            tiles_out.append(serialized_tile)

        result[self.root_item]["tiles"] = tiles_out

        schedules_out = []
        for schedule in flattened_schedules:
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

        result[self.root_item]["schedules"] = schedules_out

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

        # Wires
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

        result[self.root_item]["wires"] = wires_out

        if "stock_connections" in result[self.root_item]:
            for stock_connection in result[self.root_item]["stock_connections"]:
                stock_connection["stock"] = get_index(stock_connection["stock"])
                if "front" in stock_connection:
                    stock_connection["front"] = get_index(stock_connection["front"])
                if "back" in stock_connection:
                    stock_connection["back"] = get_index(stock_connection["back"])

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


draftsman_converters.get_version((1, 0)).add_hook_fns(
    Blueprint,
    lambda fields, converter: {
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
        ("blueprint", "entities"): (  # Custom structure function
            fields.entities,
            lambda value, _, inst: EntityList(
                inst,
                [
                    converter.structure(elem, get_entity_class(elem.get("name", None)))
                    for elem in value
                ],
            ),
        ),
        ("blueprint", "tiles"): fields.tiles.name,
        # None: fields.wires.name,
        ("blueprint", "schedules"): fields.schedules.name,
        # None: fields.stock_connections.name,
    },
    lambda fields, converter: {
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
        # None: fields.wires.name,
        ("blueprint", "schedules"): fields.schedules.name,
        # None: fields.stock_connections.name,
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
        # TODO: figure out migration
        # legacy_entity_conversions = {
        #     "curved-rail": "legacy-curved-rail",
        #     "straight-rail": "legacy-straight-rail",
        #     "logistic-chest-requester": "requester-chest",
        #     "logistic-chest-buffer": "buffer-chest",
        #     "logistic-chest-storage": "storage-chest",
        #     "logistic-chest-active-provider": "active-provider-chest",
        #     "logistic-chest-passive-provider": "passive-provider-chest",
        #     "filter-inserter": "inserter",
        #     "stack-inserter": "bulk-inserter",
        #     "stack-filter-inserter": "bulk-inserter",
        # }
        # TODO: just use defines already...
        wire_types = {
            ("1", "red"): 1,
            ("1", "green"): 2,
            ("2", "red"): 3,
            ("2", "green"): 4,
            "Cu0": 5,
            "Cu1": 6,
        }

        blueprint_dict = d["blueprint"]

        wires = blueprint_dict["wires"] = []
        if "entities" in blueprint_dict:
            for entity in blueprint_dict["entities"]:
                # Convert entities to their modern equivalents
                # if entity["name"] in legacy_entity_conversions:  # pragma: no coverage
                #     entity["name"] = legacy_entity_conversions[entity["name"]]

                # Iterate over the "connections" property in each entity and
                # convert it to the better "wires" list in Factorio 2.0
                if "connections" in entity:
                    connections = entity["connections"]
                    for side in {"1", "2"}:
                        if side not in connections:
                            continue

                        for color in connections[side]:
                            connection_points = connections[side][color]

                            for point in connection_points:
                                entity_id = point["entity_id"]
                                circuit_id = str(point.get("circuit_id", 1))
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

                # Do a similar conversion with neighbours, which also get lumped
                # into "wires"
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

        if wires == []:
            del blueprint_dict["wires"]

        return default_blueprint_hook(d, _)

    return structure_blueprint_1_0


draftsman_converters.get_version((1, 0)).register_structure_hook(
    Blueprint, structure_blueprint_1_0_factory(Blueprint)
)

draftsman_converters.get_version((2, 0)).add_hook_fns(
    Blueprint,
    lambda fields, converter: {
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
        ("blueprint", "entities"): (  # Custom structure function
            fields.entities,
            lambda value, _, inst: EntityList(
                inst,
                [
                    converter.structure(elem, get_entity_class(elem.get("name", None)))
                    for elem in value
                ],
            ),
        ),
        ("blueprint", "tiles"): fields.tiles.name,
        ("blueprint", "wires"): fields.wires.name,
        ("blueprint", "schedules"): fields.schedules.name,
        ("blueprint", "stock_connections"): fields.stock_connections.name,
    },
    lambda fields, converter: {
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
        ("blueprint", "stock_connections"): (
            fields.stock_connections,
            lambda inst: [
                converter.unstructure(elem) for elem in flatten_stock_connections(inst)
            ],
        ),
    },
)
