# mode_of_operation.py

from draftsman.classes.exportable import attempt_and_reissue
from draftsman.constants import InserterModeOfOperation, LogisticModeOfOperation

from pydantic import BaseModel, Field
from typing import Optional


class InserterModeOfOperationMixin:  # (ControlBehaviorMixin)
    """
    (Implicitly inherits :py:class:`~.ControlBehaviorMixin`)

    Gives the Inserter a mode of operation constant.
    """

    class ControlFormat(BaseModel):
        circuit_mode_of_operation: Optional[InserterModeOfOperation] = Field(
            None,
            description="""
            The manner in which this inserter should react when connected to a 
            circuit network.
            """,
        )

    class Format(BaseModel):
        pass

    @property
    def mode_of_operation(self) -> Optional[InserterModeOfOperation]:
        """
        The behavior that the inserter should follow when connected to a circuit
        network.

        :getter: Gets the mode of operation, or ``None`` if not set.
        :setter: Sets the mode of operation. Removes the key if set to ``None``.
        :type: :py:data:`draftsman.constants.InserterModeOfOperation`

        :exception ValueError: If set to a value that cannot be interpreted as a
            valid ``InserterModeOfOperation``.
        """
        return self.control_behavior.circuit_mode_of_operation

    @mode_of_operation.setter
    def mode_of_operation(self, value: Optional[InserterModeOfOperation]):
        if self.validate_assignment:
            result = attempt_and_reissue(
                self,
                type(self).Format.ControlBehavior,
                self.control_behavior,
                "circuit_mode_of_operation",
                value,
            )
            self.control_behavior.circuit_mode_of_operation = result
        else:
            self.control_behavior.circuit_mode_of_operation = value


class LogisticModeOfOperationMixin:  # (ControlBehaviorMixin)
    """
    (Implicitly inherits :py:class:`~.ControlBehaviorMixin`)

    Gives the Logistics container a mode of operation constant.
    """

    class ControlFormat(BaseModel):
        circuit_mode_of_operation: Optional[LogisticModeOfOperation] = Field(
            None,
            description="""
            The manner in which this logistics container should react when 
            connected to a circuit network.
            """,
        )

    class Format(BaseModel):
        pass

    @property
    def mode_of_operation(self) -> Optional[LogisticModeOfOperation]:
        """
        The behavior that the logistic container should follow when connected to
        a circuit network.

        :getter: Gets the mode of operation, or ``None`` if not set.
        :setter: Sets the mode of operation. Removes the key if set to ``None``.
        :type: :py:data:`draftsman.constants.LogisticModeOfOperation`

        :exception ValueError: If set to a value that cannot be interpreted as a
            valid ``LogisticModeOfOperation``.
        """
        return self.control_behavior.circuit_mode_of_operation

    @mode_of_operation.setter
    def mode_of_operation(self, value: Optional[LogisticModeOfOperation]):
        if self.validate_assignment:
            result = attempt_and_reissue(
                self,
                type(self).Format.ControlBehavior,
                self.control_behavior,
                "circuit_mode_of_operation",
                value,
            )
            self.control_behavior.circuit_mode_of_operation = result
        else:
            self.control_behavior.circuit_mode_of_operation = value
