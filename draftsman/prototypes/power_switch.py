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
from draftsman.error import DataFormatError
from draftsman import signatures
from draftsman.warning import DraftsmanWarning

from draftsman.data.entities import power_switches

from schema import SchemaError
import six
from typing import ClassVar
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

    # fmt: off
    # _exports = {
    #     **Entity._exports,
    #     **DirectionalMixin._exports,
    #     **PowerConnectableMixin._exports,
    #     **CircuitConnectableMixin._exports,
    #     **ControlBehaviorMixin._exports,
    #     **LogisticConditionMixin._exports,
    #     **CircuitConditionMixin._exports,
    #     "switch_state": {
    #         "format": "bool",
    #         "description": "The 'default' state of the switch (overridden by logistic or circuit conditions)",
    #         "required": lambda x: x is not None,
    #     },
    # }
    # fmt: on
    class Format(
        CircuitConditionMixin.Format,
        LogisticConditionMixin.Format,
        ControlBehaviorMixin.Format,
        CircuitConnectableMixin.Format,
        PowerConnectableMixin.Format,
        DirectionalMixin.Format,
        Entity.Format,
    ):
        class ControlBehavior(
            CircuitConditionMixin.ControlFormat,
            LogisticConditionMixin.ControlFormat,
        ):
            pass

        control_behavior: ClassVar[ControlBehavior | None] = None

        switch_state: bool | None = None

    def __init__(self, name=power_switches[0], **kwargs):
        # type: (str, **dict) -> None
        super(PowerSwitch, self).__init__(name, power_switches, **kwargs)

        self._dual_power_connectable = True

        self.switch_state = None
        if "switch_state" in kwargs:
            self.switch_state = kwargs["switch_state"]
            self.unused_args.pop("switch_state")
        # self._add_export("switch_state", lambda x: x is not None)

        for unused_arg in self.unused_args:
            warnings.warn(
                "{} has no attribute '{}'".format(type(self), unused_arg),
                DraftsmanWarning,
                stacklevel=2,
            )

        del self.unused_args

    # =========================================================================

    # @ControlBehaviorMixin.control_behavior.setter
    # def control_behavior(self, value):
    #     # type: (dict) -> None
    #     try:
    #         self._control_behavior = signatures.POWER_SWITCH_CONTROL_BEHAVIOR.validate(
    #             value
    #         )
    #     except SchemaError as e:
    #         six.raise_from(DataFormatError(e), None)

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
        return self._root.get("switch_state", None)

    @switch_state.setter
    def switch_state(self, value):
        # type: (bool) -> None
        if value is None:
            self._root.pop("switch_state", None)
        else:
            self._root["switch_state"] = value

    def merge(self, other):
        # type: (PowerSwitch) -> None
        super(PowerSwitch, self).merge(other)

        self.switch_state = other.switch_state

    # =========================================================================

    __hash__ = Entity.__hash__

    def __eq__(self, other) -> bool:
        return super().__eq__(other) and self.switch_state == other.switch_state
