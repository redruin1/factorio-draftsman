# circuit_read_hand.py

from draftsman.constants import ReadMode


class CircuitReadHandMixin(object): # (ControlBehaviorMixin)
    """
    TODO
    """
    @property
    def read_hand_contents(self):
        # type: () -> bool
        """
        TODO
        """
        return self.control_behavior.get("circuit_read_hand_contents", None)

    @read_hand_contents.setter
    def read_hand_contents(self, value):
        # type: (bool) -> None
        if value is None:
            self.control_behavior.pop("circuit_read_hand_contents", None)
        elif isinstance(value, bool):
            self.control_behavior["circuit_read_hand_contents"] = value
        else:
            raise TypeError("'read_hand_contents' must be a bool or None")

    # =========================================================================

    @property
    def read_mode(self):
        # type: () -> ReadMode
        """
        TODO
        """
        return self.control_behavior.get("circuit_hand_read_mode", None)

    @read_mode.setter
    def read_mode(self, value):
        # type: (ReadMode) -> None
        if value is None:
            self.control_behavior.pop("circuit_hand_read_mode", None)
        elif isinstance(value, int):
            self.control_behavior["circuit_hand_read_mode"] = value
        else:
            raise TypeError(
                "'read_mode' must be an instance of int or None"
            )