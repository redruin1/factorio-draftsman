# circuit_read_contents.py

from draftsman.classes.exportable import Exportable
from draftsman.constants import BeltReadMode
from draftsman.serialization import draftsman_converters
from draftsman.validators import instance_of

import attrs


@attrs.define(slots=False)
class CircuitReadContentsMixin(Exportable):
    """
    Allows the Entity to read it's contents and send it to a connected circuit
    network.

    .. seealso::

        | :py:class:`.CircuitReadHandMixin`
        | :py:class:`.CircuitReadResourceMixin`
    """

    read_contents: bool = attrs.field(default=False, validator=instance_of(bool))
    """
    .. serialized::

        This attribute is imported/exported from blueprint strings.

    Whether or not this Entity is set to read it's contents to a circuit
    network.
    """

    read_mode: BeltReadMode = attrs.field(
        default=BeltReadMode.PULSE,
        converter=BeltReadMode,
        validator=instance_of(BeltReadMode),
    )
    """
    .. serialized::

        This attribute is imported/exported from blueprint strings.

    The manner in which the contents of the Entity should be read. Either
    ``BeltReadMode.PULSE`, ``BeltReadMode.HOLD``, or 
    ``BeltReadMode.HOLD_ALL_BELTS`` (the lattermost only being available in 
    Factorio 2.0).
    """

    # =========================================================================

    def merge(self, other: "CircuitReadContentsMixin"):
        super().merge(other)
        self.read_contents = other.read_contents
        self.read_mode = other.read_mode


draftsman_converters.get_version((1, 0)).add_hook_fns(
    CircuitReadContentsMixin,
    lambda fields: {
        ("control_behavior", "circuit_read_hand_contents"): fields.read_contents.name,
        ("control_behavior", "circuit_contents_read_mode"): fields.read_mode.name,
    },
    lambda fields, _: {
        ("control_behavior", "circuit_read_hand_contents"): fields.read_contents.name,
        ("control_behavior", "circuit_contents_read_mode"): (
            fields.read_mode,
            # Prevent outputting mode HOLD_ALL_BELTS on Factorio 1.0
            lambda inst: (
                BeltReadMode.PULSE
                if inst.read_mode is BeltReadMode.HOLD_ALL_BELTS
                else inst.read_mode
            ),
        ),
    },
)

draftsman_converters.get_version((2, 0)).add_hook_fns(
    CircuitReadContentsMixin,
    lambda fields: {
        ("control_behavior", "circuit_read_hand_contents"): fields.read_contents.name,
        ("control_behavior", "circuit_contents_read_mode"): fields.read_mode.name,
    },
)
