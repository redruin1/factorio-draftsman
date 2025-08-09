# accumulator.py


from draftsman.classes.entity import Entity
from draftsman.classes.mixins import (
    EnergySourceMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
)
from draftsman.serialization import draftsman_converters
from draftsman.signatures import SignalID
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

    output_signal: Optional[SignalID] = attrs.field(
        factory=lambda: SignalID(name="signal-A", type="virtual"),
        converter=SignalID.converter,
        validator=instance_of(Optional[SignalID]),
    )
    """
    .. serialized::

        This attribute is imported/exported from blueprint strings.

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


draftsman_converters.add_hook_fns(
    Accumulator,
    lambda fields: {("control_behavior", "output_signal"): fields.output_signal.name},
)
