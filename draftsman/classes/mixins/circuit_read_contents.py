# circuit_read_contents.py

from draftsman.classes.exportable import attempt_and_reissue
from draftsman.constants import ReadMode

from pydantic import BaseModel, Field
from typing import Optional


class CircuitReadContentsMixin:  # (ControlBehaviorMixin)
    """
    (Implicitly inherits :py:class:`~.ControlBehaviorMixin`)

    Enables the Entity to read it's contents.

    .. seealso::

        | :py:class:`~draftsman.classes.mixins.circuit_read_hand.CircuitReadHandMixin`
        | :py:class:`~draftsman.classes.mixins.circuit_read_resource.CircuitReadResourceMixin`
    """

    class ControlFormat(BaseModel):
        circuit_read_hand_contents: Optional[bool] = Field(
            None,
            description="""
            Whether or not to read the contents of this belt's surface.
            """,
        )
        circuit_contents_read_mode: Optional[ReadMode] = Field(
            None,
            description="""
            Whether to hold or pulse the belt's surface items, if 
            'circuit_read_hand_contents' is true.
            """,
        )

    class Format(BaseModel):
        pass

    @property
    def read_contents(self) -> Optional[bool]:
        """
        Whether or not this Entity is set to read it's contents to a circuit
        network.

        :getter: Gets the value of ``read_contents``, or ``None`` if not set.
        :setter: Sets the value of ``read_contents``.

        :exception TypeError: If set to anything other than a ``bool`` or
            ``None``.
        """
        return self.control_behavior.circuit_read_hand_contents

    @read_contents.setter
    def read_contents(self, value: Optional[bool]):
        if self.validate_assignment:
            result = attempt_and_reissue(
                self,
                self.Format.ControlBehavior,
                self.control_behavior,
                "circuit_read_hand_contents",
                value,
            )
            self.control_behavior.circuit_read_hand_contents = result
        else:
            self.control_behavior.circuit_read_hand_contents = value

    # =========================================================================

    @property
    def read_mode(self) -> Optional[ReadMode]:
        """
        The mode in which the contents of the Entity should be read. Either
        ``ReadMode.PULSE`` or ``ReadMode.HOLD``.

        :getter: Gets the value of ``read_mode``, or ``None`` if not set.
        :setter: Sets the value of ``read_mode``.

        :exception ValueError: If set to anything other than a ``ReadMode``
            value or their ``int`` equivalent.
        """
        return self.control_behavior.circuit_contents_read_mode

    @read_mode.setter
    def read_mode(self, value: Optional[ReadMode]):
        if self.validate_assignment:
            result = attempt_and_reissue(
                self,
                self.Format.ControlBehavior,
                self.control_behavior,
                "circuit_contents_read_mode",
                value,
            )
            self.control_behavior.circuit_contents_read_mode = result
        else:
            self.control_behavior.circuit_contents_read_mode = value
