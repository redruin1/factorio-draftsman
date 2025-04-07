# wall.py

from draftsman.classes.entity import Entity
from draftsman.classes.exportable import attempt_and_reissue
from draftsman.classes.mixins import (
    CircuitConditionMixin,
    CircuitEnableMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
)
from draftsman.classes.vector import PrimitiveVector, Vector
from draftsman.constants import ValidationMode
from draftsman.signatures import (
    Connections,
    DraftsmanBaseModel,
    SignalID,
    AttrsSignalID,
)
from draftsman.utils import get_first

from draftsman.data.entities import walls

import attrs
from pydantic import ConfigDict, Field
from typing import Any, Literal, Optional, Union


@attrs.define
class Wall(
    CircuitConditionMixin,
    CircuitEnableMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    Entity,
):
    """
    A barrier that acts as protection for static structures.
    """

    # class Format(
    #     CircuitConditionMixin.Format,
    #     CircuitEnableMixin.Format,
    #     ControlBehaviorMixin.Format,
    #     CircuitConnectableMixin.Format,
    #     Entity.Format,
    # ):
    #     class ControlBehavior(
    #         CircuitConditionMixin.ControlFormat,
    #         CircuitEnableMixin.ControlFormat,
    #         DraftsmanBaseModel,
    #     ):
    #         circuit_open_gate: Optional[bool] = Field(
    #             True,
    #             description="""
    #             Whether or not this gate should be activated based on an input
    #             condition. 'circuit_enabled' equivalent, specifically for
    #             walls.
    #             """,
    #         )
    #         circuit_read_sensor: Optional[bool] = Field(
    #             False,
    #             description="""
    #             Whether or not to read the state of an adjacent gate and
    #             broadcast it to the circuit network.
    #             """,
    #         )
    #         output_signal: Optional[SignalID] = Field(
    #             SignalID(name="signal-G", type="virtual"),
    #             description="""
    #             The output signal type to send the value from
    #             'circuit_read_sensor'.
    #             """,
    #         )

    #     control_behavior: Optional[ControlBehavior] = ControlBehavior()

    #     model_config = ConfigDict(title="Wall")

    # # =========================================================================

    # def __init__(
    #     self,
    #     name: Optional[str] = get_first(walls),
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
    #     self.control_behavior: Wall.Format.ControlBehavior

    #     super().__init__(
    #         name=name,
    #         similar_entities=walls,
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
        return walls

    # =========================================================================

    enable_disable: bool = attrs.field(
        default=True,
        validator=attrs.validators.instance_of(bool),
        metadata={"location": ("control_behavior", "circuit_open_gate")},
    )
    """
    Whether or not this gate should be activated based on an input condition. 
    """

    # @property
    # def enable_disable(self) -> Optional[bool]:
    #     return self.control_behavior.circuit_open_gate

    # @enable_disable.setter
    # def enable_disable(self, value: Optional[bool]):
    #     if self.validate_assignment is not ValidationMode.NONE:
    #         result = attempt_and_reissue(
    #             self,
    #             type(self).Format.ControlBehavior,
    #             self.control_behavior,
    #             "circuit_open_gate",
    #             value,
    #         )
    #         self.control_behavior.circuit_open_gate = result
    #     else:
    #         self.control_behavior.circuit_open_gate = value

    # =========================================================================

    read_gate: bool = attrs.field(
        default=False,
        validator=attrs.validators.instance_of(bool),
        metadata={"location": ("control_behavior", "circuit_read_sensor")},
    )

    # @property
    # def read_gate(self) -> Optional[bool]:
    #     """
    #     Whether or not to read the state of an adjacent gate, whether it's
    #     opened or closed.
    #     """
    #     return self.control_behavior.circuit_read_sensor

    # @read_gate.setter
    # def read_gate(self, value: Optional[bool]):
    #     if self.validate_assignment:
    #         result = attempt_and_reissue(
    #             self,
    #             self.__class__.Format.ControlBehavior,
    #             self.control_behavior,
    #             "circuit_read_sensor",
    #             value,
    #         )
    #         self.control_behavior.circuit_read_sensor = result
    #     else:
    #         self.control_behavior.circuit_read_sensor = value

    # =========================================================================

    output_signal: AttrsSignalID = attrs.field(
        default=AttrsSignalID(name="signal-G", type="virtual"),
        converter=AttrsSignalID.converter,
        validator=attrs.validators.instance_of(AttrsSignalID),
        metadata={"location": ("control_behavior", "output_signal")},
    )

    # @property
    # def output_signal(self) -> Optional[SignalID]:
    #     """
    #     What signal to output the state of the adjacent gate, if this wall is
    #     connected to a circuit network.
    #     """
    #     return self.control_behavior.output_signal

    # @output_signal.setter
    # def output_signal(self, value: Optional[SignalID]):
    #     if self.validate_assignment:
    #         result = attempt_and_reissue(
    #             self,
    #             self.__class__.Format.ControlBehavior,
    #             self.control_behavior,
    #             "output_signal",
    #             value,
    #         )
    #         self.control_behavior.output_signal = result
    #     else:
    #         self.control_behavior.output_signal = value

    # =========================================================================

    __hash__ = Entity.__hash__
