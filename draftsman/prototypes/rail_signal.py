# rail_signal.py

from draftsman.classes import Entity
from draftsman.classes.mixins import (
    ReadRailSignalMixin, CircuitConditionMixin, EnableDisableMixin,
    ControlBehaviorMixin, CircuitConnectableMixin, EightWayDirectionalMixin,
)
import draftsman.signatures as signatures
from draftsman.warning import DraftsmanWarning

from draftsman.data.entities import rail_signals

import warnings


class RailSignal(ReadRailSignalMixin, CircuitConditionMixin, EnableDisableMixin, 
                 ControlBehaviorMixin, CircuitConnectableMixin, 
                 EightWayDirectionalMixin, Entity):
    """
    """
    def __init__(self, name = rail_signals[0], **kwargs):
        # type: (str, **dict) -> None
        super(RailSignal, self).__init__(name, rail_signals, **kwargs)

        for unused_arg in self.unused_args:
            warnings.warn(
                "{} has no attribute '{}'".format(type(self), unused_arg),
                DraftsmanWarning,
                stacklevel = 2
            )

    # =========================================================================

    @property
    def read_signal(self):
        # type: () -> bool
        """
        TODO
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
        """
        TODO: write (overwritten)
        """
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

    # def set_read_signal(self, value):
    #     # type: (bool) -> None
    #     """
    #     """
    #     if value is None:
    #         self.control_behavior.pop("circuit_read_signal", None)
    #     else:
    #         value = signatures.BOOLEAN.validate(value)
    #         self.control_behavior["circuit_read_signal"] = value

    # def set_enable_disable(self, value):
    #     # type: (bool) -> None
    #     """
    #     TODO: write (overwritten)
    #     """
    #     if value is None:
    #         self.control_behavior.pop("circuit_close_signal", None)
    #     else:
    #         value = signatures.BOOLEAN.validate(value)
    #         self.control_behavior["circuit_close_signal"] = value