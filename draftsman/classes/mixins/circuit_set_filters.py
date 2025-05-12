# circuit_set_filters.py

from draftsman.classes.exportable import Exportable
from draftsman.serialization import draftsman_converters
from draftsman.validators import instance_of

import attrs


@attrs.define(slots=False)
class CircuitSetFiltersMixin(Exportable):
    """
    (Implicitly inherits :py:class:`~.ControlBehaviorMixin`)

    Allows the entity to specify its filters from the circuit network.
    """

    circuit_set_filters: bool = attrs.field(default=False, validator=instance_of(bool))
    """
    Whether or not this entity should set it's filters via signals given to it
    from connected circuit networks.
    """


CircuitSetFiltersMixin.add_schema(
    {
        "properties": {
            "control_behavior": {
                "type": "object",
                "properties": {
                    "circuit_set_filters": {"type": "boolean", "default": "false"}
                },
            }
        }
    }
)


draftsman_converters.add_hook_fns(
    # {"$id": "factorio:circuit_set_filters_mixin"},
    CircuitSetFiltersMixin,
    lambda fields: {
        ("control_behavior", "circuit_set_filters"): fields.circuit_set_filters.name
    },
)
