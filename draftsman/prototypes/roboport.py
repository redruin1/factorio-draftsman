# roboport.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import (
    RequestFiltersMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    EnergySourceMixin,
)
from draftsman.serialization import draftsman_converters
from draftsman.signatures import SignalID
from draftsman.validators import instance_of, try_convert

from draftsman.data.entities import roboports

from enum import IntEnum
import attrs
from typing import Optional


@attrs.define
class Roboport(
    RequestFiltersMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    EnergySourceMixin,
    Entity,
):
    """
    An entity that acts as a node in a logistics network.
    """

    class ReadItemsMode(IntEnum):
        """
        Different manners in which a roboport can read items from it's network
        when connected via circuit wire.

        * ``NONE (0)``
            Do nothing when connected.
        * ``LOGISTICS (1)``
            Read the current inventory of the entire logistics network within
            the scope of this roboport. (Default)
        * ``MISSING_REQUESTS (2)``
            Broadcast the current items being requested but not satisfied across
            the entire logistics network within the scope of this roboport.
        """

        NONE = 0
        LOGISTICS = 1
        MISSING_REQUESTS = 2

    @property
    def similar_entities(self) -> list[str]:
        return roboports

    # =========================================================================

    read_items_mode: ReadItemsMode = attrs.field(
        default=ReadItemsMode.LOGISTICS,
        converter=try_convert(ReadItemsMode),
        validator=instance_of(ReadItemsMode),
    )
    """
    In what manner should this roboport read it's own contents.

    .. NOTE::

        In Factorio 1.0, only modes ``NONE`` and ``LOGISTICS`` are permitted.
        Attempting to export with mode ``MISSING_REQUESTS`` gets converted to
        mode ``NONE``.
    
    :exception DataFormatError: If set to anything other than the correct enum
        or equivalent int.
    """

    # =========================================================================

    read_robot_stats: bool = attrs.field(default=False, validator=instance_of(bool))
    """
    Whether or not to read the number of construction and logistics robots
    in the logisitics network to any connected circuit network.

    :exception DataFormatError: If set to anything other than a ``bool`` or 
        ``None``.
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

    roboport_count_signal: Optional[SignalID] = attrs.field(
        factory=lambda: SignalID(name="signal-R", type="virtual"),
        converter=SignalID.converter,
        validator=instance_of(Optional[SignalID]),
        metadata={"never_null": True},
    )
    """
    What signal to output the total number of roboports in the current network
    with.

    :exception DataFormatError: If set to anything that isn't a valid 
        ``SIGNAL_ID`` or ``None``.
    """

    # =========================================================================

    def merge(self, other: "Roboport"):
        super().merge(other)

        self.read_items_mode = other.read_items_mode
        self.read_robot_stats = other.read_robot_stats
        self.available_logistic_signal = other.available_logistic_signal
        self.total_logistic_signal = other.total_logistic_signal
        self.available_construction_signal = other.available_construction_signal
        self.total_construction_signal = other.total_construction_signal
        self.roboport_count_signal = other.roboport_count_signal

    # =========================================================================

    __hash__ = Entity.__hash__


@attrs.define
class _ExportFields:
    read_logistics: bool = False


_export_fields = attrs.fields(_ExportFields)


draftsman_converters.get_version((1, 0)).add_hook_fns(  # version 1.0
    Roboport,
    lambda fields: {
        ("control_behavior", "read_logistics"): (
            _export_fields.read_logistics,
            lambda v, _: Roboport.ReadItemsMode.LOGISTICS
            if v
            else Roboport.ReadItemsMode.NONE,
        ),
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
    lambda fields, converter: {
        ("control_behavior", "read_logistics"): (
            _export_fields.read_logistics,
            lambda inst: True
            if inst.read_items_mode is Roboport.ReadItemsMode.LOGISTICS
            else False,
        ),
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

draftsman_converters.get_version((2, 0)).add_hook_fns(
    Roboport,
    lambda fields: {
        # "request_filters": fields.request_filters.name,
        ("control_behavior", "read_items_mode"): fields.read_items_mode.name,
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
        (
            "control_behavior",
            "roboport_count_output_signal",
        ): fields.roboport_count_signal.name,
    },
)
