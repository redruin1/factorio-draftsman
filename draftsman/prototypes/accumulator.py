# accumulator.py

from draftsman.prototypes.mixins import (
    ControlBehaviorMixin, CircuitConnectableMixin, Entity
)
from draftsman.utils import signal_dict
from draftsman.warning import DraftsmanWarning

from draftsman.data.entities import accumulators

import warnings


class Accumulator(ControlBehaviorMixin, CircuitConnectableMixin, Entity):
    def __init__(self, name = accumulators[0], **kwargs):
        # type: (str, **dict) -> None
        super(Accumulator, self).__init__(name, accumulators, **kwargs)

        for unused_arg in self.unused_args:
            warnings.warn(
                "{} has no attribute '{}'".format(type(self), unused_arg),
                DraftsmanWarning,
                stacklevel = 2
            )

    def set_output_signal(self, signal):
        # type: (str) -> None
        """
        """
        if signal is None:
            self.control_behavior.pop("output_signal", None)
        else:
            self.control_behavior["output_signal"] = signal_dict(signal)