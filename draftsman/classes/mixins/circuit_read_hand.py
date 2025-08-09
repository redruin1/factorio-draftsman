# circuit_read_hand.py

from draftsman.classes.exportable import Exportable
from draftsman.constants import InserterReadMode
from draftsman.serialization import draftsman_converters
from draftsman.validators import instance_of

import attrs


@attrs.define(slots=False)
class CircuitReadHandMixin(Exportable):
    """
    Enables the Entity to read it's hand's contents.

    .. seealso::

        | :py:class:`~draftsman.classes.mixins.circuit_read_contents.CircuitReadContentsMixin`
        | :py:class:`~draftsman.classes.mixins.circuit_read_resource.CircuitReadResourceMixin`
    """

    read_hand_contents: bool = attrs.field(default=False, validator=instance_of(bool))
    """
    .. serialized::

        This attribute is imported/exported from blueprint strings.

    Whether or not this Entity is set to read the contents of it's hand to a
    circuit network.
    """

    # =========================================================================

    read_mode: InserterReadMode = attrs.field(
        default=InserterReadMode.PULSE,
        converter=InserterReadMode,
        validator=instance_of(InserterReadMode),
    )
    """
    .. serialized::

        This attribute is imported/exported from blueprint strings.

    The mode in which the contents of the Entity should be read. Either
    ``ReadMode.PULSE`` or ``ReadMode.HOLD``.
    """


draftsman_converters.add_hook_fns(
    CircuitReadHandMixin,
    lambda fields: {
        (
            "control_behavior",
            "circuit_read_hand_contents",
        ): fields.read_hand_contents.name,
        ("control_behavior", "circuit_hand_read_mode"): fields.read_mode.name,
    },
)
