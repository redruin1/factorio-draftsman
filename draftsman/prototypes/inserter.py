# inserter.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import (
    CircuitSetFiltersMixin,
    FiltersMixin,
    StackSizeMixin,
    CircuitReadHandMixin,
    InserterModeOfOperationMixin,
    CircuitConditionMixin,
    LogisticConditionMixin,
    CircuitEnableMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    EnergySourceMixin,
    DirectionalMixin,
)
from draftsman.classes.vector import Vector
from draftsman.constants import Direction
from draftsman.serialization import draftsman_converters
from draftsman.validators import instance_of, one_of

from draftsman.data.entities import inserters

import attrs
from typing import Literal, Optional


@attrs.define
class Inserter(
    CircuitSetFiltersMixin,
    FiltersMixin,
    StackSizeMixin,
    CircuitReadHandMixin,
    InserterModeOfOperationMixin,
    CircuitConditionMixin,
    LogisticConditionMixin,
    CircuitEnableMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    EnergySourceMixin,
    DirectionalMixin,
    Entity,
):
    """
    An entity with a swinging arm that can move items between machines.
    """

    @property
    def similar_entities(self) -> list[str]:
        return inserters

    # =========================================================================

    @property
    def pickup_position(self) -> Vector:
        """
        Gets the current position in world space that this inserter will grab
        items from.

        This value is the sum of this entity's :py:attr:`.global_position`, it's
        :py:attr:`.prototype` ``"pickup_position"``, and any custom
        :py:attr:`.pickup_position_offset`. If this entity has no known
        prototype or pickup offset, then both default to ``(0, 0)``.
        """
        try:
            direction_matrix = {
                Direction.NORTH: lambda p: p,
                Direction.EAST: lambda p: (-p[1], p[0]),
                Direction.SOUTH: lambda p: (-p[0], -p[1]),
                Direction.WEST: lambda p: (p[1], -p[0]),
            }
            pickup_position = direction_matrix[self.direction](
                self.prototype["pickup_position"]
            )
        except KeyError:  # Unknown entity/direction case
            pickup_position = (0, 0)
        return self.global_position + pickup_position + self.pickup_position_offset

    # =========================================================================

    @property
    def drop_position(self) -> Vector:
        """
        Gets the current position in world space that this inserter will drop
        items to.

        This value is the sum of this entity's :py:attr:`.global_position`, it's
        :py:attr:`.prototype` ``"pickup_position"``, and any custom
        :py:attr:`.pickup_position_offset`. If this entity has no known
        prototype or pickup offset, then both default to ``(0, 0)``.
        """
        try:
            direction_matrix = {
                Direction.NORTH: lambda p: p,
                Direction.EAST: lambda p: (-p[1], p[0]),
                Direction.SOUTH: lambda p: (-p[0], -p[1]),
                Direction.WEST: lambda p: (p[1], -p[0]),
            }
            drop_position = direction_matrix[self.direction](
                self.prototype["insert_position"]
            )
        except KeyError:  # Unknown entity/direction case
            drop_position = (0, 0)
        return self.global_position + drop_position + self.drop_position_offset

    # =========================================================================

    pickup_position_offset: Optional[Vector] = attrs.field(
        factory=lambda: Vector(0, 0),
        converter=Vector.from_other,
        validator=instance_of(Optional[Vector]),
    )
    """
    .. serialized::

        This attribute is imported/exported from blueprint strings.

    The configured pickup position "offset" used for when inserters have custom 
    pickup/dropoff locations (think adjustable inserter mods).

    The value is specified as an X/Y coordinate offset from where the position
    would "normally" be. This offset coordinate is defined in world axes, so
    a offset position of ``(0, 1)`` will always shift the inserter's hand 
    position 1 tile southward.

    .. NOTE::

        Only inserters with the ``"allow_custom_vectors"`` key set to ``True`` 
        in their :py:attr:`.prototype` definition will actually allow setting
        these values to have an effect in game. In other words, only modded 
        inserters (or vanilla inserters which have been tweaked with mods) can
        actually change this behavior.
    """

    # =========================================================================

    drop_position_offset: Optional[Vector] = attrs.field(
        factory=lambda: Vector(0, 0),
        converter=Vector.from_other,
        validator=instance_of(Optional[Vector]),
    )
    """
    .. serialized::

        This attribute is imported/exported from blueprint strings.

    The configured drop position "offset" used for when inserters have custom 
    pickup/dropoff locations (think adjustable inserter mods).

    The value is specified as an X/Y coordinate offset from where the position
    would "normally" be. This offset coordinate is defined in world axes, so
    a offset position of ``(0, 1)`` will always shift the inserter's hand 
    position 1 tile southward.

    .. NOTE::

        Only inserters with the ``"allow_custom_vectors"`` key set to ``True`` 
        in their :py:attr:`.prototype` definition will actually allow setting
        these values to have an effect in game. In other words, only modded 
        inserters (or vanilla inserters which have been tweaked with mods) can
        actually change this behavior.
    """

    # =========================================================================

    filter_mode: Literal["whitelist", "blacklist"] = attrs.field(
        default="whitelist", validator=one_of("whitelist", "blacklist")
    )
    """
    .. serialized::

        This attribute is imported/exported from blueprint strings.

    The mode that the given filter should operate under, if the inserter is 
    configured to operate with filters.
    """

    # =========================================================================

    spoil_priority: Literal["spoiled-first", "fresh-first", None] = attrs.field(
        default=None,
        validator=one_of("spoiled-first", "fresh-first", None),
    )
    """
    .. serialized::

        This attribute is imported/exported from blueprint strings.

    Whether or not this inserter should prefer most fresh or most spoiled
    items when grabbing from an inventory. If set to ``None``, this inserter
    will ignore the spoiled value of items from it's pickup logic entirely.
    """

    # =========================================================================

    def merge(self, other: "Inserter"):
        super().merge(other)

        self.circuit_set_filters = other.circuit_set_filters
        self.pickup_position_offset = other.pickup_position_offset
        self.drop_position_offset = other.drop_position_offset
        self.filter_mode = other.filter_mode
        self.spoil_priority = other.spoil_priority

    # =========================================================================

    __hash__ = Entity.__hash__


