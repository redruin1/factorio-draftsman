# circuit_enable.py

from draftsman.classes.exportable import Exportable
from draftsman.serialization import draftsman_converters
from draftsman.validators import instance_of

import attrs


@attrs.define(slots=False)
class CircuitEnableMixin(Exportable):
    """
    (Implicitly inherits :py:class:`~.ControlBehaviorMixin`)

    Allows the entity to control whether or not it's circuit condition affects
    its operation.
    """

    circuit_enabled: bool = attrs.field(  # TODO: should this be `enable_disable`?
        default=False, validator=instance_of(bool)
    )
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

    def merge(self, other: "CircuitEnableMixin"):
        super().merge(other)
        self.circuit_enabled = other.circuit_enabled


draftsman_converters.add_hook_fns(
    CircuitEnableMixin,
    lambda fields: {
        ("control_behavior", "circuit_enabled"): fields.circuit_enabled.name
    },
)
