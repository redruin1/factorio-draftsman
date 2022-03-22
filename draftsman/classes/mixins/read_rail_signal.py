# read_rail_signal.py

from draftsman import signatures
from draftsman.utils import signal_dict

from schema import SchemaError


class ReadRailSignalMixin(object): # (ControlBehaviorMixin)
    """
    TODO
    """
    @property
    def red_output_signal(self):
        # type: () -> dict
        """
        TODO
        """
        return self.control_behavior.get("red_output_signal", None)

    @red_output_signal.setter
    def red_output_signal(self, value):
        # type: (str) -> None
        if value is None:
            self.control_behavior.pop("red_output_signal", None)
        elif isinstance(value, str):
            self.control_behavior["red_output_signal"] = signal_dict(value)
        else: # dict or other
            try:
                value = signatures.SIGNAL_ID.validate(value)
                self.control_behavior["red_output_signal"] = value
            except SchemaError:
                raise TypeError("Incorrectly formatted SignalID")

    # =========================================================================

    @property
    def yellow_output_signal(self):
        # type: () -> dict
        """
        TODO
        """
        return self.control_behavior.get("yellow_output_signal", None)

    @yellow_output_signal.setter
    def yellow_output_signal(self, value):
        # type: (str) -> None
        if value is None:
            self.control_behavior.pop("yellow_output_signal", None)
        elif isinstance(value, str):
            self.control_behavior["yellow_output_signal"] = signal_dict(value)
        else: # dict or other
            try:
                value = signatures.SIGNAL_ID.validate(value)
                self.control_behavior["yellow_output_signal"] = value
            except SchemaError:
                raise TypeError("Incorrectly formatted SignalID")

    # =========================================================================

    @property
    def green_output_signal(self):
        # type: () -> dict
        """
        TODO
        """
        return self.control_behavior["green_output_signal"]

    @green_output_signal.setter
    def green_output_signal(self, value):
        # type: (str) -> None
        if value is None:
            self.control_behavior.pop("green_output_signal", None)
        elif isinstance(value, str):
            self.control_behavior["green_output_signal"] = signal_dict(value)
        else: # dict or other
            try:
                value = signatures.SIGNAL_ID.validate(value)
                self.control_behavior["green_output_signal"] = value
            except SchemaError:
                raise TypeError("Incorrectly formatted SignalID")