# generator.py

from draftsman.prototypes.mixins import DirectionalMixin, Entity
from draftsman.errors import InvalidEntityID
from draftsman.utils import warn_user

from draftsman.data.entities import generators


class Generator(DirectionalMixin, Entity):
    def __init__(self, name: str = generators[0], **kwargs):
        if name not in generators:
            raise InvalidEntityID("'{}' is not a valid name for this type"
                                  .format(name))
        super(Generator, self).__init__(name, **kwargs)

        for unused_arg in self.unused_args:
            warn_user("{} has no attribute '{}'".format(type(self), unused_arg))