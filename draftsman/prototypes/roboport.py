# roboport.py

# TODO: can roboports request items?

from draftsman.classes.entity import Entity
from draftsman.classes.exportable import attempt_and_reissue
from draftsman.classes.mixins import ControlBehaviorMixin, CircuitConnectableMixin
from draftsman.classes.vector import Vector, PrimitiveVector
from draftsman.constants import ValidationMode
from draftsman.signatures import Connections, DraftsmanBaseModel, SignalID
from draftsman.utils import get_first

from draftsman.data.entities import roboports

from pydantic import ConfigDict, Field
from typing import Any, Literal, Optional, Union


class Roboport(ControlBehaviorMixin, CircuitConnectableMixin, Entity):
    """
    An entity that acts as a node in a logistics network.
    """

    class Format(
        ControlBehaviorMixin.Format, CircuitConnectableMixin.Format, Entity.Format
    ):
        class ControlBehavior(DraftsmanBaseModel):
            read_logistics: Optional[bool] = Field(
                True,
                description="""
                Whether this roboport will broadcast the contents of the 
                logistic network it is part of to any connected circuit network.
                """,
            )
            read_robot_stats: Optional[bool] = Field(
                False,
                description="""
                Whether this roboport will broadcast the number of robots in the 
                logistic network it is part of to any connected circuit network.
                """,
            )
            available_logistic_output_signal: Optional[SignalID] = Field(
                SignalID(name="signal-X", type="virtual"),
                description="""
                The signal to broadcast the number of available logistic robots 
                on.
                """,
            )
            total_logistic_output_signal: Optional[SignalID] = Field(
                SignalID(name="signal-Y", type="virtual"),
                description="""
                The signal to broadcast the total number of logistic robots on.
                """,
            )
            available_construction_output_signal: Optional[SignalID] = Field(
                SignalID(name="signal-Z", type="virtual"),
                description="""
                The signal to broadcast the number of available construction 
                robots on.
                """,
            )
            total_construction_output_signal: Optional[SignalID] = Field(
                SignalID(name="signal-T", type="virtual"),
                description="""
                The signal to broadcast the total number of construction robots
                on.
                """,
            )

        control_behavior: Optional[ControlBehavior] = ControlBehavior()

        model_config = ConfigDict(title="Roboport")

    def __init__(
        self,
        name: Optional[str] = get_first(roboports),
        position: Union[Vector, PrimitiveVector] = None,
        tile_position: Union[Vector, PrimitiveVector] = (0, 0),
        connections: Connections = {},
        control_behavior: Format.ControlBehavior() = {},
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

        self.control_behavior: __class__.Format.ControlBehavior

        super().__init__(
            name,
            roboports,
            position=position,
            tile_position=tile_position,
            connections=connections,
            control_behavior=control_behavior,
            tags=tags,
            **kwargs
        )

        self.validate_assignment = validate_assignment

        self.validate(mode=validate).reissue_all(stacklevel=3)

    # =========================================================================

    @property
    def read_logistics(self) -> Optional[bool]:
        """
        Whether or not to read the item contents of the logisitics network.

        :getter: Gets whether or not the logistics are read, or ``None`` if not
            set.
        :setter: Sets whether or not the logistics are read. Removes the key if
            set to ``None``.
        :type: bool

        :exception TypeError: If set to anything other than a ``bool`` or ``None``.
        """
        return self.control_behavior.read_logistics

    @read_logistics.setter
    def read_logistics(self, value: Optional[bool]):
        if self.validate_assignment:
            result = attempt_and_reissue(
                self,
                type(self).Format.ControlBehavior,
                self.control_behavior,
                "read_logistics",
                value,
            )
            self.control_behavior.read_logistics = result
        else:
            self.control_behavior.read_logistics = value

    # =========================================================================

    @property
    def read_robot_stats(self) -> Optional[bool]:
        """
        Whether or not to read the number of construction and logistics robots
        in the logisitics network.

        :getter: Gets whether or not the robot counts are read, or ``None`` if
            not set.
        :setter: Sets whether or not the robot counts are read. Removes the key
            if set to ``None``.
        :type: bool

        :exception TypeError: If set to anything other than a ``bool`` or ``None``.
        """
        return self.control_behavior.read_robot_stats

    @read_robot_stats.setter
    def read_robot_stats(self, value: Optional[bool]):
        if self.validate_assignment:
            result = attempt_and_reissue(
                self,
                type(self).Format.ControlBehavior,
                self.control_behavior,
                "read_robot_stats",
                value,
            )
            self.control_behavior.read_robot_stats = result
        else:
            self.control_behavior.read_robot_stats = value

    # =========================================================================

    @property
    def available_logistic_signal(self) -> Optional[SignalID]:
        """
        What signal to output the number of available logistic robots to the
        circuit network with.

        :getter: Gets the available logistic robot signal, or ``None`` if not
            set.
        :setter: Sets the available logistic robot signal. Removes the key if
            set to ``None``.
        :type: :py:data:`.SIGNAL_ID`

        :exception TypeError: If set to anything that isn't a valid ``SIGNAL_ID``
            or ``None``.
        """
        return self.control_behavior.available_logistic_output_signal

    @available_logistic_signal.setter
    def available_logistic_signal(self, value: Union[str, SignalID, None]):
        if self.validate_assignment:
            result = attempt_and_reissue(
                self,
                type(self).Format.ControlBehavior,
                self.control_behavior,
                "available_logistic_output_signal",
                value,
            )
            self.control_behavior.available_logistic_output_signal = result
        else:
            self.control_behavior.available_logistic_output_signal = value

    # =========================================================================

    @property
    def total_logistic_signal(self) -> Optional[SignalID]:
        """
        What signal to output the total number of logistic robots to the
        circuit network with.

        :getter: Gets the total logistic robot signal, or ``None`` if not set.
        :setter: Sets the total logistic robot signal. Removes the key if set to
            ``None``.
        :type: :py:data:`.SIGNAL_ID`

        :exception TypeError: If set to anything that isn't a valid ``SIGNAL_ID``
            or ``None``.
        """
        return self.control_behavior.total_logistic_output_signal

    @total_logistic_signal.setter
    def total_logistic_signal(self, value: Union[str, SignalID, None]):
        if self.validate_assignment:
            result = attempt_and_reissue(
                self,
                type(self).Format.ControlBehavior,
                self.control_behavior,
                "total_logistic_output_signal",
                value,
            )
            self.control_behavior.total_logistic_output_signal = result
        else:
            self.control_behavior.total_logistic_output_signal = value

    # =========================================================================

    @property
    def available_construction_signal(self) -> Optional[SignalID]:
        """
        What signal to output the number of available construction robots to the
        circuit network with.

        :getter: Gets the available construction robot signal, or ``None`` if
            not set.
        :setter: Sets the available construction robot signal. Removes the key
            if set to ``None``.
        :type: :py:data:`.SIGNAL_ID`

        :exception TypeError: If set to anything that isn't a valid ``SIGNAL_ID``
            or ``None``.
        """
        return self.control_behavior.available_construction_output_signal

    @available_construction_signal.setter
    def available_construction_signal(self, value: Union[str, SignalID, None]):
        if self.validate_assignment:
            result = attempt_and_reissue(
                self,
                type(self).Format.ControlBehavior,
                self.control_behavior,
                "available_construction_output_signal",
                value,
            )
            self.control_behavior.available_construction_output_signal = result
        else:
            self.control_behavior.available_construction_output_signal = value

    # =========================================================================

    @property
    def total_construction_signal(self) -> Optional[SignalID]:
        """
        What signal to output the total number of construction robots to the
        circuit network with.

        :getter: Gets the total construction robot signal, or ``None`` if not
            set.
        :setter: Sets the total construction robot signal. Removes the key if
            set to ``None``.
        :type: :py:data:`.SIGNAL_ID`

        :exception TypeError: If set to anything that isn't a valid ``SIGNAL_ID``
            or ``None``.
        """
        return self.control_behavior.total_construction_output_signal

    @total_construction_signal.setter
    def total_construction_signal(self, value: Union[str, SignalID, None]):
        if self.validate_assignment:
            result = attempt_and_reissue(
                self,
                type(self).Format.ControlBehavior,
                self.control_behavior,
                "total_construction_output_signal",
                value,
            )
            self.control_behavior.total_construction_output_signal = result
        else:
            self.control_behavior.total_construction_output_signal = value

    # =========================================================================

    __hash__ = Entity.__hash__
