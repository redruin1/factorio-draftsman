# mode_of_operation.py

from draftsman.classes.exportable import Exportable
from draftsman.constants import InserterModeOfOperation, LogisticModeOfOperation
from draftsman.serialization import draftsman_converters
from draftsman.validators import instance_of


import attrs


@attrs.define(slots=False)
class InserterModeOfOperationMixin(Exportable):  # (ControlBehaviorMixin)
    """
    (Implicitly inherits :py:class:`~.ControlBehaviorMixin`)

    Gives the Inserter a mode of operation constant.
    """

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


InserterModeOfOperationMixin.add_schema(
    {
        "properties": {
            "control_behavior": {
                "type": "object",
                "properties": {
                    "circuit_mode_of_operation": {"enum": [0, 1, 2], "default": 0}
                },
            }
        }
    }
)

draftsman_converters.add_hook_fns(
    InserterModeOfOperationMixin,
    lambda fields: {
        (
            "control_behavior",
            "circuit_mode_of_operation",
        ): fields.mode_of_operation.name,
    },
)


@attrs.define(slots=False)
class LogisticModeOfOperationMixin(Exportable):  # (ControlBehaviorMixin)
    """
    (Implicitly inherits :py:class:`~.ControlBehaviorMixin`)

    Gives the Logistics container a mode of operation constant.
    """

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


LogisticModeOfOperationMixin.add_schema(
    {
        "properties": {
            "control_behavior": {
                "type": "object",
                "properties": {
                    "circuit_mode_of_operation": {"enum": [0, 1, 2], "default": 0}
                },
            }
        }
    }
)


draftsman_converters.add_hook_fns(
    LogisticModeOfOperationMixin,
    lambda fields: {
        ("control_behavior", "circuit_mode_of_operation"): fields.mode_of_operation.name
    },
)