@attrs.define
class _Export:
    pickup_position_offset: list[float] = [0, 0]
    drop_position_offset: list[float] = [0, 0]


_export_fields = attrs.fields(_Export)


draftsman_converters.get_version((1, 0)).add_hook_fns(
    Inserter,
    lambda fields: {
        ("control_behavior", "circuit_set_filters"): fields.circuit_set_filters.name,
        "pickup_position": fields.pickup_position_offset.name,
        "drop_position": fields.drop_position_offset.name,
        "filter_mode": fields.filter_mode.name,
        None: fields.spoil_priority.name,
    },
    lambda fields, _: {
        ("control_behavior", "circuit_set_filters"): fields.circuit_set_filters.name,
        "pickup_position": (
            _export_fields.pickup_position_offset,
            lambda inst: [inst.pickup_position_offset.x, inst.pickup_position_offset.y],
        ),
        "drop_position": (
            _export_fields.drop_position_offset,
            lambda inst: [inst.drop_position_offset.x, inst.drop_position_offset.y],
        ),
        "filter_mode": fields.filter_mode.name,
        None: fields.spoil_priority.name,
    },
)

draftsman_converters.get_version((2, 0)).add_hook_fns(
    Inserter,
    lambda fields: {
        ("control_behavior", "circuit_set_filters"): fields.circuit_set_filters.name,
        "pickup_position": fields.pickup_position_offset.name,
        "drop_position": fields.drop_position_offset.name,
        "filter_mode": fields.filter_mode.name,
        "spoil_priority": fields.spoil_priority.name,
    },
    lambda fields, _: {
        ("control_behavior", "circuit_set_filters"): fields.circuit_set_filters.name,
        "pickup_position": (
            _export_fields.pickup_position_offset,
            lambda inst: [inst.pickup_position_offset.x, inst.pickup_position_offset.y],
        ),
        "drop_position": (
            _export_fields.drop_position_offset,
            lambda inst: [inst.drop_position_offset.x, inst.drop_position_offset.y],
        ),
        "filter_mode": fields.filter_mode.name,
        "spoil_priority": fields.spoil_priority.name,
    },
)
