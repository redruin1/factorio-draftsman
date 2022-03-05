# loader.py

from draftsman.prototypes.mixins import (
    FiltersMixin, IOTypeMixin, DirectionalMixin, Entity
)
from draftsman.errors import InvalidEntityID
from draftsman.utils import warn_user

from draftsman.data.entities import loaders


class Loader(FiltersMixin, IOTypeMixin, DirectionalMixin, Entity):
    """
    """
    def __init__(self, name: str = loaders[0], **kwargs):
        if name not in loaders:
            raise InvalidEntityID("'{}' is not a valid name for this type"
                                  .format(name))
        super(Loader, self).__init__(name, **kwargs)

        for unused_arg in self.unused_args:
            warn_user("{} has no attribute '{}'".format(type(self), unused_arg))