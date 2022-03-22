# mode_of_operation.py

from draftsman.constants import ModeOfOperation


class ModeOfOperationMixin(object): # (ControlBehaviorMixin)
    """
    TODO
    """
    @property
    def mode_of_operation(self):
        # type: () -> ModeOfOperation
        """
        TODO
        """
        return self.control_behavior.get("circuit_mode_of_operation", None)

    @mode_of_operation.setter
    def mode_of_operation(self, value):
        # type: (ModeOfOperation) -> None
        if value is None:
            self.control_behavior.pop("circuit_mode_of_operation", None)
        elif isinstance(value, int):
            self.control_behavior["circuit_mode_of_operation"] = value
        else:
            raise TypeError(
                "'mode_of_operation' must be either a ModeOfOperation or int"
            )