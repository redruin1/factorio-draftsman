# circuit_read_contents.py

from draftsman.classes.exportable import attempt_and_reissue
from draftsman.constants import BeltReadMode
from draftsman.serialization import draftsman_converters
from draftsman.validators import instance_of

import attrs
from pydantic import BaseModel, Field
from typing import Optional


@attrs.define(slots=False)
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
        circuit_contents_read_mode: Optional[BeltReadMode] = Field(
            None,
            description="""
            Whether to hold or pulse the belt's surface items, if 
            'circuit_read_hand_contents' is true.
            """,
        )

    class Format(BaseModel):
        pass

    # =========================================================================

    read_contents: bool = attrs.field(default=True, validator=instance_of(bool))
    """
    Whether or not this Entity is set to read it's contents to a circuit
    network.
    """

    # @property
    # def read_contents(self) -> Optional[bool]:
    #     """
    #     Whether or not this Entity is set to read it's contents to a circuit
    #     network.

    #     :getter: Gets the value of ``read_contents``, or ``None`` if not set.
    #     :setter: Sets the value of ``read_contents``.

    #     :exception TypeError: If set to anything other than a ``bool`` or
    #         ``None``.
    #     """
    #     return self.control_behavior.circuit_read_hand_contents

    # @read_contents.setter
    # def read_contents(self, value: Optional[bool]):
    #     if self.validate_assignment:
    #         result = attempt_and_reissue(
    #             self,
    #             self.Format.ControlBehavior,
    #             self.control_behavior,
    #             "circuit_read_hand_contents",
    #             value,
    #         )
    #         self.control_behavior.circuit_read_hand_contents = result
    #     else:
    #         self.control_behavior.circuit_read_hand_contents = value

    # =========================================================================

    read_mode: BeltReadMode = attrs.field(
        default=BeltReadMode.PULSE,
        converter=BeltReadMode,
        validator=instance_of(BeltReadMode),
    )
    """
    The mode in which the contents of the Entity should be read. Either
    ``BeltReadMode.PULSE`, ``BeltReadMode.HOLD``, or 
    ``BeltReadMode.HOLD_ALL_BELTS`` (the lattermost only being available in 
    Factorio 2.0).
    """

    # @property
    # def read_mode(self) -> Optional[BeltReadMode]:
    #     """
    #     The mode in which the contents of the Entity should be read. Either
    #     ``ReadMode.PULSE`` or ``ReadMode.HOLD``.

    #     :getter: Gets the value of ``read_mode``, or ``None`` if not set.
    #     :setter: Sets the value of ``read_mode``.

    #     :exception ValueError: If set to anything other than a ``ReadMode``
    #         value or their ``int`` equivalent.
    #     """
    #     return self.control_behavior.circuit_contents_read_mode

    # @read_mode.setter
    # def read_mode(self, value: Optional[BeltReadMode]):
    #     if self.validate_assignment:
    #         result = attempt_and_reissue(
    #             self,
    #             self.Format.ControlBehavior,
    #             self.control_behavior,
    #             "circuit_contents_read_mode",
    #             value,
    #         )
    #         self.control_behavior.circuit_contents_read_mode = result
    #     else:
    #         self.control_behavior.circuit_contents_read_mode = value

    def merge(self, other: "CircuitReadContentsMixin"):
        super().merge(other)
        self.read_contents = other.read_contents
        self.read_mode = other.read_mode


# TODO: versioning
draftsman_converters.add_schema(
    {
        "$id": "factorio:circuit_read_contents_mixin",
    },
    CircuitReadContentsMixin,
    lambda fields: {
        fields.read_contents.name: ("control_behavior", "circuit_read_hand_contents"),
        fields.read_mode.name: ("control_behavior", "circuit_contents_read_mode"),
    },
)
