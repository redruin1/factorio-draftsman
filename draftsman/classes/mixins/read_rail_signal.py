# read_rail_signal.py

from draftsman.classes.exportable import attempt_and_reissue
from draftsman.signatures import SignalID

from pydantic import BaseModel, Field
from typing import Optional, Union

from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no coverage
    from draftsman.classes.entity import Entity


class ReadRailSignalMixin:  # (ControlBehaviorMixin)
    """
    (Implicitly inherits :py:class:`~.ControlBehaviorMixin`)

    Allows the Entity to set red, yellow, and green circuit output signals.
    """

    class ControlFormat(BaseModel):
        red_output_signal: Optional[SignalID] = Field(
            SignalID(name="signal-red", type="virtual"),
            description="""Circuit signal to output when the train signal reads red.""",
        )
        yellow_output_signal: Optional[SignalID] = Field(
            SignalID(name="signal-yellow", type="virtual"),
            alias="orange_output_signal",
            description="""Circuit signal to output when the train signal reads yellow/orange.""",
        )
        green_output_signal: Optional[SignalID] = Field(
            SignalID(name="signal-green", type="virtual"),
            description="""Circuit signal to output when the train signal reads green.""",
        )

    class Format(BaseModel):
        pass

    @property
    def red_output_signal(self) -> Optional[SignalID]:
        """
        The red output signal. Sent when the rail signal's state is red.

        Stored as a ``dict`` in the format ``{"name": str, "type": str}``, where
        ``name`` is the name of the signal and ``type`` is it's type, either
        ``"item"``, ``"fluid"``, or ``"signal"``.

        However, because a signal's type is always constant and can be inferred,
        it is recommended to simply set the attribute to the string name of the
        signal which will automatically be converted to the above format.

        :getter: Gets the red output signal, or ``None`` if not set.
        :setter: Sets the red output signal. Removes the key if set to ``None``.
        :type: :py:class:`draftsman.signatures.SIGNAL_ID`

        :exception InvalidSignalID: If set to a string that is not a valid
            signal name.
        :exception DataFormatError: If set to a dict that does not match the
            dict format specified above.
        """
        return self.control_behavior.red_output_signal

    @red_output_signal.setter
    def red_output_signal(self, value: Union[str, SignalID, None]):
        if self.validate_assignment:
            result = attempt_and_reissue(
                self,
                type(self).Format.ControlBehavior,
                self.control_behavior,
                "red_output_signal",
                value,
            )
            self.control_behavior.red_output_signal = result
        else:
            self.control_behavior.red_output_signal = value

    # =========================================================================

    @property
    def yellow_output_signal(self) -> Optional[SignalID]:
        """
        The yellow (internally: orange) output signal. Sent when the rail
        signal's state is yellow.

        Stored as a ``dict`` in the format ``{"name": str, "type": str}``, where
        ``name`` is the name of the signal and ``type`` is it's type, either
        ``"item"``, ``"fluid"``, or ``"signal"``.

        However, because a signal's type is always constant and can be inferred,
        it is recommended to simply set the attribute to the string name of the
        signal which will automatically be converted to the above format.

        :getter: Gets the yellow output signal, or ``None`` if not set.
        :setter: Sets the yellow output signal. Removes the key if set to ``None``.
        :type: :py:class:`draftsman.signatures.SIGNAL_ID`

        :exception InvalidSignalID: If set to a string that is not a valid
            signal name.
        :exception DataFormatError: If set to a dict that does not match the
            dict format specified above.
        """
        return self.control_behavior.yellow_output_signal

    @yellow_output_signal.setter
    def yellow_output_signal(self, value: Union[str, SignalID, None]):
        if self.validate_assignment:
            result = attempt_and_reissue(
                self,
                type(self).Format.ControlBehavior,
                self.control_behavior,
                "yellow_output_signal",
                value,
            )
            self.control_behavior.yellow_output_signal = result
        else:
            self.control_behavior.yellow_output_signal = value

    # =========================================================================

    @property
    def green_output_signal(self) -> Optional[SignalID]:
        """
        The green output signal. Sent when the rail signal's state is green.

        Stored as a ``dict`` in the format ``{"name": str, "type": str}``, where
        ``name`` is the name of the signal and ``type`` is it's type, either
        ``"item"``, ``"fluid"``, or ``"signal"``.

        However, because a signal's type is always constant and can be inferred,
        it is recommended to simply set the attribute to the string name of the
        signal which will automatically be converted to the above format.

        :getter: Gets the green output signal, or ``None`` if not set.
        :setter: Sets the green output signal. Removes the key if set to ``None``.
        :type: :py:class:`draftsman.signatures.SIGNAL_ID`

        :exception InvalidSignalID: If set to a string that is not a valid
            signal name.
        :exception DataFormatError: If set to a dict that does not match the
            dict format specified above.
        """
        return self.control_behavior.green_output_signal

    @green_output_signal.setter
    def green_output_signal(self, value: Union[str, SignalID, None]):
        if self.validate_assignment:
            result = attempt_and_reissue(
                self,
                type(self).Format.ControlBehavior,
                self.control_behavior,
                "green_output_signal",
                value,
            )
            self.control_behavior.green_output_signal = result
        else:
            self.control_behavior.green_output_signal = value

    # =========================================================================

    def merge(self, other: "Entity"):
        super(ReadRailSignalMixin, self).merge(other)

        self.red_output_signal = other.red_output_signal
        self.yellow_output_signal = other.yellow_output_signal
        self.green_output_signal = other.green_output_signal
