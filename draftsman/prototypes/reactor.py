# reactor.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import (
    ItemRequestMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    EnergySourceMixin,
)
from draftsman.serialization import draftsman_converters
from draftsman.signatures import AttrsSignalID
from draftsman.validators import instance_of

from draftsman.data.entities import reactors

import attrs
from pydantic import ConfigDict, Field
from typing import Any, Literal, Optional, Union


@attrs.define
class Reactor(
    ItemRequestMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    EnergySourceMixin,
    Entity,
):
    """
    An entity that converts a fuel into thermal energy.
    """

    @property
    def similar_entities(self) -> list[str]:
        return reactors

    # =========================================================================

    read_burner_fuel: bool = attrs.field(default=False, validator=instance_of(bool))
    """
    Whether or not to broadcast the amount of fuel currently in the reactor to 
    any connected circuit networks.
    """

    # =========================================================================

    read_temperature: bool = attrs.field(
        default=False,
        validator=instance_of(bool),
    )
    """
    Whether or not to brodcast the current temperature in Celsius of the reactor 
    to any connected circuit networks.
    """

    # =========================================================================

    temperature_signal: Optional[AttrsSignalID] = attrs.field(
        factory=lambda: AttrsSignalID(name="signal-T", type="virtual"),
        converter=AttrsSignalID.converter,
        validator=instance_of(Optional[AttrsSignalID]),
    )
    """
    The signal with which to broadcast the reactors temperature to, if this 
    entity is configured to do so.
    """

    # =========================================================================

    __hash__ = Entity.__hash__

# TODO: might need to add hooks for 1.0 with a custom MRO

draftsman_converters.get_version((2, 0)).add_hook_fns(
    Reactor,
    lambda fields: {
        ("control_behavior", "read_burner_fuel"): fields.read_burner_fuel.name,
        ("control_behavior", "read_temperature"): fields.read_temperature.name,
        ("control_behavior", "temperature_signal"): fields.temperature_signal.name,
    },
)
