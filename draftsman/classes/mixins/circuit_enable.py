# circuit_enable.py

from draftsman.classes.exportable import attempt_and_reissue

from pydantic import BaseModel, Field
from typing import Optional


class CircuitEnableMixin:  # (ControlBehaviorMixin)
    """
    (Implicitly inherits :py:class:`~.ControlBehaviorMixin`)

    Allows the entity to control whether or not it's circuit condition affects
    its operation.
    """

    class ControlFormat(BaseModel):
        circuit_enabled: Optional[bool] = Field(
            False,
            description="""
            Whether or not this machine will be toggled by some circuit 
            network. Many machines reuse this parameter name, but others have
            unique ones specific to their types.
            """,  # TODO: examples of different keys
        )

    class Format(BaseModel):
        pass

    @property
    def circuit_enabled(self) -> Optional[bool]:
        """
        Whether or not the machine enables its operation based on a circuit
        condition. Only used on entities that have multiple operation states,
        including (but not limited to) a inserters, belts, train-stops,
        power-switches, etc.

        :getter: Gets the value of ``circuit_enable``, or ``None`` if not set.
        :setter: Sets the value of ``circuit_enable``. Removes the attribute if
            set to ``None``.

        :exception TypeError: If set to anything other than a ``bool`` or
            ``None``.
        """
        return self.control_behavior.circuit_enable

    @circuit_enabled.setter
    def circuit_enabled(self, value: Optional[bool]):
        if self.validate_assignment:
            result = attempt_and_reissue(
                self,
                type(self).Format.ControlBehavior,
                self.control_behavior,
                "circuit_enable",
                value,
            )
            self.control_behavior.circuit_enable = result
        else:
            self.control_behavior.circuit_enable = value
