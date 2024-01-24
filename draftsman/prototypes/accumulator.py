# accumulator.py


from draftsman.classes.entity import Entity
from draftsman.classes.exportable import attempt_and_reissue
from draftsman.classes.mixins import ControlBehaviorMixin, CircuitConnectableMixin
from draftsman.classes.vector import Vector, PrimitiveVector
from draftsman.constants import ValidationMode
from draftsman.error import DataFormatError
from draftsman.signatures import Connections, DraftsmanBaseModel, SignalID
from draftsman.utils import get_first

from draftsman.data.entities import accumulators
from draftsman.data.signals import signal_dict

from pydantic import ConfigDict, Field
from typing import Any, Literal, Optional, Union


class Accumulator(ControlBehaviorMixin, CircuitConnectableMixin, Entity):
    """
    An entity that stores electricity for periods of high demand.
    """

    class Format(
        ControlBehaviorMixin.Format,
        CircuitConnectableMixin.Format,
        Entity.Format,
    ):
        class ControlBehavior(DraftsmanBaseModel):
            output_signal: Optional[SignalID] = Field(
                SignalID(name="signal-A", type="virtual"),
                description="""
                The output signal to broadcast this accumulators charge level as
                to any connected circuit network. The output value is as a 
                percentage, where '0' is empty and '100' is full.""",
            )

        control_behavior: Optional[ControlBehavior] = ControlBehavior()

        model_config = ConfigDict(title="Accumulator")

    def __init__(
        self,
        name: Optional[str] = get_first(accumulators),
        position: Union[Vector, PrimitiveVector] = None,
        tile_position: Union[Vector, PrimitiveVector] = (0, 0),
        connections: Connections = Connections(),
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

        self.control_behavior: __class__.Format.ControlBehavior

        super().__init__(
            name,
            accumulators,
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
    def output_signal(self) -> Optional[SignalID]:
        """
        The signal used to output this accumulator's charge level, if set.

        :getter: Gets the output signal, or ``None`` if not set.
        :setter: Sets the output signal. Removes the key if set to ``None``.
        :type: :py:data:`.SIGNAL_ID`

        :exception InvalidSignalError: If set to a string not recognized as a valid
            signal name.
        :exception DataFormatError: If set to a ``dict`` that does not comply
            with the :py:data:`.SIGNAL_ID` format.
        """
        return self.control_behavior.output_signal

    @output_signal.setter
    def output_signal(self, value: Union[str, SignalID, None]):  # TODO: SignalName
        if self.validate_assignment:
            result = attempt_and_reissue(
                self,
                type(self).Format.ControlBehavior,
                self.control_behavior,
                "output_signal",
                value,
            )
            self.control_behavior.output_signal = result
        else:
            self.control_behavior.output_signal = value

    # =========================================================================

    __hash__ = Entity.__hash__

    def __eq__(self, other: "Accumulator") -> bool:
        return super().__eq__(other) and self.output_signal == other.output_signal
