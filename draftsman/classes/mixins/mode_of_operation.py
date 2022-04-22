# mode_of_operation.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.constants import ModeOfOperation


class ModeOfOperationMixin(object):  # (ControlBehaviorMixin)
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
        else:
            self.control_behavior["circuit_mode_of_operation"] = ModeOfOperation(value)
