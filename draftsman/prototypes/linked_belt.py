# linked_belt.py

from draftsman.prototypes.mixins import DirectionalMixin, Entity
from draftsman.errors import InvalidEntityID
from draftsman.utils import warn_user

from draftsman.data.entities import linked_belts


class LinkedBelt(DirectionalMixin, Entity):
    """
    Functionally, currently unimplemented. Need to analyze how mods use this 
    entity, as I can't seem to figure out the example one in the game.
    """
    def __init__(self, name: str = linked_belts[0], **kwargs):
        if name not in linked_belts:
            raise InvalidEntityID("'{}' is not a valid name for this type"
                                  .format(name))
        super(LinkedBelt, self).__init__(name, **kwargs)

        for unused_arg in self.unused_args:
            warn_user("{} has no attribute '{}'".format(type(self), unused_arg))