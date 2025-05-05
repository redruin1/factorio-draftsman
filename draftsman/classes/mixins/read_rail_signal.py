# read_rail_signal.py

from draftsman.serialization import draftsman_converters
from draftsman.signatures import AttrsSignalID
from draftsman.validators import instance_of

import attrs
from pydantic import BaseModel, Field
from typing import Optional, Union

from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no coverage
    from draftsman.classes.entity import Entity


@attrs.define(slots=False)
class ReadRailSignalMixin:  # (ControlBehaviorMixin)
    """
    (Implicitly inherits :py:class:`~.ControlBehaviorMixin`)

    Allows the Entity to set red, yellow, and green circuit output signals.
    """

    # =========================================================================

    red_output_signal: Optional[AttrsSignalID] = attrs.field(
        factory=lambda: AttrsSignalID(name="signal-red", type="virtual"),
        converter=AttrsSignalID.converter,
        validator=instance_of(Optional[AttrsSignalID]),
    )
    """
    The red output signal. Sent with a unit value when the rail signal's state 
    is red.
    """

    # @property
    # def red_output_signal(self) -> Optional[SignalID]:
    #     """
    #     The red output signal. Sent when the rail signal's state is red.

    #     Stored as a ``dict`` in the format ``{"name": str, "type": str}``, where
    #     ``name`` is the name of the signal and ``type`` is it's type, either
    #     ``"item"``, ``"fluid"``, or ``"signal"``.

    #     However, because a signal's type is always constant and can be inferred,
    #     it is recommended to simply set the attribute to the string name of the
    #     signal which will automatically be converted to the above format.

    #     :getter: Gets the red output signal, or ``None`` if not set.
    #     :setter: Sets the red output signal. Removes the key if set to ``None``.

    #     :exception InvalidSignalID: If set to a string that is not a valid
    #         signal name.
    #     :exception DataFormatError: If set to a dict that does not match the
    #         dict format specified above.
    #     """
    #     return self.control_behavior.red_output_signal

    # @red_output_signal.setter
    # def red_output_signal(self, value: Union[str, SignalID, None]):
    #     if self.validate_assignment:
    #         result = attempt_and_reissue(
    #             self,
    #             type(self).Format.ControlBehavior,
    #             self.control_behavior,
    #             "red_output_signal",
    #             value,
    #         )
    #         self.control_behavior.red_output_signal = result
    #     else:
    #         self.control_behavior.red_output_signal = value

    # =========================================================================

    yellow_output_signal: Optional[AttrsSignalID] = attrs.field(
        factory=lambda: AttrsSignalID(name="signal-yellow", type="virtual"),
        converter=AttrsSignalID.converter,
        validator=instance_of(Optional[AttrsSignalID]),
    )
    """
    The yellow output signal. Sent with a unit value when the rail signal's 
    state is yellow.
    """

    # @property
    # def yellow_output_signal(self) -> Optional[SignalID]:
    #     """
    #     The yellow output signal. Sent when the rail signal's state is yellow.

    #     Stored as a ``dict`` in the format ``{"name": str, "type": str}``, where
    #     ``name`` is the name of the signal and ``type`` is it's type, either
    #     ``"item"``, ``"fluid"``, or ``"signal"``.

    #     However, because a signal's type is always constant and can be inferred,
    #     it is recommended to simply set the attribute to the string name of the
    #     signal which will automatically be converted to the above format.

    #     :getter: Gets the yellow output signal, or ``None`` if not set.
    #     :setter: Sets the yellow output signal. Removes the key if set to ``None``.

    #     :exception InvalidSignalID: If set to a string that is not a valid
    #         signal name.
    #     :exception DataFormatError: If set to a dict that does not match the
    #         dict format specified above.
    #     """
    #     return self.control_behavior.yellow_output_signal

    # @yellow_output_signal.setter
    # def yellow_output_signal(self, value: Union[str, SignalID, None]):
    #     if self.validate_assignment:
    #         result = attempt_and_reissue(
    #             self,
    #             type(self).Format.ControlBehavior,
    #             self.control_behavior,
    #             "yellow_output_signal",
    #             value,
    #         )
    #         self.control_behavior.yellow_output_signal = result
    #     else:
    #         self.control_behavior.yellow_output_signal = value

    # =========================================================================

    green_output_signal: Optional[AttrsSignalID] = attrs.field(
        factory=lambda: AttrsSignalID(name="signal-green", type="virtual"),
        converter=AttrsSignalID.converter,
        validator=instance_of(Optional[AttrsSignalID]),
    )
    """
    The green output signal. Sent with a unit value when the rail signal's state
    is green.
    """

    # @property
    # def green_output_signal(self) -> Optional[SignalID]:
    #     """
    #     The green output signal. Sent when the rail signal's state is green.

    #     Stored as a ``dict`` in the format ``{"name": str, "type": str}``, where
    #     ``name`` is the name of the signal and ``type`` is it's type, either
    #     ``"item"``, ``"fluid"``, or ``"signal"``.

    #     However, because a signal's type is always constant and can be inferred,
    #     it is recommended to simply set the attribute to the string name of the
    #     signal which will automatically be converted to the above format.

    #     :getter: Gets the green output signal, or ``None`` if not set.
    #     :setter: Sets the green output signal. Removes the key if set to ``None``.

    #     :exception InvalidSignalID: If set to a string that is not a valid
    #         signal name.
    #     :exception DataFormatError: If set to a dict that does not match the
    #         dict format specified above.
    #     """
    #     return self.control_behavior.green_output_signal

    # @green_output_signal.setter
    # def green_output_signal(self, value: Union[str, SignalID, None]):
    #     if self.validate_assignment:
    #         result = attempt_and_reissue(
    #             self,
    #             type(self).Format.ControlBehavior,
    #             self.control_behavior,
    #             "green_output_signal",
    #             value,
    #         )
    #         self.control_behavior.green_output_signal = result
    #     else:
    #         self.control_behavior.green_output_signal = value

    # =========================================================================

    def merge(self, other: "Entity"):
        super(ReadRailSignalMixin, self).merge(other)

        self.red_output_signal = other.red_output_signal
        self.yellow_output_signal = other.yellow_output_signal
        self.green_output_signal = other.green_output_signal


draftsman_converters.get_version((1, 0)).add_schema( # pragma: no branch
    {"$id": "factorio:read_rail_signals_mixin_v1.0"},
    ReadRailSignalMixin,
    lambda fields: {
        ("control_behavior", "red_output_signal"): fields.red_output_signal.name,
        ("control_behavior", "orange_output_signal"): fields.yellow_output_signal.name,
        ("control_behavior", "green_output_signal"): fields.green_output_signal.name,
    },
)

draftsman_converters.get_version((2, 0)).add_schema(
    {"$id": "factorio:read_rail_signals_mixin_v2.0"},
    ReadRailSignalMixin,
    lambda fields: {
        ("control_behavior", "red_output_signal"): fields.red_output_signal.name,
        ("control_behavior", "yellow_output_signal"): fields.yellow_output_signal.name,
        ("control_behavior", "green_output_signal"): fields.green_output_signal.name,
    },
)
