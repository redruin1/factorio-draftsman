# roboport.py

from draftsman.prototypes.mixins import (
    ControlBehaviorMixin, CircuitConnectableMixin, Entity
)
import draftsman.signatures as signatures
from draftsman.utils import signal_dict
from draftsman.warning import DraftsmanWarning

from draftsman.data.entities import roboports

import warnings


class Roboport(ControlBehaviorMixin, CircuitConnectableMixin, Entity):
    """
    """
    def __init__(self, name = roboports[0], **kwargs):
        # type: (str, **dict) -> None
        super(Roboport, self).__init__(name, roboports, **kwargs)

        for unused_arg in self.unused_args:
            warnings.warn(
                "{} has no attribute '{}'".format(type(self), unused_arg),
                DraftsmanWarning,
                stacklevel = 2
            )

    def set_read_logistics(self, value):
        # type: (bool) -> None
        """
        """
        if value is None:
            self.control_behavior.pop("read_logistics", None)
        else:
            value = signatures.BOOLEAN.validate(value)
            self.control_behavior["read_logistics"] = value

    def set_read_robot_stats(self, value):
        # type: (bool) -> None
        """
        """
        if value is None:
            self.control_behavior.pop("read_robot_stats", None)
        else:
            signatures.BOOLEAN.validate(value)
            self.control_behavior["read_robot_stats"] = value

    def set_available_logistics_signal(self, signal):
        # type: (str) -> None
        """
        """
        if signal is None:
            self.control_behavior.pop("available_logistic_output_signal", None)
        else:
            signal = signal_dict(signal)
            self.control_behavior["available_logistic_output_signal"] = signal

    def set_total_logistics_signal(self, signal):
        # type: (str) -> None
        """
        """
        if signal is None:
            self.control_behavior.pop("total_logistic_output_signal", None)
        else:
            signal = signal_dict(signal)
            self.control_behavior["total_logistic_output_signal"] = signal

    def set_available_construction_signal(self, signal):
        # type: (str) -> None
        """
        """
        if signal is None:
            self.control_behavior.pop("available_construction_output_signal", 
                                      None)
        else:
            signal = signal_dict(signal)
            self.control_behavior["available_construction_output_signal"]=signal

    def set_total_construction_signal(self, signal):
        # type: (str) -> None
        """
        """
        if signal is None:
            self.control_behavior.pop("total_construction_output_signal", None)
        else:
            signal = signal_dict(signal)
            self.control_behavior["total_construction_output_signal"] = signal