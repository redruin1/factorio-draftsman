# mode_of_operation.py

from draftsman.classes.exportable import Exportable
from draftsman.constants import InserterModeOfOperation, LogisticModeOfOperation
from draftsman.serialization import draftsman_converters
from draftsman.validators import instance_of

from pydantic import BaseModel, Field

import attrs
from typing import Optional


@attrs.define(slots=False)
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

    # =========================================================================

    mode_of_operation: InserterModeOfOperation = attrs.field(
        default=InserterModeOfOperation.ENABLE_DISABLE,
        converter=InserterModeOfOperation,
        validator=instance_of(InserterModeOfOperation),
    )
    """
    The behavior that the inserter should follow when connected to a circuit
    network.

    :exception DataFormatError: If set to a value that cannot be interpreted as 
        a valid ``InserterModeOfOperation``.
    """

    # @property
    # def mode_of_operation(self) -> Optional[InserterModeOfOperation]:
    #     """
    #     The behavior that the inserter should follow when connected to a circuit
    #     network.

    #     :getter: Gets the mode of operation, or ``None`` if not set.
    #     :setter: Sets the mode of operation. Removes the key if set to ``None``.

    #     :exception ValueError: If set to a value that cannot be interpreted as a
    #         valid ``InserterModeOfOperation``.
    #     """
    #     return self.control_behavior.circuit_mode_of_operation

    # @mode_of_operation.setter
    # def mode_of_operation(self, value: Optional[InserterModeOfOperation]):
    #     if self.validate_assignment:
    #         result = attempt_and_reissue(
    #             self,
    #             type(self).Format.ControlBehavior,
    #             self.control_behavior,
    #             "circuit_mode_of_operation",
    #             value,
    #         )
    #         self.control_behavior.circuit_mode_of_operation = result
    #     else:
    #         self.control_behavior.circuit_mode_of_operation = value


@attrs.define(slots=False)
class LogisticModeOfOperationMixin(Exportable):  # (ControlBehaviorMixin)
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

    mode_of_operation: LogisticModeOfOperation = attrs.field(
        default=LogisticModeOfOperation.SEND_CONTENTS,
        converter=LogisticModeOfOperation,
        validator=instance_of(LogisticModeOfOperation),
    )
    """
    The behavior that the logistic container should follow when connected to
    a circuit network.

    :exception DataFormatError: If set to a value that cannot be interpreted as 
        a valid ``LogisticModeOfOperation``.
    """

    # @property
    # def mode_of_operation(self) -> Optional[LogisticModeOfOperation]:
    #     """
    #     The behavior that the logistic container should follow when connected to
    #     a circuit network.

    #     :getter: Gets the mode of operation, or ``None`` if not set.
    #     :setter: Sets the mode of operation. Removes the key if set to ``None``.

    #     :exception ValueError: If set to a value that cannot be interpreted as a
    #         valid ``LogisticModeOfOperation``.
    #     """
    #     return self.circuit_mode_of_operation

    # @mode_of_operation.setter
    # def mode_of_operation(self, value: Optional[LogisticModeOfOperation]):
    #     if self.validate_assignment:
    #         result = attempt_and_reissue(
    #             self,
    #             type(self).Format.ControlBehavior,
    #             self.control_behavior,
    #             "circuit_mode_of_operation",
    #             value,
    #         )
    #         self.control_behavior.circuit_mode_of_operation = result
    #     else:
    #         self.control_behavior.circuit_mode_of_operation = value


draftsman_converters.add_schema(
    {"$id": "factorio:mode_of_operation_mixin"},
    LogisticModeOfOperationMixin,
    lambda fields: {
        ("control_behavior", "circuit_mode_of_operation"): fields.mode_of_operation.name
    },
)


@attrs.define(slots=False)
class CargoHubModeOfOperationMixin:
    """
    (Implicitly inherits :py:class:`~.ControlBehaviorMixin`)

    Gives the Cargo hub a mode of operation constant.
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

    mode_of_operation: LogisticModeOfOperation = attrs.field(
        default=LogisticModeOfOperation.SEND_CONTENTS,
        converter=LogisticModeOfOperation,
        validator=instance_of(LogisticModeOfOperation),
    )
    """
    The behavior that the logistic container should follow when connected to
    a circuit network.

    :exception DataFormatError: If set to a value that cannot be interpreted as 
        a valid ``LogisticModeOfOperation``.
    """

    # @property
    # def mode_of_operation(self) -> Optional[LogisticModeOfOperation]:
    #     """
    #     The behavior that the logistic container should follow when connected to
    #     a circuit network.

    #     :getter: Gets the mode of operation, or ``None`` if not set.
    #     :setter: Sets the mode of operation. Removes the key if set to ``None``.

    #     :exception ValueError: If set to a value that cannot be interpreted as a
    #         valid ``LogisticModeOfOperation``.
    #     """
    #     return self.control_behavior.circuit_mode_of_operation

    # @mode_of_operation.setter
    # def mode_of_operation(self, value: Optional[LogisticModeOfOperation]):
    #     if self.validate_assignment:
    #         result = attempt_and_reissue(
    #             self,
    #             type(self).Format.ControlBehavior,
    #             self.control_behavior,
    #             "circuit_mode_of_operation",
    #             value,
    #         )
    #         self.control_behavior.circuit_mode_of_operation = result
    #     else:
    #         self.control_behavior.circuit_mode_of_operation = value
