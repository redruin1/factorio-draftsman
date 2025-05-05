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
from draftsman.signatures import AttrsSignalID
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

    # class Format(
    #     ControlBehaviorMixin.Format, CircuitConnectableMixin.Format, Entity.Format
    # ):
    #     class ControlBehavior(DraftsmanBaseModel):
    #         read_logistics: Optional[bool] = Field(
    #             True,
    #             description="""
    #             Whether this roboport will broadcast the contents of the
    #             logistic network it is part of to any connected circuit network.
    #             """,
    #         )
    #         read_robot_stats: Optional[bool] = Field(
    #             False,
    #             description="""
    #             Whether this roboport will broadcast the number of robots in the
    #             logistic network it is part of to any connected circuit network.
    #             """,
    #         )
    #         available_logistic_output_signal: Optional[SignalID] = Field(
    #             SignalID(name="signal-X", type="virtual"),
    #             description="""
    #             The signal to broadcast the number of available logistic robots
    #             on.
    #             """,
    #         )
    #         total_logistic_output_signal: Optional[SignalID] = Field(
    #             SignalID(name="signal-Y", type="virtual"),
    #             description="""
    #             The signal to broadcast the total number of logistic robots on.
    #             """,
    #         )
    #         available_construction_output_signal: Optional[SignalID] = Field(
    #             SignalID(name="signal-Z", type="virtual"),
    #             description="""
    #             The signal to broadcast the number of available construction
    #             robots on.
    #             """,
    #         )
    #         total_construction_output_signal: Optional[SignalID] = Field(
    #             SignalID(name="signal-T", type="virtual"),
    #             description="""
    #             The signal to broadcast the total number of construction robots
    #             on.
    #             """,
    #         )

    #     control_behavior: Optional[ControlBehavior] = ControlBehavior()

    #     model_config = ConfigDict(title="Roboport")

    # def __init__(
    #     self,
    #     name: Optional[str] = get_first(roboports),
    #     position: Union[Vector, PrimitiveVector] = None,
    #     tile_position: Union[Vector, PrimitiveVector] = (0, 0),
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

    #     self.control_behavior: __class__.Format.ControlBehavior

    #     super().__init__(
    #         name,
    #         roboports,
    #         position=position,
    #         tile_position=tile_position,
    #         control_behavior=control_behavior,
    #         tags=tags,
    #         **kwargs
    #     )

    #     self.validate_assignment = validate_assignment

    # =========================================================================

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

    # @property
    # def read_logistics(self) -> Optional[bool]:
    #     """
    #     Whether or not to read the item contents of the logisitics network.

    #     :getter: Gets whether or not the logistics are read, or ``None`` if not
    #         set.
    #     :setter: Sets whether or not the logistics are read. Removes the key if
    #         set to ``None``.

    #     :exception TypeError: If set to anything other than a ``bool`` or ``None``.
    #     """
    #     return self.control_behavior.read_logistics

    # @read_logistics.setter
    # def read_logistics(self, value: Optional[bool]):
    #     if self.validate_assignment:
    #         result = attempt_and_reissue(
    #             self,
    #             type(self).Format.ControlBehavior,
    #             self.control_behavior,
    #             "read_logistics",
    #             value,
    #         )
    #         self.control_behavior.read_logistics = result
    #     else:
    #         self.control_behavior.read_logistics = value

    # =========================================================================

    read_robot_stats: bool = attrs.field(default=False, validator=instance_of(bool))
    """
    Whether or not to read the number of construction and logistics robots
    in the logisitics network to any connected circuit network.

    :exception DataFormatError: If set to anything other than a ``bool`` or ``None``.
    """

    # @property
    # def read_robot_stats(self) -> Optional[bool]:
    #     """
    #     Whether or not to read the number of construction and logistics robots
    #     in the logisitics network.

    #     :getter: Gets whether or not the robot counts are read, or ``None`` if
    #         not set.
    #     :setter: Sets whether or not the robot counts are read. Removes the key
    #         if set to ``None``.

    #     :exception TypeError: If set to anything other than a ``bool`` or ``None``.
    #     """
    #     return self.control_behavior.read_robot_stats

    # @read_robot_stats.setter
    # def read_robot_stats(self, value: Optional[bool]):
    #     if self.validate_assignment:
    #         result = attempt_and_reissue(
    #             self,
    #             type(self).Format.ControlBehavior,
    #             self.control_behavior,
    #             "read_robot_stats",
    #             value,
    #         )
    #         self.control_behavior.read_robot_stats = result
    #     else:
    #         self.control_behavior.read_robot_stats = value

    # =========================================================================

    available_logistic_signal: Optional[AttrsSignalID] = attrs.field(
        factory=lambda: AttrsSignalID(name="signal-X", type="virtual"),
        converter=AttrsSignalID.converter,
        validator=instance_of(Optional[AttrsSignalID]),
    )
    """
    What signal to output the number of available logistic robots to the
    circuit network with.

    :exception DataFormatError: If set to anything that isn't a valid 
        ``SIGNAL_ID`` or ``None``.
    """

    # @property
    # def available_logistic_signal(self) -> Optional[SignalID]:
    #     """
    #     What signal to output the number of available logistic robots to the
    #     circuit network with.

    #     :getter: Gets the available logistic robot signal, or ``None`` if not
    #         set.
    #     :setter: Sets the available logistic robot signal. Removes the key if
    #         set to ``None``.

    #     :exception TypeError: If set to anything that isn't a valid ``SIGNAL_ID``
    #         or ``None``.
    #     """
    #     return self.control_behavior.available_logistic_output_signal

    # @available_logistic_signal.setter
    # def available_logistic_signal(self, value: Union[str, SignalID, None]):
    #     if self.validate_assignment:
    #         result = attempt_and_reissue(
    #             self,
    #             type(self).Format.ControlBehavior,
    #             self.control_behavior,
    #             "available_logistic_output_signal",
    #             value,
    #         )
    #         self.control_behavior.available_logistic_output_signal = result
    #     else:
    #         self.control_behavior.available_logistic_output_signal = value

    # =========================================================================

    total_logistic_signal: Optional[AttrsSignalID] = attrs.field(
        factory=lambda: AttrsSignalID(name="signal-Y", type="virtual"),
        converter=AttrsSignalID.converter,
        validator=instance_of(Optional[AttrsSignalID]),
    )
    """
    What signal to output the total number of logistic robots to the
    circuit network with.

    :exception DataFormatError: If set to anything that isn't a valid 
        ``SIGNAL_ID`` or ``None``.
    """

    # @property
    # def total_logistic_signal(self) -> Optional[SignalID]:
    #     """
    #     What signal to output the total number of logistic robots to the
    #     circuit network with.

    #     :getter: Gets the total logistic robot signal, or ``None`` if not set.
    #     :setter: Sets the total logistic robot signal. Removes the key if set to
    #         ``None``.

    #     :exception TypeError: If set to anything that isn't a valid ``SIGNAL_ID``
    #         or ``None``.
    #     """
    #     return self.control_behavior.total_logistic_output_signal

    # @total_logistic_signal.setter
    # def total_logistic_signal(self, value: Union[str, SignalID, None]):
    #     if self.validate_assignment:
    #         result = attempt_and_reissue(
    #             self,
    #             type(self).Format.ControlBehavior,
    #             self.control_behavior,
    #             "total_logistic_output_signal",
    #             value,
    #         )
    #         self.control_behavior.total_logistic_output_signal = result
    #     else:
    #         self.control_behavior.total_logistic_output_signal = value

    # =========================================================================

    available_construction_signal: Optional[AttrsSignalID] = attrs.field(
        factory=lambda: AttrsSignalID(name="signal-Z", type="virtual"),
        converter=AttrsSignalID.converter,
        validator=instance_of(Optional[AttrsSignalID]),
    )
    """
    What signal to output the number of available construction robots to the
    circuit network with.

    :exception DataFormatError: If set to anything that isn't a valid 
        ``SIGNAL_ID`` or ``None``.
    """

    # @property
    # def available_construction_signal(self) -> Optional[SignalID]:
    #     """
    #     What signal to output the number of available construction robots to the
    #     circuit network with.

    #     :getter: Gets the available construction robot signal, or ``None`` if
    #         not set.
    #     :setter: Sets the available construction robot signal. Removes the key
    #         if set to ``None``.

    #     :exception TypeError: If set to anything that isn't a valid ``SIGNAL_ID``
    #         or ``None``.
    #     """
    #     return self.control_behavior.available_construction_output_signal

    # @available_construction_signal.setter
    # def available_construction_signal(self, value: Union[str, SignalID, None]):
    #     if self.validate_assignment:
    #         result = attempt_and_reissue(
    #             self,
    #             type(self).Format.ControlBehavior,
    #             self.control_behavior,
    #             "available_construction_output_signal",
    #             value,
    #         )
    #         self.control_behavior.available_construction_output_signal = result
    #     else:
    #         self.control_behavior.available_construction_output_signal = value

    # =========================================================================

    total_construction_signal: Optional[AttrsSignalID] = attrs.field(
        factory=lambda: AttrsSignalID(name="signal-T", type="virtual"),
        converter=AttrsSignalID.converter,
        validator=instance_of(Optional[AttrsSignalID]),
    )
    """
    What signal to output the total number of construction robots to the
    circuit network with.

    :exception DataFormatError: If set to anything that isn't a valid 
        ``SIGNAL_ID`` or ``None``.
    """

    # @property
    # def total_construction_signal(self) -> Optional[SignalID]:
    #     """
    #     What signal to output the total number of construction robots to the
    #     circuit network with.

    #     :getter: Gets the total construction robot signal, or ``None`` if not
    #         set.
    #     :setter: Sets the total construction robot signal. Removes the key if
    #         set to ``None``.

    #     :exception TypeError: If set to anything that isn't a valid ``SIGNAL_ID``
    #         or ``None``.
    #     """
    #     return self.control_behavior.total_construction_output_signal

    # @total_construction_signal.setter
    # def total_construction_signal(self, value: Union[str, SignalID, None]):
    #     if self.validate_assignment:
    #         result = attempt_and_reissue(
    #             self,
    #             type(self).Format.ControlBehavior,
    #             self.control_behavior,
    #             "total_construction_output_signal",
    #             value,
    #         )
    #         self.control_behavior.total_construction_output_signal = result
    #     else:
    #         self.control_behavior.total_construction_output_signal = value

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


draftsman_converters.add_schema(
    {"$id": "factorio:roboport"},
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
