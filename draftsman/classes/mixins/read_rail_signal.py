# read_rail_signal.py

from draftsman.classes.exportable import Exportable
from draftsman.serialization import draftsman_converters
from draftsman.signatures import SignalID
from draftsman.validators import instance_of

import attrs
from typing import Optional

from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no coverage
    pass


@attrs.define(slots=False)
class ReadRailSignalMixin(Exportable):
    """
    Allows the Entity to set red, yellow, and green circuit output signals.
    """

    red_output_signal: Optional[SignalID] = attrs.field(
        factory=lambda: SignalID(name="signal-red", type="virtual"),
        converter=SignalID.converter,
        validator=instance_of(Optional[SignalID]),
        metadata={"never_null": True},
    )
    """
    .. serialized::

        This attribute is imported/exported from blueprint strings.

    The red output signal. Sent with a unit value when the rail signal's state 
    is red.
    """

    # =========================================================================

    yellow_output_signal: Optional[SignalID] = attrs.field(
        factory=lambda: SignalID(name="signal-yellow", type="virtual"),
        converter=SignalID.converter,
        validator=instance_of(Optional[SignalID]),
        metadata={"never_null": True},
    )
    """
    .. serialized::

        This attribute is imported/exported from blueprint strings.

    The yellow output signal. Sent with a unit value when the rail signal's 
    state is yellow.
    """

    # =========================================================================

    green_output_signal: Optional[SignalID] = attrs.field(
        factory=lambda: SignalID(name="signal-green", type="virtual"),
        converter=SignalID.converter,
        validator=instance_of(Optional[SignalID]),
        metadata={"never_null": True},
    )
    """
    .. serialized::

        This attribute is imported/exported from blueprint strings.

    The green output signal. Sent with a unit value when the rail signal's state
    is green.
    """

    # =========================================================================

    def merge(self, other: "ReadRailSignalMixin"):
        super().merge(other)

        self.red_output_signal = other.red_output_signal
        self.yellow_output_signal = other.yellow_output_signal
        self.green_output_signal = other.green_output_signal


draftsman_converters.get_version((1, 0)).add_hook_fns(
    ReadRailSignalMixin,
    lambda fields: {
        ("control_behavior", "red_output_signal"): fields.red_output_signal.name,
        ("control_behavior", "orange_output_signal"): fields.yellow_output_signal.name,
        ("control_behavior", "green_output_signal"): fields.green_output_signal.name,
    },
)

draftsman_converters.get_version((2, 0)).add_hook_fns(
    ReadRailSignalMixin,
    lambda fields: {
        ("control_behavior", "red_output_signal"): fields.red_output_signal.name,
        ("control_behavior", "yellow_output_signal"): fields.yellow_output_signal.name,
        ("control_behavior", "green_output_signal"): fields.green_output_signal.name,
    },
)
