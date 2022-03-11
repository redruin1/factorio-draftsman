# wall.py

from draftsman.prototypes.mixins import (
    CircuitConditionMixin, EnableDisableMixin, ControlBehaviorMixin, 
    CircuitConnectableMixin, Entity
)
import draftsman.signatures as signatures
from draftsman.utils import signal_dict
from draftsman.warning import DraftsmanWarning

from draftsman.data.entities import walls

import warnings


class Wall(CircuitConditionMixin, EnableDisableMixin, ControlBehaviorMixin, 
           CircuitConnectableMixin, Entity):
    def __init__(self, name = walls[0], **kwargs):
        # type: (str, **dict) -> None
        super(Wall, self).__init__(name, walls, **kwargs)

        for unused_arg in self.unused_args:
            warnings.warn(
                "{} has no attribute '{}'".format(type(self), unused_arg),
                DraftsmanWarning,
                stacklevel = 2
            )

    def set_enable_disable(self, value):
        # type: (bool) -> None
        """
        Overwritten
        """
        if value is None:
            self.control_behavior.pop("circuit_open_gate", None)
        else:
            value = signatures.BOOLEAN.validate(value)
            self.control_behavior["circuit_open_gate"] = value

    def set_read_gate(self, value):
        # type: (bool) -> None
        """
        """
        if value is None:
            self.control_behavior.pop("circuit_read_sensor", None)
        else:
            value = signatures.BOOLEAN.validate(value)
            self.control_behavior["circuit_read_sensor"] = value

    def set_output_signal(self, signal):
        # type: (str) -> None
        """
        """
        if signal is None:
            self.control_behavior.pop("output_signal", None)
        else:
            self.control_behavior["output_signal"] = signal_dict(signal)
