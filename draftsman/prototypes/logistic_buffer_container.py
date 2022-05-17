# logistic_buffer_container.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import (
    RequestItemsMixin,
    LogisticModeOfOperationMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    RequestFiltersMixin,
    InventoryMixin,
)
from draftsman.constants import LogisticModeOfOperation
from draftsman.warning import DraftsmanWarning

from draftsman.data.entities import logistic_buffer_containers

import warnings


class LogisticBufferContainer(
    InventoryMixin,
    RequestItemsMixin,
    LogisticModeOfOperationMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    RequestFiltersMixin,
    Entity,
):
    """
    A logistics container that requests items on a secondary priority.
    """

    def __init__(self, name=logistic_buffer_containers[0], **kwargs):
        # type: (str, **dict) -> None
        # Set the mode of operation type for this entity
        self._mode_of_operation_type = LogisticModeOfOperation

        super(LogisticBufferContainer, self).__init__(
            name, logistic_buffer_containers, **kwargs
        )

        for unused_arg in self.unused_args:
            warnings.warn(
                "{} has no attribute '{}'".format(type(self), unused_arg),
                DraftsmanWarning,
                stacklevel=2,
            )
