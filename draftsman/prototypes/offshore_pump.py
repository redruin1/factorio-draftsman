# offshore_pump.py

from draftsman.prototypes.mixins import (
    CircuitConditionMixin, LogisticConditionMixin, ControlBehaviorMixin,
    CircuitConnectableMixin, DirectionalMixin, Entity
)
from draftsman.errors import InvalidEntityID
from draftsman.utils import warn_user

from draftsman.data.entities import offshore_pumps


class OffshorePump(CircuitConditionMixin, LogisticConditionMixin, 
                   ControlBehaviorMixin, CircuitConnectableMixin, 
                   DirectionalMixin, Entity):
    def __init__(self, name: str = offshore_pumps[0], **kwargs):
        if name not in offshore_pumps:
            raise InvalidEntityID("'{}' is not a valid name for this type"
                                  .format(name))
        super(OffshorePump, self).__init__(name, **kwargs)

        for unused_arg in self.unused_args:
            warn_user("{} has no attribute '{}'".format(type(self), unused_arg))