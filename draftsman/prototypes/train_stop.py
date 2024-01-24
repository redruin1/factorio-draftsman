# train_stop.py

from draftsman.classes.entity import Entity
from draftsman.classes.exportable import attempt_and_reissue
from draftsman.classes.mixins import (
    ColorMixin,
    CircuitConditionMixin,
    EnableDisableMixin,
    LogisticConditionMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    DoubleGridAlignedMixin,
    DirectionalMixin,
)
from draftsman.classes.vector import Vector, PrimitiveVector
from draftsman.constants import Direction, ValidationMode
from draftsman.signatures import Connections, DraftsmanBaseModel, SignalID, uint32
from draftsman.utils import get_first

from draftsman.data.entities import train_stops
from draftsman.data.signals import signal_dict

from pydantic import (
    ConfigDict,
    Field,
    ValidationInfo,
    ValidatorFunctionWrapHandler,
    field_validator,
)
from typing import Any, Literal, Optional, Union


class TrainStop(
    ColorMixin,
    CircuitConditionMixin,
    LogisticConditionMixin,
    EnableDisableMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    DoubleGridAlignedMixin,
    DirectionalMixin,
    Entity,
):
    """
    A stop for making train schedules for locomotives.
    """

    class Format(
        ColorMixin.Format,
        CircuitConditionMixin.Format,
        LogisticConditionMixin.Format,
        EnableDisableMixin.Format,
        ControlBehaviorMixin.Format,
        CircuitConnectableMixin.Format,
        DoubleGridAlignedMixin.Format,
        DirectionalMixin.Format,
        Entity.Format,
    ):
        class ControlBehavior(
            CircuitConditionMixin.ControlFormat,
            LogisticConditionMixin.ControlFormat,
            EnableDisableMixin.ControlFormat,
            DraftsmanBaseModel,
        ):
            send_to_train: Optional[bool] = Field(
                True,
                description="""
                Whether or not to send any connected circuit network's signals
                to the stopped train.
                """,
            )
            set_trains_limit: Optional[bool] = Field(
                False,
                description="""
                Whether or not to limit the amount of trains that can use this
                stop dynamically via a circuit signal.
                """,
            )
            trains_limit_signal: Optional[SignalID] = Field(
                SignalID(name="signal-L", type="virtual"),
                description="""
                The input signal to read to limit the number of trains that can 
                use this stop at any one time. Overrides 'manual_trains_limit' 
                if 'set_trains_limit' is true.
                """,
            )
            read_from_train: Optional[bool] = Field(
                False,
                description="""
                Whether or not to read the contents of the stopped train and 
                broadcast it to the circuit network.
                """,
            )
            read_stopped_train: Optional[bool] = Field(
                False,
                description="""
                Whether or not to read the unique ID of the stopped train and 
                broadcast it to the circuit network.
                """,
            )
            train_stopped_signal: Optional[SignalID] = Field(
                SignalID(name="signal-T", type="virtual"),
                description="""
                The output signal which holds the unique ID of the stopped train,
                if 'read_stopped_train' is true.
                """,
            )
            read_trains_count: Optional[bool] = Field(
                False,
                description="""
                Whether or not to read the trains heading to this train stop,
                including the train that is currently stopped (if any are).
                """,
            )
            trains_count_signal: Optional[SignalID] = Field(
                SignalID(name="signal-C", type="virtual"),
                description="""
                The output signal which emits the current number of trains 
                heading to this stop, if 'read_trains_count' is true.
                """,
            )

        control_behavior: ControlBehavior | None = ControlBehavior()

        station: Optional[str] = Field(
            None,
            description="""
            The name of this particular train stop.
            """,
        )
        manual_trains_limit: Optional[uint32] = Field(  # TODO: dimension
            None,
            description="""
            The maximum amount of trains that can be scheduled to this stop, 
            unless overridden by the circuit network if enabled.
            """,
        )

        model_config = ConfigDict(title="TrainStop")

    def __init__(
        self,
        name: Optional[str] = get_first(train_stops),
        position: Union[Vector, PrimitiveVector] = None,
        tile_position: Union[Vector, PrimitiveVector] = (0, 0),
        direction: Direction = Direction.NORTH,
        connections: Connections = {},
        control_behavior: Format.ControlBehavior = {},
        tags: dict[str, Any] = {},
        validate: Union[
            ValidationMode, Literal["none", "minimum", "strict", "pedantic"]
        ] = ValidationMode.STRICT,
        validate_assignment: Union[
            ValidationMode, Literal["none", "minimum", "strict", "pedantic"]
        ] = ValidationMode.STRICT,
        **kwargs
    ):
        """
        TODO
        """

        self._root: __class__.Format
        self.control_behavior: __class__.Format.ControlBehavior

        super(TrainStop, self).__init__(
            name,
            train_stops,
            position=position,
            tile_position=tile_position,
            direction=direction,
            connections=connections,
            control_behavior=control_behavior,
            tags=tags,
            **kwargs
        )

        self.station = kwargs.get("station", None)
        self.manual_trains_limit = kwargs.get("manual_trains_limit", None)

        self.validate_assignment = validate_assignment

        self.validate(mode=validate).reissue_all(stacklevel=3)

    # =========================================================================

    @property
    def double_grid_aligned(self) -> bool:
        return True

    # =========================================================================

    @property
    def station(self) -> Optional[str]:
        """
        The name of this station.
        TODO more
        """
        return self._root.station

    @station.setter
    def station(self, value: Optional[str]):
        if self.validate_assignment:
            result = attempt_and_reissue(
                self, type(self).Format, self._root, "station", value
            )
            self._root.station = result
        else:
            self._root.station = value

    # =========================================================================

    @property
    def manual_trains_limit(self) -> Optional[uint32]:
        """
        A limit to the amount of trains that can use this stop. Overridden by
        the circuit signal set train limit (if present).
        """
        return self._root.manual_trains_limit

    @manual_trains_limit.setter
    def manual_trains_limit(self, value: Optional[uint32]):
        if self.validate_assignment:
            result = attempt_and_reissue(
                self, type(self).Format, self._root, "manual_trains_limit", value
            )
            self._root.manual_trains_limit = result
        else:
            self._root.manual_trains_limit = value

    # =========================================================================

    @property
    def send_to_train(self) -> Optional[bool]:
        """
        Whether or not to send the contents of any connected circuit network to
        the train to determine it's schedule.
        """
        return self.control_behavior.send_to_train

    @send_to_train.setter
    def send_to_train(self, value: Optional[bool]):
        if self.validate_assignment:
            result = attempt_and_reissue(
                self,
                type(self).Format.ControlBehavior,
                self.control_behavior,
                "send_to_train",
                value,
            )
            self.control_behavior.send_to_train = result
        else:
            self.control_behavior.send_to_train = value

    # =========================================================================

    @property
    def read_from_train(self) -> Optional[bool]:
        """
        Whether or not to read the train's contents when stopped at this train
        stop.
        """
        return self.control_behavior.read_from_train

    @read_from_train.setter
    def read_from_train(self, value: Optional[bool]):
        if self.validate_assignment:
            result = attempt_and_reissue(
                self,
                type(self).Format.ControlBehavior,
                self.control_behavior,
                "read_from_train",
                value,
            )
            self.control_behavior.read_from_train = result
        else:
            self.control_behavior.read_from_train = value

    # =========================================================================

    @property
    def read_stopped_train(self) -> Optional[bool]:
        """
        Whether or not to read a unique number associated with the train
        currently stopped at the station.
        """
        return self.control_behavior.read_stopped_train

    @read_stopped_train.setter
    def read_stopped_train(self, value: Optional[bool]):
        if self.validate_assignment:
            result = attempt_and_reissue(
                self,
                type(self).Format.ControlBehavior,
                self.control_behavior,
                "read_stopped_train",
                value,
            )
            self.control_behavior.read_stopped_train = result
        else:
            self.control_behavior.read_stopped_train = value

    # =========================================================================

    @property
    def train_stopped_signal(self) -> Optional[SignalID]:
        """
        What signal to output the unique train ID if a train is currently
        stopped at a station.
        """
        return self.control_behavior.train_stopped_signal

    @train_stopped_signal.setter
    def train_stopped_signal(self, value: Union[str, SignalID, None]):
        if self.validate_assignment:
            result = attempt_and_reissue(
                self,
                type(self).Format.ControlBehavior,
                self.control_behavior,
                "train_stopped_signal",
                value,
            )
            self.control_behavior.train_stopped_signal = result
        else:
            self.control_behavior.train_stopped_signal = value

    # =========================================================================

    @property
    def signal_limits_trains(self) -> Optional[bool]:
        """
        Whether or not an external signal should limit the number of trains that
        can use this stop.
        """
        return self.control_behavior.set_trains_limit

    @signal_limits_trains.setter
    def signal_limits_trains(self, value: Optional[bool]):
        if self.validate_assignment:
            result = attempt_and_reissue(
                self,
                type(self).Format.ControlBehavior,
                self.control_behavior,
                "set_trains_limit",
                value,
            )
            self.control_behavior.set_trains_limit = result
        else:
            self.control_behavior.set_trains_limit = value

    # =========================================================================

    @property
    def trains_limit_signal(self) -> Optional[SignalID]:
        """
        What signal to read to limit the number of trains that can use this stop.
        """
        return self.control_behavior.trains_limit_signal

    @trains_limit_signal.setter
    def trains_limit_signal(self, value: Union[str, SignalID, None]):
        if self.validate_assignment:
            result = attempt_and_reissue(
                self,
                type(self).Format.ControlBehavior,
                self.control_behavior,
                "trains_limit_signal",
                value,
            )
            self.control_behavior.trains_limit_signal = result
        else:
            self.control_behavior.trains_limit_signal = value

    # =========================================================================

    @property
    def read_trains_count(self) -> Optional[bool]:
        """
        Whether or not to read the number of trains that currently use this stop.
        """
        return self.control_behavior.read_trains_count

    @read_trains_count.setter
    def read_trains_count(self, value: Optional[bool]):
        if self.validate_assignment:
            result = attempt_and_reissue(
                self,
                type(self).Format.ControlBehavior,
                self.control_behavior,
                "read_trains_count",
                value,
            )
            self.control_behavior.read_trains_count = result
        else:
            self.control_behavior.read_trains_count = value

    # =========================================================================

    @property
    def trains_count_signal(self) -> Optional[SignalID]:
        """
        What signal to use to output the current number of trains that use this
        stop.
        """
        return self.control_behavior.trains_count_signal

    @trains_count_signal.setter
    def trains_count_signal(self, value: Union[str, SignalID, None]):
        if self.validate_assignment:
            result = attempt_and_reissue(
                self,
                type(self).Format.ControlBehavior,
                self.control_behavior,
                "trains_count_signal",
                value,
            )
            self.control_behavior.trains_count_signal = result
        else:
            self.control_behavior.trains_count_signal = value

    # =========================================================================

    def merge(self, other: "TrainStop"):
        super(TrainStop, self).merge(other)

        self.station = other.station
        self.manual_trains_limit = other.manual_trains_limit

    # =========================================================================

    __hash__ = Entity.__hash__

    def __eq__(self, other: "TrainStop") -> bool:
        return (
            super().__eq__(other)
            and self.station == other.station
            and self.manual_trains_limit == other.manual_trains_limit
        )
