# train_stop.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import (
    ColorMixin,
    CircuitConditionMixin,
    CircuitEnableMixin,
    LogisticConditionMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    DoubleGridAlignedMixin,
    DirectionalMixin,
)
from draftsman.serialization import draftsman_converters
from draftsman.signatures import Color, SignalID, uint32
from draftsman.utils import fix_incorrect_pre_init
from draftsman.validators import instance_of

from draftsman.data.entities import train_stops

import attrs
from typing import Optional


# TODO: priority


@fix_incorrect_pre_init
@attrs.define
class TrainStop(
    ColorMixin,
    LogisticConditionMixin,
    CircuitConditionMixin,
    CircuitEnableMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    DoubleGridAlignedMixin,
    DirectionalMixin,
    Entity,
):
    """
    A stop for making train schedules for locomotives.
    """

    # class Format(
    #     ColorMixin.Format,
    #     CircuitConditionMixin.Format,
    #     LogisticConditionMixin.Format,
    #     CircuitEnableMixin.Format,
    #     ControlBehaviorMixin.Format,
    #     CircuitConnectableMixin.Format,
    #     DoubleGridAlignedMixin.Format,
    #     DirectionalMixin.Format,
    #     Entity.Format,
    # ):
    #     class ControlBehavior(
    #         CircuitConditionMixin.ControlFormat,
    #         LogisticConditionMixin.ControlFormat,
    #         CircuitEnableMixin.ControlFormat,
    #         DraftsmanBaseModel,
    #     ):
    #         send_to_train: Optional[bool] = Field(
    #             True,
    #             description="""
    #             Whether or not to send any connected circuit network's signals
    #             to the stopped train.
    #             """,
    #         )
    #         set_trains_limit: Optional[bool] = Field(
    #             False,
    #             description="""
    #             Whether or not to limit the amount of trains that can use this
    #             stop dynamically via a circuit signal.
    #             """,
    #         )
    #         trains_limit_signal: Optional[SignalID] = Field(
    #             SignalID(name="signal-L", type="virtual"),
    #             description="""
    #             The input signal to read to limit the number of trains that can
    #             use this stop at any one time. Overrides 'manual_trains_limit'
    #             if 'set_trains_limit' is true.
    #             """,
    #         )
    #         read_from_train: Optional[bool] = Field(
    #             False,
    #             description="""
    #             Whether or not to read the contents of the stopped train and
    #             broadcast it to the circuit network.
    #             """,
    #         )
    #         read_stopped_train: Optional[bool] = Field(
    #             False,
    #             description="""
    #             Whether or not to read the unique ID of the stopped train and
    #             broadcast it to the circuit network.
    #             """,
    #         )
    #         train_stopped_signal: Optional[SignalID] = Field(
    #             SignalID(name="signal-T", type="virtual"),
    #             description="""
    #             The output signal which holds the unique ID of the stopped train,
    #             if 'read_stopped_train' is true.
    #             """,
    #         )
    #         read_trains_count: Optional[bool] = Field(
    #             False,
    #             description="""
    #             Whether or not to read the trains heading to this train stop,
    #             including the train that is currently stopped (if any are).
    #             """,
    #         )
    #         trains_count_signal: Optional[SignalID] = Field(
    #             SignalID(name="signal-C", type="virtual"),
    #             description="""
    #             The output signal which emits the current number of trains
    #             heading to this stop, if 'read_trains_count' is true.
    #             """,
    #         )

    #     control_behavior: ControlBehavior | None = ControlBehavior()

    #     station: Optional[str] = Field(
    #         None,
    #         description="""
    #         The name of this particular train stop.
    #         """,
    #     )
    #     manual_trains_limit: Optional[uint32] = Field(  # TODO: dimension
    #         None,
    #         description="""
    #         The maximum amount of trains that can be scheduled to this stop,
    #         unless overridden by the circuit network if enabled.
    #         """,
    #     )

    #     model_config = ConfigDict(title="TrainStop")

    # def __init__(
    #     self,
    #     name: Optional[str] = get_first(train_stops),
    #     position: Union[Vector, PrimitiveVector] = None,
    #     tile_position: Union[Vector, PrimitiveVector] = (0, 0),
    #     direction: Direction = Direction.NORTH,
    #     control_behavior: Format.ControlBehavior = {},
    #     tags: dict[str, Any] = {},
    #     validate_assignment: Union[
    #         ValidationMode, Literal["none", "minimum", "strict", "pedantic"]
    #     ] = ValidationMode.STRICT,
    #     **kwargs
    # ):
    #     """
    #     TODO
    #     """

    #     self._root: __class__.Format
    #     self.control_behavior: __class__.Format.ControlBehavior

    #     super(TrainStop, self).__init__(
    #         name,
    #         train_stops,
    #         position=position,
    #         tile_position=tile_position,
    #         direction=direction,
    #         control_behavior=control_behavior,
    #         tags=tags,
    #         **kwargs
    #     )

    #     self.station = kwargs.get("station", None)
    #     self.manual_trains_limit = kwargs.get("manual_trains_limit", None)

    #     self.validate_assignment = validate_assignment

    # =========================================================================

    @property
    def similar_entities(self) -> list[str]:
        return train_stops

    # =========================================================================

    @property
    def double_grid_aligned(self) -> bool:
        return True

    # =========================================================================

    # TODO: should be evolved
    color: Optional[Color] = attrs.field(
        default=Color(r=242 / 255, g=0, b=0, a=127 / 255),
        converter=Color.converter,
        validator=instance_of(Optional[Color]),
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
    Whether or not to read the number of trains that currently use this stop.
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

    def merge(self, other: "TrainStop"):
        super(TrainStop, self).merge(other)

        self.station = other.station
        self.manual_trains_limit = other.manual_trains_limit
        self.send_to_train = other.send_to_train
        self.read_from_train = other.read_from_train
        self.read_stopped_train = other.read_stopped_train
        self.train_stopped_signal = other.train_stopped_signal
        self.signal_limits_trains = other.signal_limits_trains
        self.trains_limit_signal = other.trains_limit_signal
        self.read_trains_count = other.read_trains_count
        self.trains_count_signal = other.trains_count_signal

    # =========================================================================

    __hash__ = Entity.__hash__


draftsman_converters.add_hook_fns(
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
