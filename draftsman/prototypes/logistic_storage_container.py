# logistic_storage_container.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import (
    ItemRequestMixin,
    LogisticModeOfOperationMixin,
    CircuitConditionMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    RequestFiltersMixin,
    InventoryMixin,
)
from draftsman.constants import LogisticModeOfOperation
from draftsman.serialization import draftsman_converters
from draftsman.validators import instance_of

from draftsman.data.entities import logistic_storage_containers

import attrs


@attrs.define
class LogisticStorageContainer(
    InventoryMixin,
    ItemRequestMixin,
    # LogisticModeOfOperationMixin,
    # CircuitConditionMixin, # TODO: does this have a condition on 2.0?
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    RequestFiltersMixin,
    Entity,
):
    """
    A logistics container that stores items not currently being used in the
    logistic network.
    """

    # =========================================================================

    @property
    def similar_entities(self) -> list[str]:
        return logistic_storage_containers

    # =========================================================================

    read_contents: bool = attrs.field(default=True, validator=instance_of(bool))
    """
    Whether or not to broadcast the contents of this logi chest to any connected 
    circuit network.

    .. NOTE::

        Only has an effect on versions of Factorio >= 2.0. On prior versions,
        this value is hardcoded to always read the contents to the circuit 
        network if connected by wire.
    """

    # =========================================================================

    __hash__ = Entity.__hash__


@attrs.define
class _ExportLogisticActiveContainer:
    circuit_mode_of_operation: LogisticModeOfOperation = attrs.field(
        default=LogisticModeOfOperation.SEND_CONTENTS
    )


_export_fields = attrs.fields(_ExportLogisticActiveContainer)

# TODO: still not a fan of defining hooks like this
draftsman_converters.get_version((1, 0)).add_hook_fns(
    LogisticStorageContainer,
    lambda fields: {
        ("control_behavior", "circuit_mode_of_operation"): (
            fields.read_contents,
            lambda _: True,  # Always return True
        )
    },
    lambda fields, converter: {
        ("control_behavior", "circuit_mode_of_operation"): (
            _export_fields.circuit_mode_of_operation,
            lambda _: LogisticModeOfOperation.SEND_CONTENTS,  # Always return SEND_CONTENTS
        )
    },
)

draftsman_converters.get_version((2, 0)).add_hook_fns(
    LogisticStorageContainer,
    lambda fields: {
        ("control_behavior", "circuit_mode_of_operation"): (
            fields.read_contents,
            lambda v: v == LogisticModeOfOperation.SEND_CONTENTS,
        )
    },
    lambda fields, converter: {
        ("control_behavior", "circuit_mode_of_operation"): (
            _export_fields.circuit_mode_of_operation,
            lambda inst: LogisticModeOfOperation.SEND_CONTENTS
            if inst.read_contents
            else LogisticModeOfOperation.NONE,
        )
    },
)
