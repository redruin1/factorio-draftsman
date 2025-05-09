# space_platform_hub.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import (
    RequestFiltersMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
)
from draftsman.serialization import draftsman_converters
from draftsman.signatures import AttrsSignalID
from draftsman.validators import instance_of

from draftsman.data.entities import space_platform_hubs

import attrs

from typing import Optional


@attrs.define
class SpacePlatformHub(
    RequestFiltersMixin, ControlBehaviorMixin, CircuitConnectableMixin, Entity
):
    """
    Main control center of space platforms.
    """

    @property
    def similar_entities(self) -> list[str]:
        return space_platform_hubs

    # =========================================================================

    read_contents: bool = attrs.field(default=True, validator=instance_of(bool))
    """
    Whether or not to broadcast the contents of the hub to any connected circuit
    network.
    """

    # =========================================================================

    send_to_platform: bool = attrs.field(default=True, validator=instance_of(bool))
    """
    Whether or not to send the contents of the circuit network to the platform 
    for determining it's circuit conditions.
    """

    # =========================================================================

    read_moving_from: bool = attrs.field(default=False, validator=instance_of(bool))
    """
    Whether or not to send the planet the platform is currently moving from to 
    the connected circuit network.
    """

    # =========================================================================

    read_moving_to: bool = attrs.field(default=False, validator=instance_of(bool))
    """
    Whether or not to send the planet the platform is currently moving to to the 
    connected circuit network.
    """

    # =========================================================================

    read_speed: bool = attrs.field(default=False, validator=instance_of(bool))
    """
    Whether or not to output the platforms current speed to the connected 
    circuit network.
    """

    # =========================================================================

    speed_signal: Optional[AttrsSignalID] = attrs.field(
        factory=lambda: AttrsSignalID(name="signal-V", type="virtual"),
        converter=AttrsSignalID.converter,
        validator=instance_of(Optional[AttrsSignalID]),
    )
    """
    The signal to output the speed of the platform's current speed, if 
    configured to do so.
    """

    # =========================================================================

    read_damage_taken: bool = attrs.field(default=False, validator=instance_of(bool))
    """
    Whether or not to output the total amount of damage this platform has taken
    (since it started moving) to the connected circuit network.
    """

    # =========================================================================

    damage_taken_signal: Optional[AttrsSignalID] = attrs.field(
        factory=lambda: AttrsSignalID(name="signal-D", type="virtual"),
        converter=AttrsSignalID.converter,
        validator=instance_of(Optional[AttrsSignalID]),
    )
    """
    The signal to output the total amount of damage taken, if configured to do
    so.
    """

    # =========================================================================

    request_missing_construction_materials: bool = attrs.field(
        default=True, validator=instance_of(bool)
    )
    """
    Whether or not to automatically request construction materials from 
    configured surfaces the platform is stationed above.
    """

    # =========================================================================

    __hash__ = Entity.__hash__


draftsman_converters.add_hook_fns(
    # {
    #     "$id": "factorio:space_platform_hub"
    # },
    SpacePlatformHub,
    lambda fields: {
        ("control_behavior", "read_contents"): fields.read_contents.name,
        ("control_behavior", "send_to_platform"): fields.send_to_platform.name,
        ("control_behavior", "read_moving_from"): fields.read_moving_from.name,
        ("control_behavior", "read_moving_to"): fields.read_moving_to.name,
        ("control_behavior", "read_speed"): fields.read_speed.name,
        ("control_behavior", "speed_signal"): fields.speed_signal.name,
        ("control_behavior", "read_damage_taken"): fields.read_damage_taken.name,
        ("control_behavior", "damage_taken_signal"): fields.damage_taken_signal.name,
        "request_missing_construction_materials": fields.request_missing_construction_materials.name,
    },
)
