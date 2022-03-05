# logistic_storage_container.py

from draftsman.prototypes.mixins import (
    CircuitConnectableMixin, RequestFiltersMixin, InventoryMixin, Entity
)
from draftsman.errors import InvalidEntityID
from draftsman.utils import warn_user

from draftsman.data.entities import logistic_storage_containers


class LogisticStorageContainer(CircuitConnectableMixin, RequestFiltersMixin, 
                               InventoryMixin, Entity):
    """
    """
    def __init__(self, name: str = logistic_storage_containers[0], **kwargs):
        if name not in logistic_storage_containers:
            raise InvalidEntityID("'{}' is not a valid name for this type"
                                  .format(name))
        super(LogisticStorageContainer, self).__init__(name, **kwargs)

        for unused_arg in self.unused_args:
            warn_user("{} has no attribute '{}'".format(type(self), unused_arg))