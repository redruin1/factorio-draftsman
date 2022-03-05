# pump.py

from draftsman.prototypes.mixins import (
    CircuitConditionMixin, ControlBehaviorMixin, CircuitConnectableMixin, 
    DirectionalMixin, Entity
)
from draftsman.errors import InvalidEntityID
from draftsman.utils import warn_user

from draftsman.data.entities import pumps


class Pump(CircuitConditionMixin, ControlBehaviorMixin, CircuitConnectableMixin, 
           DirectionalMixin, Entity):
    """
    """
    def __init__(self, name: str = pumps[0], **kwargs):
        if name not in pumps:
            raise InvalidEntityID("'{}' is not a valid name for this type"
                                  .format(name))
        super(Pump, self).__init__(name, **kwargs)

        for unused_arg in self.unused_args:
            warn_user("{} has no attribute '{}'".format(type(self), unused_arg))