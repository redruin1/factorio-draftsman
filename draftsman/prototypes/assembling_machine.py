# assembling_machine.py

from draftsman.prototypes.mixins import RequestItemsMixin, RecipeMixin, Entity
from draftsman.errors import InvalidEntityID
from draftsman.utils import warn_user

from draftsman.data.entities import assembling_machines


class AssemblingMachine(RequestItemsMixin, RecipeMixin, Entity):
    def __init__(self, name: str = assembling_machines[0], **kwargs):
        if name not in assembling_machines:
            raise InvalidEntityID("'{}' is not a valid name for this type"
                                  .format(name))
        super(AssemblingMachine, self).__init__(name, **kwargs)

        for unused_arg in self.unused_args:
            warn_user("{} has no attribute '{}'".format(type(self), unused_arg))