# logistic_buffer_container.py

from draftsman.prototypes.mixins import (
    ModeOfOperationMixin, ControlBehaviorMixin, CircuitConnectableMixin,
    RequestFiltersMixin, InventoryMixin, Entity
)
from draftsman.errors import InvalidEntityID
from draftsman.utils import warn_user

from draftsman.data.entities import logistic_buffer_containers


class LogisticBufferContainer(ModeOfOperationMixin, ControlBehaviorMixin, 
                              CircuitConnectableMixin, RequestFiltersMixin, 
                              InventoryMixin, Entity):
    """
    """
    def __init__(self, name: str = logistic_buffer_containers[0], **kwargs):
        if name not in logistic_buffer_containers:
            raise InvalidEntityID("'{}' is not a valid name for this type"
                                  .format(name))
        super(LogisticBufferContainer, self).__init__(name, **kwargs)

        for unused_arg in self.unused_args:
            warn_user("{} has no attribute '{}'".format(type(self), unused_arg))