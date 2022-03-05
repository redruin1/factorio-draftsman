# straight_rail.py

from draftsman.prototypes.mixins import (
    DoubleGridAlignedMixin, EightWayDirectionalMixin, Entity
)
from draftsman.errors import InvalidEntityID
from draftsman.utils import warn_user

from draftsman.data.entities import straight_rails


class StraightRail(DoubleGridAlignedMixin, EightWayDirectionalMixin, Entity):
    """
    """
    def __init__(self, name: str = straight_rails[0], **kwargs):
        if name not in straight_rails:
            raise InvalidEntityID("'{}' is not a valid name for this type"
                                  .format(name))
        super(StraightRail, self).__init__(name, **kwargs)

        for unused_arg in self.unused_args:
            warn_user("{} has no attribute '{}'".format(type(self), unused_arg))