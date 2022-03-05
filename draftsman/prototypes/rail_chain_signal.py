# rail_chain_signal.py

from draftsman.prototypes.mixins import (
    ReadRailSignalMixin, ControlBehaviorMixin, CircuitConnectableMixin, 
    EightWayDirectionalMixin, Entity
)
from draftsman.errors import InvalidEntityID
from draftsman.utils import warn_user, signal_dict

from draftsman.data.entities import rail_chain_signals


class RailChainSignal(ReadRailSignalMixin, ControlBehaviorMixin, 
                      CircuitConnectableMixin, EightWayDirectionalMixin, 
                      Entity):
    """
    """
    def __init__(self, name: str = rail_chain_signals[0], **kwargs):
        if name not in rail_chain_signals:
            raise InvalidEntityID("'{}' is not a valid name for this type"
                                  .format(name))
        super(RailChainSignal, self).__init__(name, **kwargs)

        for unused_arg in self.unused_args:
            warn_user("{} has no attribute '{}'".format(type(self), unused_arg))
    
    def set_blue_output_signal(self, signal: str) -> None:
        """
        """
        if signal is None:
            self.control_behavior.pop("blue_output_signal", None)
        else:
            self.control_behavior["blue_output_signal"] = signal_dict(signal)