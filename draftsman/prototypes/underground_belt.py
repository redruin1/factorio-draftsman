# underground_belt.py

from draftsman.prototypes.mixins import IOTypeMixin, DirectionalMixin, Entity
from draftsman.errors import InvalidEntityID
from draftsman.utils import warn_user

from draftsman.data.entities import underground_belts


class UndergroundBelt(IOTypeMixin, DirectionalMixin, Entity):
    """
    """
    def __init__(self, name: str = underground_belts[0], **kwargs):
        if name not in underground_belts:
            raise InvalidEntityID("'{}' is not a valid name for this type"
                                  .format(name))
        super(UndergroundBelt, self).__init__(name, **kwargs)

        for unused_arg in self.unused_args:
            warn_user("{} has no attribute '{}'".format(type(self), unused_arg))