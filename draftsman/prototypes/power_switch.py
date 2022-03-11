# power_switch.py

from draftsman.prototypes.mixins import (
    CircuitConditionMixin, LogisticConditionMixin, ControlBehaviorMixin,
    CircuitConnectableMixin, PowerConnectableMixin, DirectionalMixin, Entity
)
import draftsman.signatures as signatures
from draftsman.warning import DraftsmanWarning

from draftsman.data.entities import power_switches

import warnings


class PowerSwitch(CircuitConditionMixin, LogisticConditionMixin, 
                  ControlBehaviorMixin, CircuitConnectableMixin, 
                  PowerConnectableMixin, DirectionalMixin, Entity):
    """
    """
    def __init__(self, name = power_switches[0], **kwargs):
        # type: (str, **dict) -> None
        super(PowerSwitch, self).__init__(name, power_switches, **kwargs)

        self.dual_power_connectable = True

        self.switch_state = None
        if "switch_state" in kwargs:
            self.set_switch_state(kwargs["switch_state"])
            self.unused_args.pop("switch_state")
        self._add_export("switch_state", lambda x: x is not None)

        for unused_arg in self.unused_args:
            warnings.warn(
                "{} has no attribute '{}'".format(type(self), unused_arg),
                DraftsmanWarning,
                stacklevel = 2
            )

    def set_switch_state(self, value):
        # type: (bool) -> None
        """
        """
        self.switch_state = signatures.BOOLEAN.validate(value)