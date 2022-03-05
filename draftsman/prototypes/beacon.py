# beacon.py

from draftsman.prototypes.mixins import RequestItemsMixin, Entity
from draftsman.errors import InvalidEntityID
from draftsman.utils import warn_user

from draftsman.data.entities import beacons


class Beacon(RequestItemsMixin, Entity):
    def __init__(self, name: str = beacons[0], **kwargs):
        if name not in beacons:
            raise InvalidEntityID("'{}' is not a valid name for this type"
                                  .format(name))
        super(Beacon, self).__init__(name, **kwargs)

        for unused_arg in self.unused_args:
            warn_user("{} has no attribute '{}'".format(type(self), unused_arg))