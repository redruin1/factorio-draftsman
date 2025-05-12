# circuit_read_resource.py

from draftsman.classes.exportable import Exportable
from draftsman.constants import MiningDrillReadMode
from draftsman.serialization import draftsman_converters
from draftsman.validators import instance_of

import attrs
from pydantic import BaseModel, Field
from typing import Optional


@attrs.define(slots=False)
class CircuitReadResourceMixin(Exportable):
    """
    (Implicitly inherits :py:class:`~.ControlBehaviorMixin`)

    Enables the Entity to read the resources underneath it.

    .. seealso::

        | :py:class:`~draftsman.classes.mixins.circuit_read_contents.CircuitReadContentsMixin`
        | :py:class:`~draftsman.classes.mixins.circuit_read_hand.CircuitReadHandMixin`
    """

    read_resources: bool = attrs.field(default=True, validator=instance_of(bool))
    """
    Whether or not this Entity is set to read the resources underneath to a
    circuit network.

    :exception DataFormatError: If set to anything other than a ``bool``.
    """

    read_mode: MiningDrillReadMode = attrs.field(
        default=MiningDrillReadMode.UNDER_DRILL,
        converter=MiningDrillReadMode,
        validator=instance_of(MiningDrillReadMode),
    )
    """
    The mode in which the resources underneath the Entity should be read.
    Either ``MiningDrillReadMode.UNDER_DRILL`` or
    ``MiningDrillReadMode.TOTAL_PATCH``.

    :exception DataFormatError: If set to anything other than a
        ``MiningDrillReadMode`` value or their ``int`` equivalent.
    """


CircuitReadResourceMixin.add_schema(
    {
        "properties": {
            "control_behavior": {
                "type": "object",
                "properties": {
                    "circuit_read_resources": {"type": "boolean", "default": "true"},
                    "circuit_resource_read_mode": {
                        "enum": [0, 1],
                        "default": 0,
                    },
                },
            }
        }
    }
)

draftsman_converters.add_hook_fns(
    # {"$id": "factorio:circuit_read_resources_mixin"},
    CircuitReadResourceMixin,
    lambda fields: {
        ("control_behavior", "circuit_read_resources"): fields.read_resources.name,
        ("control_behavior", "circuit_resource_read_mode"): fields.read_mode.name,
    },
)
