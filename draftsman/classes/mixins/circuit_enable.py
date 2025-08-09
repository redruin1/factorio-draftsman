# circuit_enable.py

from draftsman.classes.exportable import Exportable
from draftsman.serialization import draftsman_converters
from draftsman.validators import instance_of

import attrs


@attrs.define(slots=False)
class CircuitEnableMixin(Exportable):
    """
    Allows the entity to control whether or not it's circuit condition affects
    its operation.
    """

    circuit_enabled: bool = attrs.field(default=False, validator=instance_of(bool))
    """
    .. serialized::

        This attribute is imported/exported from blueprint strings.

    Whether or not the machine enables its operation based on a circuit
    condition. Certain entities lack this attribute despite still having a 
    :py:attr:`~.CircuitConditionMixin.circuit_condition`; in those cases, being 
    circuit enabled is implied by being connected to a circuit network at all.
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
