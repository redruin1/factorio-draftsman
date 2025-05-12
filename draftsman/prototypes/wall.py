# wall.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import (
    CircuitConditionMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
)
from draftsman.serialization import draftsman_converters
from draftsman.signatures import AttrsSignalID
from draftsman.validators import instance_of

from draftsman.data.entities import walls

import attrs
from typing import Optional


@attrs.define
class Wall(
    CircuitConditionMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    Entity,
):
    """
    A static barrier that acts as protection for structures.
    """

    # @schema(version=(1, 0))
    # def json_schema(self) -> dict:
    #     return {
    #         "$id": "factorio:wall"
    #     }

    # @schema(version=(2, 0))
    # def json_schema(self) -> dict:
    #     return {
    #         "$id": "factorio:wall"
    #     }

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

    enable_disable: bool = attrs.field(default=True, validator=instance_of(bool))
    """
    Whether or not this gate should be activated based on an input condition. 
    """

    # @enable_disable.validator
    # def enable_disable_validator(self, attr, value, mode: Optional[ValidationMode] = None):
    #     if self.validate_assignment or mode:
    #         if not isinstance(value, bool):
    #             msg = "{} given invalid value {}".format(attr.name, repr(value))
    #             raise DataFormatError(msg)

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

    read_gate: bool = attrs.field(default=False, validator=instance_of(bool))

    # @read_gate.validator
    # def read_gate_validator(self, attr, value, mode: Optional[ValidationMode] = None):
    #     if self.validate_assignment or mode:
    #         if not isinstance(value, bool):
    #             msg = "{} given invalid value {}".format(attr.name, repr(value))
    #             raise DataFormatError(msg)

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

    output_signal: Optional[AttrsSignalID] = attrs.field(
        factory=lambda: AttrsSignalID(name="signal-G", type="virtual"),
        converter=AttrsSignalID.converter,
        validator=instance_of(Optional[AttrsSignalID]),
    )

    # @output_signal.validator
    # def validate_output_signal(
    #     self, attr, value, mode: Optional[ValidationMode] = None
    # ):
    #     if self.validate_assignment or mode:
    #         if not value is None and not isinstance(value, AttrsSignalID):
    #             msg = "{} given invalid value {}".format(attr.name, repr(value))
    #             raise DataFormatError(msg)

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

    def merge(self, other: "Wall"):
        super().merge(other)

        self.enable_disable = other.enable_disable
        self.read_gate = other.read_gate
        self.output_signal = other.output_signal

    # =========================================================================

    __hash__ = Entity.__hash__


draftsman_converters.get_version((1, 0)).add_hook_fns(
    Wall,
    lambda fields: {
        ("control_behavior", "circuit_open_gate"): fields.enable_disable.name,
        ("control_behavior", "circuit_read_sensor"): fields.read_gate.name,
        ("control_behavior", "output_signal"): fields.output_signal.name,
    },
)

draftsman_converters.get_version((2, 0)).add_hook_fns(
    Wall,
    lambda fields: {
        ("control_behavior", "circuit_open_gate"): fields.enable_disable.name,
        ("control_behavior", "circuit_read_gate"): fields.read_gate.name,
        ("control_behavior", "output_signal"): fields.output_signal.name,
    },
)
