# rail_signal.py

from draftsman.classes.collision_set import CollisionSet
from draftsman.classes.entity import Entity
from draftsman.classes.mixins import (
    ReadRailSignalMixin,
    CircuitConditionMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    DirectionalMixin,
)
from draftsman.constants import Direction, SIXTEEN_WAY_DIRECTIONS
from draftsman.serialization import draftsman_converters
from draftsman.utils import fix_incorrect_pre_init
from draftsman.validators import instance_of

from draftsman.data.entities import rail_signals

import attrs
from typing import Optional


@fix_incorrect_pre_init
@attrs.define
class RailSignal(
    ReadRailSignalMixin,
    CircuitConditionMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    DirectionalMixin,
    Entity,
):
    """
    A rail signal that determines whether or not trains can pass along their
    rail block.
    """

    @property
    def similar_entities(self) -> list[str]:
        return rail_signals

    # =========================================================================

    @property
    def collision_set_rotated(self) -> bool:
        return False

    # =========================================================================

    @property
    def valid_directions(self) -> set[Direction]:
        return SIXTEEN_WAY_DIRECTIONS

    # =========================================================================

    @property
    def collision_set(self) -> Optional[CollisionSet]:
        # This entity doesn't actually rotate it's collision box
        return self.static_collision_set

    # =========================================================================

    circuit_enabled: bool = attrs.field(
        default=False,
        validator=instance_of(bool),
    )
    """
    .. serialized::

        This attribute is imported/exported from blueprint strings.

    Whether or not a connected circuit network should control the state of this
    rail signal.
    """

    # =========================================================================

    read_signal: bool = attrs.field(
        default=True,
        validator=instance_of(bool),
    )
    """
    .. serialized::

        This attribute is imported/exported from blueprint strings.

    Whether or not to read the state of the rail signal as their output
    signals.
    """

    # =========================================================================

    __hash__ = Entity.__hash__


draftsman_converters.add_hook_fns(
    RailSignal,
    lambda fields: {
        ("control_behavior", "circuit_close_signal"): fields.circuit_enabled.name,
        ("control_behavior", "circuit_read_signal"): fields.read_signal.name,
    },
)
