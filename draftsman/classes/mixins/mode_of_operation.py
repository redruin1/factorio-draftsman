# mode_of_operation.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.constants import InserterModeOfOperation, LogisticModeOfOperation


class InserterModeOfOperationMixin(object):  # (ControlBehaviorMixin)
    """
    (Implicitly inherits :py:class:`~.ControlBehaviorMixin`)

    Gives the Inserter a mode of operation constant.
    """

    @property
    def mode_of_operation(self):
        # type: () -> InserterModeOfOperation
        """
        The behavior that the inserter should follow when connected to a circuit
        network.

        :getter: Gets the mode of operation, or ``None`` if not set.
        :setter: Sets the mode of operation. Removes the key if set to ``None``.
        :type: :py:data:`draftsman.constants.InserterModeOfOperation`

        :exception ValueError: If set to a value that cannot be interpreted as a
            valid ``InserterModeOfOperation``.
        """
        return self.control_behavior.get("circuit_mode_of_operation", None)

    @mode_of_operation.setter
    def mode_of_operation(self, value):
        # type: (InserterModeOfOperation) -> None
        if value is None:
            self.control_behavior.pop("circuit_mode_of_operation", None)
        else:
            value = InserterModeOfOperation(value)
            self.control_behavior["circuit_mode_of_operation"] = value


class LogisticModeOfOperationMixin(object):  # (ControlBehaviorMixin)
    """
    (Implicitly inherits :py:class:`~.ControlBehaviorMixin`)

    Gives the Logistics container a mode of operation constant.
    """

    @property
    def mode_of_operation(self):
        # type: () -> LogisticModeOfOperation
        """
        The behavior that the logistic container should follow when connected to
        a circuit network.

        :getter: Gets the mode of operation, or ``None`` if not set.
        :setter: Sets the mode of operation. Removes the key if set to ``None``.
        :type: :py:data:`draftsman.constants.LogisticModeOfOperation`

        :exception ValueError: If set to a value that cannot be interpreted as a
            valid ``LogisticModeOfOperation``.
        """
        return self.control_behavior.get("circuit_mode_of_operation", None)

    @mode_of_operation.setter
    def mode_of_operation(self, value):
        # type: (LogisticModeOfOperation) -> None
        if value is None:
            self.control_behavior.pop("circuit_mode_of_operation", None)
        else:
            value = LogisticModeOfOperation(value)
            self.control_behavior["circuit_mode_of_operation"] = value
