# rail_chain_signal.py

from draftsman.prototypes.mixins import (
    ReadRailSignalMixin, ControlBehaviorMixin, CircuitConnectableMixin, 
    EightWayDirectionalMixin, Entity
)
from draftsman.utils import signal_dict
from draftsman.warning import DraftsmanWarning

from draftsman.data.entities import rail_chain_signals

import warnings


class RailChainSignal(ReadRailSignalMixin, ControlBehaviorMixin, 
                      CircuitConnectableMixin, EightWayDirectionalMixin, 
                      Entity):
    """
    """
    def __init__(self, name = rail_chain_signals[0], **kwargs):
        # type: (str, **dict) -> None
        super(RailChainSignal, self).__init__(
            name, rail_chain_signals, **kwargs
        )

        for unused_arg in self.unused_args:
            warnings.warn(
                "{} has no attribute '{}'".format(type(self), unused_arg),
                DraftsmanWarning,
                stacklevel = 2
            )
    
    def set_blue_output_signal(self, signal):
        # type: (str) -> None
        """
        """
        if signal is None:
            self.control_behavior.pop("blue_output_signal", None)
        else:
            self.control_behavior["blue_output_signal"] = signal_dict(signal)