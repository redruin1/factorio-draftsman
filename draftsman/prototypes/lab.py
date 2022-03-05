# lab.py

from draftsman.prototypes.mixins import RequestItemsMixin, Entity
from draftsman.errors import InvalidEntityID
from draftsman.utils import warn_user

from draftsman.data.entities import labs


class Lab(RequestItemsMixin, Entity):
    def __init__(self, name: str = labs[0], **kwargs):
        if name not in labs:
            raise InvalidEntityID("'{}' is not a valid name for this type"
                                  .format(name))
        super(Lab, self).__init__(name, **kwargs)

        for unused_arg in self.unused_args:
            warn_user("{} has no attribute '{}'".format(type(self), unused_arg))