# stack_size.py

from draftsman.classes.exportable import attempt_and_reissue
from draftsman.error import DataFormatError
from draftsman.signatures import SignalID, uint8
from draftsman.data.signals import signal_dict

from pydantic import BaseModel, Field

# import six
from typing import Optional

from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no coverage
    from draftsman.classes.entity import Entity


class StackSizeMixin:  # (ControlBehaviorMixin)
    """
    (Implicitly inherits :py:class:`~.ControlBehaviorMixin`)

    Gives the entity a stack size attribute. Allows it to give a constant,
    overridden stack size and a circuit-set stack size.
    """

    class ControlFormat(BaseModel):
        circuit_set_stack_size: Optional[bool] = Field(
            None,
            description="""
            Whether or not the circuit network should affect the stack size of 
            this entity.
            """,
        )
        stack_control_input_signal: Optional[SignalID] = Field(
            None,
            description="""
            What circuit signal should be used to override the stack size of 
            this entity, if 'circuit_set_stack_size' is true.
            """,
        )

    class Format(BaseModel):
        override_stack_size: Optional[uint8] = Field(
            None,
            description="""
            The constant stack size override for this entity. Superseded by 
            'stack_control_input_signal', if present and enabled.
            """,
        )

    def __init__(self, name: str, similar_entities: list[str], **kwargs):
        self._root: __class__.Format

        super().__init__(name, similar_entities, **kwargs)

        self.override_stack_size = kwargs.get("override_stack_size", None)

    # =========================================================================

    @property
    def override_stack_size(self) -> Optional[uint8]:
        """
        The inserter's stack size override. Will use this unless a circuit
        stack size is set and enabled.

        :getter: Gets the overridden stack size.
        :setter: Sets the overridden stack size.

        :exception TypeError:
        """
        return self._root.override_stack_size

    @override_stack_size.setter
    def override_stack_size(self, value: Optional[uint8]):
        if self.validate_assignment:
            result = attempt_and_reissue(
                self, type(self).Format, self._root, "override_stack_size", value
            )
            self._root.override_stack_size = result
        else:
            self._root.override_stack_size = value

    # =========================================================================

    @property
    def circuit_stack_size_enabled(self) -> Optional[bool]:
        """
        Sets if the inserter's stack size is controlled by circuit signal.

        :getter: Gets whether or not the circuit stack size is enabled, or
            ``None`` if not set.
        :setter: Sets whether or not the circuit stack size is enabled. Removes
            the key if set to ``None``.

        :exception TypeError: If set to anything other than a ``bool`` or
            ``None``.
        """
        return self.control_behavior.circuit_set_stack_size

    @circuit_stack_size_enabled.setter
    def circuit_stack_size_enabled(self, value: Optional[bool]):
        if self.validate_assignment:
            result = attempt_and_reissue(
                self,
                self.Format.ControlBehavior,
                self.control_behavior,
                "circuit_set_stack_size",
                value,
            )
            self.control_behavior.circuit_set_stack_size = result
        else:
            self.control_behavior.circuit_set_stack_size = value

    # =========================================================================

    @property
    def stack_size_control_signal(self) -> Optional[SignalID]:
        """
        Specify the stack size input signal for the inserter. Will read from
        this signal's value on any connected circuit network and will use that
        value to set the maximum stack size for this entity, if enabled.

        Stored as a ``dict`` in the format ``{"name": str, "type": str}``, where
        ``name`` is the name of the signal and ``type`` is it's type, either
        ``"item"``, ``"fluid"``, or ``"signal"``.

        However, because a signal's type is always constant and can be inferred,
        it is recommended to simply set the attribute to the string name of the
        signal which will automatically be converted to the above format.

        :getter: Gets the stack control signal, or ``None`` if not set.
        :setter: Sets the stack control signal. Removes the key if set to
            ``None``.

        :exception InvalidSignalID: If set to a string that is not a valid
            signal name.
        :exception DataFormatError: If set to a dict that does not match the
            dict format specified above.
        """
        return self.control_behavior.stack_control_input_signal

    @stack_size_control_signal.setter
    def stack_size_control_signal(self, value: Optional[SignalID]):
        if self.validate_assignment:
            result = attempt_and_reissue(
                self,
                self.Format.ControlBehavior,
                self.control_behavior,
                "stack_control_input_signal",
                value,
            )
            self.control_behavior.stack_control_input_signal = result
        else:
            self.control_behavior.stack_control_input_signal = value

    # =========================================================================

    def merge(self, other: "Entity"):
        super(StackSizeMixin, self).merge(other)

        self.override_stack_size = other.override_stack_size

    # =========================================================================

    def __eq__(self, other: "Entity") -> bool:
        return (
            super().__eq__(other)
            and self.override_stack_size == other.override_stack_size
        )
