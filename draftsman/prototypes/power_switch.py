# power_switch.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import (
    CircuitConditionMixin,
    LogisticConditionMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    PowerConnectableMixin,
    DirectionalMixin,
)
import draftsman.signatures as signatures
from draftsman.warning import DraftsmanWarning

from draftsman.data.entities import power_switches

import warnings


class PowerSwitch(
    CircuitConditionMixin,
    LogisticConditionMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    PowerConnectableMixin,
    DirectionalMixin,
    Entity,
):
    """
    An entity that connects or disconnects a power network. Can be controlled
    manually or with a circuit condition or a logistic condition.
    """

    def __init__(self, name=power_switches[0], **kwargs):
        # type: (str, **dict) -> None
        super(PowerSwitch, self).__init__(name, power_switches, **kwargs)

        self._dual_power_connectable = True

        self.switch_state = None
        if "switch_state" in kwargs:
            self.switch_state = kwargs["switch_state"]
            self.unused_args.pop("switch_state")
        self._add_export("switch_state", lambda x: x is not None)

        for unused_arg in self.unused_args:
            warnings.warn(
                "{} has no attribute '{}'".format(type(self), unused_arg),
                DraftsmanWarning,
                stacklevel=2,
            )

    # =========================================================================

    @property
    def switch_state(self):
        # type: () -> bool
        """
        Whether the switch is passing electricity or not. This is a manual
        setting that is overridden by the circuit or logistic condition.

        :getter: Gets the value of the switch state.
        :setter: Sets the value of the switch state.
        :type: ``bool``

        :exception TypeError: If set to anything other than a ``bool`` or ``None``.
        """
        return self._switch_state

    @switch_state.setter
    def switch_state(self, value):
        # type: (bool) -> None
        if value is None or isinstance(value, bool):
            self._switch_state = value
        else:
            raise TypeError("'switch_state' must be a bool or None")
