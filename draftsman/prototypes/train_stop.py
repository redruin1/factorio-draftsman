# train_stop.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import (
    ColorMixin,
    CircuitConditionMixin,
    CircuitEnableMixin,
    LogisticConditionMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    DirectionalMixin,
)
from draftsman.serialization import draftsman_converters
from draftsman.signatures import Color, SignalID, LuaDouble, uint32
from draftsman.utils import fix_incorrect_pre_init, attrs_reuse
from draftsman.validators import instance_of

from draftsman.data.entities import train_stops

import attrs
from typing import Optional


@fix_incorrect_pre_init
@attrs.define
class TrainStop(
    ColorMixin,
    LogisticConditionMixin,
    CircuitConditionMixin,
    CircuitEnableMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    DirectionalMixin,
    Entity,
):
    """
    A stop for making train schedules for locomotives.
    """

    @property
    def similar_entities(self) -> list[str]:
        return train_stops

    # =========================================================================

    @property
    def double_grid_aligned(self) -> bool:
        return True

    # =========================================================================

    color = attrs_reuse(
        attrs.fields(ColorMixin).color,
        factory=lambda: Color(r=242 / 255, g=0, b=0, a=127 / 255),
    )

    # =========================================================================

    station: str = attrs.field(
        default="",
        converter=lambda v: "" if v is None else v,
        validator=instance_of(str),
    )
    """
    The name of this station.
    """

    # =========================================================================

    manual_trains_limit: Optional[uint32] = attrs.field(
        default=None,
        validator=instance_of(Optional[uint32]),
        metadata={"never_null": True},
    )
    """
    A limit to the amount of trains that can use this stop. If set to ``None``, 
    this stop has no limit on the number of trains that can path to it. 
    Overridden by the circuit signal set train limit (if present).
    """

    # =========================================================================

    priority: LuaDouble = attrs.field(default=50, validator=instance_of(LuaDouble))
    """
    The static priority that schedules should use to bias trains to or away from 
    this train stop. Overridden by :py:attr:`.`
    """

    # =========================================================================

    send_to_train: bool = attrs.field(default=True, validator=instance_of(bool))
    """
    Whether or not to send the contents of any connected circuit network to
    the train to determine it's schedule.
    """

    # =========================================================================

    read_from_train: bool = attrs.field(default=False, validator=instance_of(bool))
    """
    Whether or not to broadcast the train's contents to connected circuit 
    networks when stopped at this train stop.
    """

    # =========================================================================

    read_stopped_train: bool = attrs.field(default=False, validator=instance_of(bool))
    """
    Whether or not to read a unique number associated with the train
    currently stopped at the station.
    """

    # =========================================================================

    train_stopped_signal: Optional[SignalID] = attrs.field(
        factory=lambda: SignalID(name="signal-T", type="virtual"),
        converter=SignalID.converter,
        validator=instance_of(Optional[SignalID]),
        metadata={"never_null": True},
    )
    """
    What signal to output the unique train ID if a train is currently
    stopped at a station.
    """

    # =========================================================================

    signal_limits_trains: bool = attrs.field(default=False, validator=instance_of(bool))
    """
    Whether or not an external signal should limit the number of trains that
    can use this stop.
    """

    # =========================================================================

    trains_limit_signal: Optional[SignalID] = attrs.field(
        factory=lambda: SignalID(name="signal-L", type="virtual"),
        converter=SignalID.converter,
        validator=instance_of(Optional[SignalID]),
        metadata={"never_null": True},
    )
    """
    What signal to read to limit the number of trains that can use this stop.
    """

    # =========================================================================

    read_trains_count: bool = attrs.field(default=False, validator=instance_of(bool))
    """
    Whether or not to read the number of trains that currently use this stop and
    broadcast it to any connected circuit network.
    """

    # =========================================================================

    trains_count_signal: Optional[SignalID] = attrs.field(
        factory=lambda: SignalID(name="signal-C", type="virtual"),
        converter=SignalID.converter,
        validator=instance_of(Optional[SignalID]),
        metadata={"never_null": True},
    )
    """
    What signal to use to output the current number of trains that use this
    stop.
    """

    # =========================================================================

    set_priority: bool = attrs.field(default=False, validator=instance_of(bool))
    """
    Whether or not the priority of this train stop should be set via the circuit
    network. The signal used is determined by :py:attr:`.priority_signal`.
    """

    # =========================================================================

    priority_signal: Optional[SignalID] = attrs.field(
        factory=lambda: SignalID(name="signal-P", type="virtual"),
        converter=SignalID.converter,
        validator=instance_of(Optional[SignalID]),
        metadata={"never_null": True},
    )
    """
    Which signal to read the dynamic priority of this train stop from.
    """

    # =========================================================================

    def merge(self, other: "TrainStop"):
        super(TrainStop, self).merge(other)

        self.station = other.station
        self.manual_trains_limit = other.manual_trains_limit
        self.priority = other.priority
        self.send_to_train = other.send_to_train
        self.read_from_train = other.read_from_train
        self.read_stopped_train = other.read_stopped_train
        self.train_stopped_signal = other.train_stopped_signal
        self.signal_limits_trains = other.signal_limits_trains
        self.trains_limit_signal = other.trains_limit_signal
        self.read_trains_count = other.read_trains_count
        self.trains_count_signal = other.trains_count_signal
        self.set_priority = other.set_priority
        self.priority_signal = other.priority_signal

    # =========================================================================

    __hash__ = Entity.__hash__


draftsman_converters.get_version((1, 0)).add_hook_fns(
    TrainStop,
    lambda fields: {
        "station": fields.station.name,
        "manual_trains_limit": fields.manual_trains_limit.name,
        ("control_behavior", "send_to_train"): fields.send_to_train.name,
        ("control_behavior", "read_from_train"): fields.read_from_train.name,
        ("control_behavior", "read_stopped_train"): fields.read_stopped_train.name,
        ("control_behavior", "train_stopped_signal"): fields.train_stopped_signal.name,
        ("control_behavior", "set_trains_limit"): fields.signal_limits_trains.name,
        ("control_behavior", "trains_limit_signal"): fields.trains_limit_signal.name,
        ("control_behavior", "read_trains_count"): fields.read_trains_count.name,
        ("control_behavior", "trains_count_signal"): fields.trains_count_signal.name,
    },
)

draftsman_converters.get_version((2, 0)).add_hook_fns(
    TrainStop,
    lambda fields: {
        "station": fields.station.name,
        "manual_trains_limit": fields.manual_trains_limit.name,
        "priority": fields.priority.name,
        ("control_behavior", "send_to_train"): fields.send_to_train.name,
        ("control_behavior", "read_from_train"): fields.read_from_train.name,
        ("control_behavior", "read_stopped_train"): fields.read_stopped_train.name,
        ("control_behavior", "train_stopped_signal"): fields.train_stopped_signal.name,
        ("control_behavior", "set_trains_limit"): fields.signal_limits_trains.name,
        ("control_behavior", "trains_limit_signal"): fields.trains_limit_signal.name,
        ("control_behavior", "read_trains_count"): fields.read_trains_count.name,
        ("control_behavior", "trains_count_signal"): fields.trains_count_signal.name,
        ("control_behavior", "set_priority"): fields.set_priority.name,
        ("control_behavior", "priority_signal"): fields.priority_signal.name,
    },
)
