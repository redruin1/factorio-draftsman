# rail_signal.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import (
    ReadRailSignalMixin,
    CircuitConditionMixin,
    EnableDisableMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    EightWayDirectionalMixin,
)
import draftsman.signatures as signatures
from draftsman.warning import DraftsmanWarning

from draftsman.data.entities import rail_signals
from draftsman.data import entities

import warnings


class RailSignal(
    ReadRailSignalMixin,
    CircuitConditionMixin,
    EnableDisableMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    EightWayDirectionalMixin,
    Entity,
):
    """
    A rail signal that determines whether or not trains can pass along their
    rail block.
    """

    def __init__(self, name=rail_signals[0], **kwargs):
        # type: (str, **dict) -> None
        super(RailSignal, self).__init__(name, rail_signals, **kwargs)

        if "collision_mask" in entities.raw[self.name]:  # pragma: no coverage
            self._collision_mask = set(entities.raw[self.name]["collision_mask"])
        else:  # pragma: no coverage
            self._collision_mask = {"floor-layer", "rail-layer", "item-layer"}

        for unused_arg in self.unused_args:
            warnings.warn(
                "{} has no attribute '{}'".format(type(self), unused_arg),
                DraftsmanWarning,
                stacklevel=2,
            )

    # =========================================================================

    @property
    def read_signal(self):
        # type: () -> bool
        """
        Whether or not to read the state of the rail signal as their output
        signals.

        :getter: Gets whether or not to read the signal, or ``None`` if not set.
        :setter: Sets whether or not to read the signal. Removes the key if set
            to ``None``.
        :type: ``bool``

        :exception TypeError: If set to anything other than a ``bool`` or ``None``.
        """
        return self.control_behavior.get("circuit_read_signal", None)

    @read_signal.setter
    def read_signal(self, value):
        # type: (bool) -> None
        if value is None:
            self.control_behavior.pop("circuit_read_signal", None)
        elif isinstance(value, bool):
            self.control_behavior["circuit_read_signal"] = value
        else:
            raise TypeError("'read_signal' must be a bool or None")

    # =========================================================================

    @property
    def enable_disable(self):
        # type: () -> bool
        return self.control_behavior.get("circuit_close_signal", None)

    @enable_disable.setter
    def enable_disable(self, value):
        # type: (bool) -> None
        if value is None:
            self.control_behavior.pop("circuit_close_signal", None)
        elif isinstance(value, bool):
            self.control_behavior["circuit_close_signal"] = value
        else:
            raise TypeError("'enable_disable' must be a bool or None")

    # =========================================================================

    # def on_insert(self, parent):
    #     # Check if the rail_signal is adjacent to a rail
    #     # This test has to be more sophisticated than just testing for adjacent
    #     # entities; we also must consider the orientation of signal to ensure
    #     # it is facing the correct direction (must be on the right side of the
    #     # track, unless there exists another signal on the opposite side)
    #     pass
