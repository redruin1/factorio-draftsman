# wall.py

from draftsman.prototypes.mixins import (
    CircuitConditionMixin, EnableDisableMixin, ControlBehaviorMixin, 
    CircuitConnectableMixin, Entity
)
from draftsman.errors import InvalidEntityID
from draftsman.utils import warn_user, signal_dict
import draftsman.signatures as signatures

from draftsman.data.entities import walls


class Wall(CircuitConditionMixin, EnableDisableMixin, ControlBehaviorMixin, 
           CircuitConnectableMixin, Entity):
    def __init__(self, name: str = walls[0], **kwargs):
        if name not in walls:
            raise InvalidEntityID("'{}' is not a valid name for this type"
                                  .format(name))
        super(Wall, self).__init__(name, **kwargs)

        for unused_arg in self.unused_args:
            warn_user("{} has no attribute '{}'".format(type(self), unused_arg))

    def set_enable_disable(self, value: bool) -> None:
        """
        Overwritten
        """
        if value is None:
            self.control_behavior.pop("circuit_open_gate", None)
        else:
            value = signatures.BOOLEAN.validate(value)
            self.control_behavior["circuit_open_gate"] = value

    def set_read_gate(self, value: bool) -> None:
        """
        """
        if value is None:
            self.control_behavior.pop("circuit_read_sensor", None)
        else:
            value = signatures.BOOLEAN.validate(value)
            self.control_behavior["circuit_read_sensor"] = value

    def set_output_signal(self, signal: bool) -> None:
        """
        """
        if signal is None:
            self.control_behavior.pop("output_signal", None)
        else:
            self.control_behavior["output_signal"] = signal_dict(signal)
