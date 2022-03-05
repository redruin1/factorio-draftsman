# cargo_wagon.py

from draftsman.prototypes.mixins import (
    InventoryFilterMixin, OrientationMixin, Entity
)
from draftsman.errors import InvalidEntityID
from draftsman.utils import warn_user

from draftsman.data.entities import cargo_wagons


class CargoWagon(InventoryFilterMixin, OrientationMixin, Entity):
    """
    """
    def __init__(self, name: str = cargo_wagons[0], **kwargs):
        if name not in cargo_wagons:
            raise InvalidEntityID("'{}' is not a valid name for this type"
                                  .format(name))
        super(CargoWagon, self).__init__(name, **kwargs)

        for unused_arg in self.unused_args:
            warn_user("{} has no attribute '{}'".format(type(self), unused_arg))