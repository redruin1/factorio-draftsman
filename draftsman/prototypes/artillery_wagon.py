# artillery_wagon.py

from draftsman.prototypes.mixins import OrientationMixin, Entity
from draftsman.errors import InvalidEntityID
from draftsman.utils import warn_user

from draftsman.data.entities import artillery_wagons


class ArtilleryWagon(OrientationMixin, Entity):
    """
    """
    def __init__(self, name: str = artillery_wagons[0], **kwargs):
        if name not in artillery_wagons:
            raise InvalidEntityID("'{}' is not a valid name for this type"
                                  .format(name))
        super(ArtilleryWagon, self).__init__(name, **kwargs)

        for unused_arg in self.unused_args:
            warn_user("{} has no attribute '{}'".format(type(self), unused_arg))