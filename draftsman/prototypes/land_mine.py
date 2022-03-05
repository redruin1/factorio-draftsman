# land_mine.py

from draftsman.prototypes.mixins import Entity
from draftsman.errors import InvalidEntityID
from draftsman.utils import warn_user

from draftsman.data.entities import land_mines


class LandMine(Entity):
    def __init__(self, name: str = land_mines[0], **kwargs):
        if name not in land_mines:
            raise InvalidEntityID("'{}' is not a valid name for this type"
                                  .format(name))
        super(LandMine, self).__init__(name, **kwargs)

        for unused_arg in self.unused_args:
            warn_user("{} has no attribute '{}'".format(type(self), unused_arg))