# locomotive.py

from draftsman.prototypes.mixins import ColorMixin, OrientationMixin, Entity
from draftsman.errors import InvalidEntityID
from draftsman.utils import warn_user

from draftsman.data.entities import locomotives


class Locomotive(ColorMixin, OrientationMixin, Entity):
    """
    """
    def __init__(self, name: str = locomotives[0], **kwargs):
        if name not in locomotives:
            raise InvalidEntityID("'{}' is not a valid name for this type".format(name))
        super(Locomotive, self).__init__(name, **kwargs)

        for unused_arg in self.unused_args:
            warn_user("{} has no attribute '{}'".format(type(self), unused_arg))