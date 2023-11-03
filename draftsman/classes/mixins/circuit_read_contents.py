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
    def read_contents(self) -> bool:
        """
        Whether or not this Entity is set to read it's contents to a circuit
        network.

        :getter: Gets the value of ``read_contents``, or ``None`` if not set.
        :setter: Sets the value of ``read_contents``.
        :type: ``bool``

        :exception TypeError: If set to anything other than a ``bool`` or
            ``None``.
        """
        return self.control_behavior.circuit_read_hand_contents

    @read_contents.setter
    def read_contents(self, value: bool):
        # type: (bool) -> None
        if self.validate_assignment:
            attempt_and_reissue(self, "circuit_read_hand_contents", value)

        self.control_behavior.circuit_read_hand_contents = value

        # if value is None:
        #     self.control_behavior.pop("circuit_read_hand_contents", None)
        # elif isinstance(value, bool):
        #     self.control_behavior["circuit_read_hand_contents"] = value
        # else:
        #     raise TypeError("'read_contents' must be a bool or None")

    # =========================================================================

    @property
    def read_mode(self) -> ReadMode:
        """
        The mode in which the contents of the Entity should be read. Either
        ``ReadMode.PULSE`` or ``ReadMode.HOLD``.

        :getter: Gets the value of ``read_mode``, or ``None`` if not set.
        :setter: Sets the value of ``read_mode``.
        :type: :py:data:`~draftsman.constants.ReadMode`

        :exception ValueError: If set to anything other than a ``ReadMode``
            value or their ``int`` equivalent.
        """
        return self.control_behavior.circuit_contents_read_mode

    @read_mode.setter
    def read_mode(self, value: ReadMode):
        if self.validate_assignment:
            attempt_and_reissue(self, "circuit_contents_read_mode", value)

        self.control_behavior.circuit_contents_read_mode = value

        # if value is None:
        #     self.control_behavior.pop("circuit_contents_read_mode", None)
        # else:
        #     self.control_behavior["circuit_contents_read_mode"] = ReadMode(value)
