# lamp.py

from draftsman.prototypes.mixins import (
    CircuitConditionMixin, ControlBehaviorMixin, CircuitConnectableMixin, Entity
)
from draftsman.errors import InvalidEntityID
from draftsman.utils import warn_user
import draftsman.signatures as signatures

from draftsman.data.entities import lamps


class Lamp(CircuitConditionMixin, ControlBehaviorMixin, CircuitConnectableMixin,
           Entity):
    """
    """
    def __init__(self, name: str = lamps[0], **kwargs):
        if name not in lamps:
            raise InvalidEntityID("'{}' is not a valid name for this type"
                                  .format(name))
        super(Lamp, self).__init__(name, **kwargs)

        for unused_arg in self.unused_args:
            warn_user("{} has no attribute '{}'".format(type(self), unused_arg))

    def set_use_colors(self, value: bool) -> None:
        """
        """
        if value is None:
            self.control_behavior.pop("use_colors", None)
        else:
            value = signatures.BOOLEAN.validate(value)
            self.control_behavior["use_colors"] = value