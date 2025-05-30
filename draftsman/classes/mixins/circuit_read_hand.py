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
    Whether or not this Entity is set to read the contents of it's hand to a
    circuit network.

    :getter: Gets the value of ``read_hand_contents``, or ``None`` if not
        set.
    :setter: Sets the value of ``read_hand_contents``.

    :exception TypeError: If set to anything other than a ``bool`` or
        ``None``.
    """

    # =========================================================================

    read_mode: InserterReadMode = attrs.field(
        default=InserterReadMode.PULSE,
        converter=InserterReadMode,
        validator=instance_of(InserterReadMode),
    )
    """
    The mode in which the contents of the Entity should be read. Either
    ``ReadMode.PULSE`` or ``ReadMode.HOLD``.

    :getter: Gets the value of ``read_mode``, or ``None`` if not set.
    :setter: Sets the value of ``read_mode``.

    :exception ValueError: If set to anything other than a ``ReadMode``
        value or their ``int`` equivalent.
    """


# TODO: versioning

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
