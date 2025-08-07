# mode_of_operation.py

from draftsman.classes.exportable import Exportable
from draftsman.constants import InserterModeOfOperation, LogisticModeOfOperation
from draftsman.serialization import draftsman_converters
from draftsman.validators import instance_of


import attrs


@attrs.define(slots=False)
class InserterModeOfOperationMixin(Exportable):
    """
    Gives the :py:class:`.Inserter` a ``mode_of_operation`` attribute.
    """

    mode_of_operation: InserterModeOfOperation = attrs.field(
        default=InserterModeOfOperation.ENABLE_DISABLE,
        converter=InserterModeOfOperation,
        validator=instance_of(InserterModeOfOperation),
    )
    """
    .. deprecated:: 3.0.0 (Factorio 2.0)

        In Factorio 2.0, an inserter can have any combination of these modes
        defined simultaneously, via attributes like 
        :py:attr:`~.Inserter.circuit_enabled`, 
        :py:attr:`~.Inserter.circuit_set_filters`,
        :py:attr:`~.Inserter.circuit_set_stack_size`, etc.
        
        This attribute is only respected when exporting for the old Factorio 1.0
        format.

    .. serialized::

        This attribute is imported/exported from blueprint strings.

    The behavior that the inserter should follow when connected to a circuit
    network, defined as one of several integer "modes".
    """


draftsman_converters.get_version((1, 0)).add_hook_fns(
    InserterModeOfOperationMixin,
    lambda fields: {
        (
            "control_behavior",
            "circuit_mode_of_operation",
        ): fields.mode_of_operation.name,
    },
)


@attrs.define(slots=False)
class LogisticModeOfOperationMixin(Exportable):
    """
    Gives the logistics container a ``mode_of_operation`` attribute.
    """

    mode_of_operation: LogisticModeOfOperation = attrs.field(
        default=LogisticModeOfOperation.SEND_CONTENTS,
        converter=LogisticModeOfOperation,
        validator=instance_of(LogisticModeOfOperation),
    )
    """
    .. serialized::

        This attribute is imported/exported from blueprint strings.

    The behavior that the logistic container should follow when connected to
    a circuit network.
    """


draftsman_converters.add_hook_fns(
    LogisticModeOfOperationMixin,
    lambda fields: {
        ("control_behavior", "circuit_mode_of_operation"): fields.mode_of_operation.name
    },
)
