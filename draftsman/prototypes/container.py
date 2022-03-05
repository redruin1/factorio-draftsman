# container.py

from draftsman.prototypes.mixins import (
    CircuitConnectableMixin, InventoryMixin, Entity
)
from draftsman.errors import InvalidEntityID
from draftsman.utils import warn_user

from draftsman.data.entities import containers

class Container(CircuitConnectableMixin, InventoryMixin, Entity):
    """
    * `wooden-chest`
    * `iron-chest`
    * `steel-chest`
    * `logistic-chest-active-provider`
    * `logistic-chest-passive-provider`
    """
    def __init__(self, name: str = containers[0], **kwargs):
        if name not in containers:
            raise InvalidEntityID("'{}' is not a valid name for this type"
                                  .format(name))
        super(Container, self).__init__(name, **kwargs)

        for unused_arg in self.unused_args:
            warn_user("{} has no attribute '{}'".format(type(self), unused_arg))