# fluid_wagon.py

from draftsman.prototypes.mixins import OrientationMixin, Entity
from draftsman.errors import InvalidEntityID
from draftsman.utils import warn_user

from draftsman.data.entities import fluid_wagons


class FluidWagon(OrientationMixin, Entity):
    """
    """
    def __init__(self, name: str = fluid_wagons[0], **kwargs):
        if name not in fluid_wagons:
            raise InvalidEntityID("'{}' is not a valid name for this type"
                                  .format(name))
        super(FluidWagon, self).__init__(name, **kwargs)

        for unused_arg in self.unused_args:
            warn_user("{} has no attribute '{}'".format(type(self), unused_arg))