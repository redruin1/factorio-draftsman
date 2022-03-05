# underground_pipe.py

from draftsman.prototypes.mixins import DirectionalMixin, Entity
from draftsman.errors import InvalidEntityID
from draftsman.utils import warn_user

from draftsman.data.entities import underground_pipes


class UndergroundPipe(DirectionalMixin, Entity):
    """
    """
    def __init__(self, name: str = underground_pipes[0], **kwargs):
        if name not in underground_pipes:
            raise InvalidEntityID("'{}' is not a valid name for this type"
                                  .format(name))
        super(UndergroundPipe, self).__init__(name, **kwargs)

        for unused_arg in self.unused_args:
            warn_user("{} has no attribute '{}'".format(type(self), unused_arg))