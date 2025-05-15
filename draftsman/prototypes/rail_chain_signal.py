# rail_chain_signal.py

from draftsman.classes.collision_set import CollisionSet
from draftsman.classes.entity import Entity
from draftsman.classes.mixins import (
    ReadRailSignalMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    # EightWayDirectionalMixin,
    DirectionalMixin,
)
from draftsman.constants import Direction, SIXTEEN_WAY_DIRECTIONS
from draftsman.serialization import draftsman_converters
from draftsman.signatures import AttrsSignalID
from draftsman.utils import fix_incorrect_pre_init
from draftsman.validators import instance_of

from draftsman.data.entities import rail_chain_signals

import attrs
from typing import Optional


@fix_incorrect_pre_init
@attrs.define
class RailChainSignal(
    ReadRailSignalMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    DirectionalMixin,
    Entity,
):
    """
    A rail signal that determines access of a current rail block based on a
    forward rail block.
    """

    @property
    def similar_entities(self) -> list[str]:
        return rail_chain_signals

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

    blue_output_signal: Optional[AttrsSignalID] = attrs.field(
        factory=lambda: AttrsSignalID(name="signal-blue", type="virtual"),
        converter=AttrsSignalID.converter,
        validator=instance_of(Optional[AttrsSignalID]),
        metadata={"never_null": True},
    )
    """
    The blue output signal. Sent with a unit value when the rail signal's state 
    is blue.
    """

    # =========================================================================

    def merge(self, other: "RailChainSignal"):
        super().merge(other)

        self.blue_output_signal = other.blue_output_signal

    # =========================================================================

    __hash__ = Entity.__hash__


RailChainSignal.add_schema(
    {
        "$id": "urn:factorio:entity:rail-chain-signal",
        "properties": {
            "control_behavior": {
                "type": "object",
                "properties": {
                    "blue_output_signal": {
                        "$ref": "urn:factorio:signal-id",
                        "default": {"name": "signal-blue", "type": "virtual"},
                    }
                },
            }
        },
    }
)


draftsman_converters.add_hook_fns(
    RailChainSignal,
    lambda fields: {
        ("control_behavior", "blue_output_signal"): fields.blue_output_signal.name
    },
)
