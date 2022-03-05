# accumulator.py

from draftsman.prototypes.mixins import (
    ControlBehaviorMixin, CircuitConnectableMixin, Entity
)
from draftsman.errors import InvalidEntityID
from draftsman.utils import warn_user, signal_dict

from draftsman.data.entities import accumulators


class Accumulator(ControlBehaviorMixin, CircuitConnectableMixin, Entity):
    def __init__(self, name: str = accumulators[0], **kwargs):
        if name not in accumulators:
            raise InvalidEntityID("'{}' is not a valid name for this type"
                                  .format(name))
        super(Accumulator, self).__init__(name, **kwargs)

        for unused_arg in self.unused_args:
            warn_user("{} has no attribute '{}'".format(type(self), unused_arg))

    def set_output_signal(self, signal: str) -> None:
        """
        """
        if signal is None:
            self.control_behavior.pop("output_signal", None)
        else:
            self.control_behavior["output_signal"] = signal_dict(signal)