# accumulator.py


from draftsman.classes.entity import Entity
from draftsman.classes.mixins import (
    EnergySourceMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
)
from draftsman.serialization import draftsman_converters
from draftsman.signatures import AttrsSignalID
from draftsman.validators import instance_of

from draftsman.data.entities import accumulators

import attrs
from typing import Optional


@attrs.define
class Accumulator(
    ControlBehaviorMixin, CircuitConnectableMixin, EnergySourceMixin, Entity
):
    """
    An entity that stores electricity for periods of high demand.
    """

    @property
    def similar_entities(self) -> list:
        return accumulators

    # =========================================================================

    output_signal: Optional[AttrsSignalID] = attrs.field(
        factory=lambda: AttrsSignalID(name="signal-A", type="virtual"),
        converter=AttrsSignalID.converter,
        validator=instance_of(Optional[AttrsSignalID]),
    )
    """
    The signal used to output this accumulator's charge level, if connected to
    a circuit network.

    :exception InvalidSignalError: If set to a string not recognized as a valid
        signal name.
    :exception DataFormatError: If set to a ``dict`` that does not comply
        with the :py:data:`.SIGNAL_ID` format.
    """

    # =========================================================================

    def merge(self, other: "Accumulator"):
        super().merge(other)

        self.output_signal = other.output_signal

    # =========================================================================

    __hash__ = Entity.__hash__


Accumulator.add_schema(
    {
        "$id": "urn:factorio:entity:accumulator",  # TODO: versionize IDs
        "type": "object",
        "properties": {
            "control_behavior": {
                "type": "object",
                "properties": {
                    "output_signal": {
                        "anyOf": [{"$ref": "urn:factorio:signal-id"}, {"type": "null"}]
                    }
                },
            }
        },
    }
)

draftsman_converters.add_hook_fns(
    Accumulator,
    lambda fields: {("control_behavior", "output_signal"): fields.output_signal.name},
)
