# circuit_read_hand.py

from draftsman.classes.exportable import attempt_and_reissue
from draftsman.constants import ReadMode

from pydantic import BaseModel, Field
from typing import Optional


class CircuitReadHandMixin:  # (ControlBehaviorMixin)
    """
    (Implicitly inherits :py:class:`~.ControlBehaviorMixin`)

    Enables the Entity to read it's hand's contents.

    .. seealso::

        | :py:class:`~draftsman.classes.mixins.circuit_read_contents.CircuitReadContentsMixin`
        | :py:class:`~draftsman.classes.mixins.circuit_read_resource.CircuitReadResourceMixin`
    """

    class ControlFormat(BaseModel):
        circuit_read_hand_contents: Optional[bool] = Field(
            None,
            description="""
            Whether or not to read the contents of this inserter's hand.
            """,
        )
        circuit_hand_read_mode: Optional[ReadMode] = Field(
            None,
            description="""
            Whether to hold or pulse the inserter's held items, if 
            'circuit_read_hand_contents' is true.
            """,
        )

    class Format(BaseModel):
        pass

    @property
    def read_hand_contents(self) -> bool:
        """
        Whether or not this Entity is set to read the contents of it's hand to a
        circuit network.

        :getter: Gets the value of ``read_hand_contents``, or ``None`` if not
            set.
        :setter: Sets the value of ``read_hand_contents``.
        :type: ``bool``

        :exception TypeError: If set to anything other than a ``bool`` or
            ``None``.
        """
        return self.control_behavior.circuit_read_hand_contents

    @read_hand_contents.setter
    def read_hand_contents(self, value):
        # type: (bool) -> None
        if self.validate_assignment:
            attempt_and_reissue(self, "circuit_read_hand_contents", value)

        self.control_behavior.circuit_read_hand_contents = value

        # if value is None:
        #     self.control_behavior.pop("circuit_read_hand_contents", None)
        # elif isinstance(value, bool):
        #     self.control_behavior["circuit_read_hand_contents"] = value
        # else:
        #     raise TypeError("'read_hand_contents' must be a bool or None")

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
        return self.control_behavior.circuit_hand_read_mode

    @read_mode.setter
    def read_mode(self, value: ReadMode):
        if self.validate_assignment:
            attempt_and_reissue(self, "circuit_contents_read_mode", value)

        self.control_behavior.circuit_contents_read_mode = value

        # if value is None:
        #     self.control_behavior.pop("circuit_hand_read_mode", None)
        # else:
        #     self.control_behavior["circuit_hand_read_mode"] = ReadMode(value)
