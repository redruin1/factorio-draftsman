# accumulator.py


from draftsman.classes.entity import Entity
from draftsman.classes.mixins import (
    EnergySourceMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
)
from draftsman.serialization import draftsman_converters
from draftsman.signatures import AttrsSignalID
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

    # class Format(
    #     ControlBehaviorMixin.Format,
    #     CircuitConnectableMixin.Format,
    #     Entity.Format,
    # ):
    #     class ControlBehavior(DraftsmanBaseModel):
    #         output_signal: Optional[SignalID] = Field(
    #             SignalID(name="signal-A", type="virtual"),
    #             description="""
    #             The output signal to broadcast this accumulators charge level as
    #             to any connected circuit network. The output value is as a
    #             percentage, where '0' is empty and '100' is full.""",
    #         )

    #     control_behavior: Optional[ControlBehavior] = ControlBehavior()

    #     model_config = ConfigDict(title="Accumulator")

    # def __init__(
    #     self,
    #     name: Optional[str] = get_first(accumulators),
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
    #         accumulators,
    #         position=position,
    #         tile_position=tile_position,
    #         control_behavior=control_behavior,
    #         tags=tags,
    #         **kwargs
    #     )

    #     self.validate_assignment = validate_assignment

    @property
    def similar_entities(self) -> list:
        return accumulators

    # =========================================================================

    output_signal: Optional[AttrsSignalID] = attrs.field(
        factory=lambda: AttrsSignalID(name="signal-A", type="virtual"),
        converter=AttrsSignalID.converter,
        validator=instance_of(Optional[AttrsSignalID]),
    )
    """
    The signal used to output this accumulator's charge level, if connected to
    a circuit network.

    :exception InvalidSignalError: If set to a string not recognized as a valid
        signal name.
    :exception DataFormatError: If set to a ``dict`` that does not comply
        with the :py:data:`.SIGNAL_ID` format.
    """

    # @property
    # def output_signal(self) -> Optional[SignalID]:
    #     """
    #     The signal used to output this accumulator's charge level, if set.

    #     :getter: Gets the output signal, or ``None`` if not set.
    #     :setter: Sets the output signal. Removes the key if set to ``None``.

    #     :exception InvalidSignalError: If set to a string not recognized as a valid
    #         signal name.
    #     :exception DataFormatError: If set to a ``dict`` that does not comply
    #         with the :py:data:`.SIGNAL_ID` format.
    #     """
    #     return self.control_behavior.output_signal

    # @output_signal.setter
    # def output_signal(self, value: Union[str, SignalID, None]):  # TODO: SignalName
    #     if self.validate_assignment:
    #         result = attempt_and_reissue(
    #             self,
    #             type(self).Format.ControlBehavior,
    #             self.control_behavior,
    #             "output_signal",
    #             value,
    #         )
    #         self.control_behavior.output_signal = result
    #     else:
    #         self.control_behavior.output_signal = value

    # =========================================================================

    def merge(self, other: "Accumulator"):
        super().merge(other)

        self.output_signal = other.output_signal

    __hash__ = Entity.__hash__


Accumulator.add_schema(
    {
        "$id": "urn:factorio:entity:accumulator", # TODO: versionize IDs
        "type": "object",
        "properties": {
            "control_behavior": {
                "type": "object",
                "properties": {
                    "output_signal": {
                        "anyOf": [
                            {"$ref": "urn:factorio:signal-id"},
                            {"type": "null"}
                        ]
                    }
                }
            }
        }
    }
)

draftsman_converters.add_hook_fns(
    Accumulator,
    lambda fields: {("control_behavior", "output_signal"): fields.output_signal.name},
)
