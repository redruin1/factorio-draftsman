# roboport.py

from draftsman.prototypes.mixins import (
    ControlBehaviorMixin, CircuitConnectableMixin, Entity
)
from draftsman.errors import InvalidEntityID
from draftsman.utils import warn_user, signal_dict
import draftsman.signatures as signatures

from draftsman.data.entities import roboports


class Roboport(ControlBehaviorMixin, CircuitConnectableMixin, Entity):
    """
    """
    def __init__(self, name: str = roboports[0], **kwargs):
        if name not in roboports:
            raise InvalidEntityID("'{}' is not a valid name for this type"
                                  .format(name))
        super(Roboport, self).__init__(name, **kwargs)

        for unused_arg in self.unused_args:
            warn_user("{} has no attribute '{}'".format(type(self), unused_arg))

    def set_read_logistics(self, value: bool) -> None:
        """
        """
        if value is None:
            self.control_behavior.pop("read_logistics", None)
        else:
            value = signatures.BOOLEAN.validate(value)
            self.control_behavior["read_logistics"] = value

    def set_read_robot_stats(self, value: bool) -> None:
        """
        """
        if value is None:
            self.control_behavior.pop("read_robot_stats", None)
        else:
            signatures.BOOLEAN.validate(value)
            self.control_behavior["read_robot_stats"] = value

    def set_available_logistics_signal(self, signal: str) -> None:
        """
        """
        if signal is None:
            self.control_behavior.pop("available_logistic_output_signal", None)
        else:
            signal = signal_dict(signal)
            self.control_behavior["available_logistic_output_signal"] = signal

    def set_total_logistics_signal(self, signal: str) -> None:
        """
        """
        if signal is None:
            self.control_behavior.pop("total_logistic_output_signal", None)
        else:
            signal = signal_dict(signal)
            self.control_behavior["total_logistic_output_signal"] = signal

    def set_available_construction_signal(self, signal: str) -> None:
        """
        """
        if signal is None:
            self.control_behavior.pop("available_construction_output_signal", 
                                      None)
        else:
            signal = signal_dict(signal)
            self.control_behavior["available_construction_output_signal"]=signal

    def set_total_construction_signal(self, signal: str) -> None:
        """
        """
        if signal is None:
            self.control_behavior.pop("total_construction_output_signal", None)
        else:
            signal = signal_dict(signal)
            self.control_behavior["total_construction_output_signal"] = signal