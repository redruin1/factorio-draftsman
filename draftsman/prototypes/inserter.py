# inserter.py

from draftsman.prototypes.mixins import (
    StackSizeMixin, CircuitReadHandMixin, ModeOfOperationMixin, 
    CircuitConditionMixin, EnableDisableMixin, LogisticConditionMixin,
    ControlBehaviorMixin, CircuitConnectableMixin, DirectionalMixin, Entity
)
from draftsman.errors import InvalidEntityID
from draftsman.utils import warn_user

from draftsman.data.entities import inserters


class Inserter(StackSizeMixin, CircuitReadHandMixin, ModeOfOperationMixin, 
               CircuitConditionMixin, EnableDisableMixin, 
               LogisticConditionMixin, ControlBehaviorMixin, 
               CircuitConnectableMixin, DirectionalMixin, Entity):
    """
    """
    def __init__(self, name: str = inserters[0], **kwargs):
        if name not in inserters:
            raise InvalidEntityID("'{}' is not a valid name for this type"
                                  .format(name))
        super(Inserter, self).__init__(name, **kwargs)

        for unused_arg in self.unused_args:
            warn_user("{} has no attribute '{}'".format(type(self), unused_arg))