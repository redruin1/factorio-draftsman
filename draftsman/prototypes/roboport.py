# roboport.py

# TODO: can roboports request items?
# 2.0: well, definitely now they can

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import (
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    EnergySourceMixin,
)
from draftsman.serialization import draftsman_converters
from draftsman.signatures import SignalID
from draftsman.validators import instance_of

from draftsman.data.entities import roboports

import attrs
from typing import Optional


@attrs.define
class Roboport(
    ControlBehaviorMixin, CircuitConnectableMixin, EnergySourceMixin, Entity
):
    """
    An entity that acts as a node in a logistics network.
    """

    @property
    def similar_entities(self) -> list[str]:
        return roboports

    # =========================================================================

    read_logistics: bool = attrs.field(default=True, validator=instance_of(bool))
    """
    Whether or not to read the item contents of the logisitics network to any
    connected circuit network.

    :exception DataFormatError: If set to anything other than a ``bool`` or 
        ``None``.
    """

    # =========================================================================

    read_robot_stats: bool = attrs.field(default=False, validator=instance_of(bool))
    """
    Whether or not to read the number of construction and logistics robots
    in the logisitics network to any connected circuit network.

    :exception DataFormatError: If set to anything other than a ``bool`` or ``None``.
    """

    # =========================================================================

    available_logistic_signal: Optional[SignalID] = attrs.field(
        factory=lambda: SignalID(name="signal-X", type="virtual"),
        converter=SignalID.converter,
        validator=instance_of(Optional[SignalID]),
        metadata={"never_null": True},
    )
    """
    What signal to output the number of available logistic robots to the
    circuit network with.

    :exception DataFormatError: If set to anything that isn't a valid 
        ``SIGNAL_ID`` or ``None``.
    """

    # =========================================================================

    total_logistic_signal: Optional[SignalID] = attrs.field(
        factory=lambda: SignalID(name="signal-Y", type="virtual"),
        converter=SignalID.converter,
        validator=instance_of(Optional[SignalID]),
        metadata={"never_null": True},
    )
    """
    What signal to output the total number of logistic robots to the
    circuit network with.

    :exception DataFormatError: If set to anything that isn't a valid 
        ``SIGNAL_ID`` or ``None``.
    """

    # =========================================================================

    available_construction_signal: Optional[SignalID] = attrs.field(
        factory=lambda: SignalID(name="signal-Z", type="virtual"),
        converter=SignalID.converter,
        validator=instance_of(Optional[SignalID]),
        metadata={"never_null": True},
    )
    """
    What signal to output the number of available construction robots to the
    circuit network with.

    :exception DataFormatError: If set to anything that isn't a valid 
        ``SIGNAL_ID`` or ``None``.
    """

    # =========================================================================

    total_construction_signal: Optional[SignalID] = attrs.field(
        factory=lambda: SignalID(name="signal-T", type="virtual"),
        converter=SignalID.converter,
        validator=instance_of(Optional[SignalID]),
        metadata={"never_null": True},
    )
    """
    What signal to output the total number of construction robots to the
    circuit network with.

    :exception DataFormatError: If set to anything that isn't a valid 
        ``SIGNAL_ID`` or ``None``.
    """

    # =========================================================================

    def merge(self, other: "Roboport"):
        super().merge(other)

        self.read_logistics = other.read_logistics
        self.read_robot_stats = other.read_robot_stats
        self.available_logistic_signal = other.available_logistic_signal
        self.total_logistic_signal = other.total_logistic_signal
        self.available_construction_signal = other.available_construction_signal
        self.total_construction_signal = other.total_construction_signal

    # =========================================================================

    __hash__ = Entity.__hash__


# TODO: versioning

draftsman_converters.add_hook_fns(  # version 1.0
    Roboport,
    lambda fields: {
        ("control_behavior", "read_logistics"): fields.read_logistics.name,
        ("control_behavior", "read_robot_stats"): fields.read_robot_stats.name,
        (
            "control_behavior",
            "available_logistic_output_signal",
        ): fields.available_logistic_signal.name,
        (
            "control_behavior",
            "total_logistic_output_signal",
        ): fields.total_logistic_signal.name,
        (
            "control_behavior",
            "available_construction_output_signal",
        ): fields.available_construction_signal.name,
        (
            "control_behavior",
            "total_construction_output_signal",
        ): fields.total_construction_signal.name,
    },
)
