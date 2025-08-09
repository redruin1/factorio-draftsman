# circuit_read_resource.py

from draftsman.classes.exportable import Exportable
from draftsman.constants import MiningDrillReadMode
from draftsman.serialization import draftsman_converters
from draftsman.validators import instance_of

import attrs


@attrs.define(slots=False)
class CircuitReadResourceMixin(Exportable):
    """
    Enables the Entity to read the resources underneath it.

    .. seealso::

        | :py:class:`~draftsman.classes.mixins.circuit_read_contents.CircuitReadContentsMixin`
        | :py:class:`~draftsman.classes.mixins.circuit_read_hand.CircuitReadHandMixin`
    """

    read_resources: bool = attrs.field(default=True, validator=instance_of(bool))
    """
    .. serialized::

        This attribute is imported/exported from blueprint strings.

    Whether or not this Entity is set to read the resources underneath to a
    circuit network.
    """

    read_mode: MiningDrillReadMode = attrs.field(
        default=MiningDrillReadMode.UNDER_DRILL,
        converter=MiningDrillReadMode,
        validator=instance_of(MiningDrillReadMode),
    )
    """
    .. serialized::

        This attribute is imported/exported from blueprint strings.

    The mode in which the resources underneath the Entity should be read.
    """


draftsman_converters.add_hook_fns(
    CircuitReadResourceMixin,
    lambda fields: {
        ("control_behavior", "circuit_read_resources"): fields.read_resources.name,
        ("control_behavior", "circuit_resource_read_mode"): fields.read_mode.name,
    },
)
