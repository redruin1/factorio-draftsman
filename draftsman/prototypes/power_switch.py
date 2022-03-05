# power_switch.py

from draftsman.prototypes.mixins import (
    CircuitConditionMixin, LogisticConditionMixin, ControlBehaviorMixin,
    CircuitConnectableMixin, PowerConnectableMixin, DirectionalMixin, Entity
)
from draftsman.errors import InvalidEntityID
from draftsman.utils import warn_user
import draftsman.signatures as signatures

from draftsman.data.entities import power_switches


class PowerSwitch(CircuitConditionMixin, LogisticConditionMixin, 
                  ControlBehaviorMixin, CircuitConnectableMixin, 
                  PowerConnectableMixin, DirectionalMixin, Entity):
    """
    """
    def __init__(self, name: str = power_switches[0], **kwargs):
        if name not in power_switches:
            raise InvalidEntityID("'{}' is not a valid name for this type"
                                  .format(name))
        super(PowerSwitch, self).__init__(name, **kwargs)

        self.dual_power_connectable = True

        self.switch_state = None
        if "switch_state" in kwargs:
            self.set_switch_state(kwargs["switch_state"])
            self.unused_args.pop("switch_state")
        self._add_export("switch_state", lambda x: x is not None)

        for unused_arg in self.unused_args:
            warn_user("{} has no attribute '{}'".format(type(self), unused_arg))

    def set_switch_state(self, value: bool) -> None:
        """
        """
        self.switch_state = signatures.BOOLEAN.validate(value)