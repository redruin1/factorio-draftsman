# transport_belt.py

from draftsman.prototypes.mixins import (
    CircuitReadContentsMixin, LogisticConditionMixin, CircuitConditionMixin,
    EnableDisableMixin, ControlBehaviorMixin, CircuitConnectableMixin,
    DirectionalMixin, Entity
)
from draftsman.errors import InvalidEntityID
from draftsman.utils import warn_user

from draftsman.data.entities import transport_belts


class TransportBelt(CircuitReadContentsMixin, LogisticConditionMixin, 
                    CircuitConditionMixin, EnableDisableMixin, 
                    ControlBehaviorMixin, CircuitConnectableMixin, 
                    DirectionalMixin, Entity):
    """
    """
    def __init__(self, name: str = transport_belts[0], **kwargs):
        if name not in transport_belts:
            raise InvalidEntityID("'{}' is not a valid name for this type"
                                  .format(name))
        super(TransportBelt, self).__init__(name, **kwargs)

        for unused_arg in self.unused_args:
            warn_user("{} has no attribute '{}'".format(type(self), unused_arg))