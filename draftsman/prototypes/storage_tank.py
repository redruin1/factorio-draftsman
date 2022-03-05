# storage_tank.py

from draftsman.prototypes.mixins import (
    CircuitConnectableMixin, DirectionalMixin, Entity
)
from draftsman.errors import InvalidEntityID
from draftsman.utils import warn_user

from draftsman.data.entities import storage_tanks


class StorageTank(CircuitConnectableMixin, DirectionalMixin, Entity):
    """
    """
    def __init__(self, name: str = storage_tanks[0], **kwargs):
        if name not in storage_tanks:
            raise InvalidEntityID("'{}' is not a valid name for this type"
                                  .format(name))
        super(StorageTank, self).__init__(name, **kwargs)
        
        for unused_arg in self.unused_args:
            warn_user("{} has no attribute '{}'".format(type(self), unused_arg))