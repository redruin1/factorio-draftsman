# circuit_set_filters.py

from draftsman.classes.exportable import Exportable
from draftsman.serialization import draftsman_converters
from draftsman.validators import instance_of

import attrs


@attrs.define(slots=False)
class CircuitSetFiltersMixin(Exportable):
    """
    Allows the entity to specify its filters from a connected circuit network.
    """

    circuit_set_filters: bool = attrs.field(default=False, validator=instance_of(bool))
    """
    .. serialized::

        This attribute is imported/exported from blueprint strings.

    Whether or not this entity should set it's filters via signals given to it
    from connected circuit networks.
    """


draftsman_converters.add_hook_fns(
    CircuitSetFiltersMixin,
    lambda fields: {
        ("control_behavior", "circuit_set_filters"): fields.circuit_set_filters.name
    },
)
