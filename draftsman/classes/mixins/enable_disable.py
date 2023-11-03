# enable_disable.py

from draftsman.classes.exportable import attempt_and_reissue

from pydantic import BaseModel, Field
from typing import Optional


class EnableDisableMixin:  # (ControlBehaviorMixin)
    """
    (Implicitly inherits :py:class:`~.ControlBehaviorMixin`)

    Allows the entity to control whether or not it's circuit condition affects
    its operation.
    """

    class ControlFormat(BaseModel):
        circuit_enable_disable: Optional[bool] = Field(
            None,
            description="""
            Whether or not this machine will be toggled by some circuit 
            condition. Many machines reuse this parameter name, but others have
            unique ones specific to their types.
            """,  # TODO: examples of different keys
        )

    class Format(BaseModel):
        pass

    @property
    def enable_disable(self) -> bool:
        """
        Whether or not the machine enables its operation based on a circuit
        condition. Only used on entities that have multiple operation states,
        including (but not limited to) a inserters, belts, train-stops,
        power-switches, etc.

        :getter: Gets the value of ``enable_disable``, or ``None`` if not set.
        :setter: Sets the value of ``enable_disable``. Removes the attribute if
            set to ``None``.
        :type: ``bool``

        :exception TypeError: If set to anything other than a ``bool`` or
            ``None``.
        """
        return self.control_behavior.circuit_enable_disable

    @enable_disable.setter
    def enable_disable(self, value: bool):
        if self.validate_assignment:
            attempt_and_reissue(self, "circuit_enable_disable", value)

        self.control_behavior.circuit_enable_disable = value
