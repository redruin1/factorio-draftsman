# stack_size.py

from draftsman.classes.exportable import Exportable
from draftsman.serialization import draftsman_converters
from draftsman.signatures import AttrsSignalID, uint8
from draftsman.validators import instance_of

import attrs
from typing import Optional


@attrs.define(slots=False)
class StackSizeMixin(Exportable):
    """
    (Implicitly inherits :py:class:`~.ControlBehaviorMixin`)

    Gives the entity a stack size attribute. Allows it to give a constant,
    overridden stack size and a circuit-set stack size.
    """

    override_stack_size: Optional[uint8] = attrs.field(
        default=None, validator=instance_of(Optional[uint8])
    )
    """
    The inserter's stack size override. Will use this unless a circuit
    stack size is set and enabled.

    :exception DataFormatError: TODO
    """

    # =========================================================================

    circuit_set_stack_size: bool = attrs.field(
        default=False, validator=instance_of(bool)
    )
    """
    Whether or not the inserter's stack size is controlled by circuit signal.

    :exception DataFormatError: If set to anything other than a ``bool``.
    """

    # =========================================================================

    stack_size_control_signal: Optional[AttrsSignalID] = attrs.field(
        default=None,
        converter=AttrsSignalID.converter,
        validator=instance_of(Optional[AttrsSignalID]),
    )
    """
    Specify the stack size input signal for the inserter, if enabled.
    """

    # =========================================================================

    def merge(self, other: "StackSizeMixin"):
        super().merge(other)

        self.override_stack_size = other.override_stack_size
        self.circuit_set_stack_size = other.circuit_set_stack_size
        self.stack_size_control_signal = other.stack_size_control_signal


draftsman_converters.add_hook_fns(
    StackSizeMixin,
    lambda fields: {
        "override_stack_size": fields.override_stack_size.name,
        (
            "control_behavior",
            "circuit_set_stack_size",
        ): fields.circuit_set_stack_size.name,
        (
            "control_behavior",
            "stack_control_input_signal",
        ): fields.stack_size_control_signal.name,
    },
)
