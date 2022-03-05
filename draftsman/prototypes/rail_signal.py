# rail_signal.py

from draftsman.prototypes.mixins import (
    ReadRailSignalMixin, CircuitConditionMixin, EnableDisableMixin,
    ControlBehaviorMixin, CircuitConnectableMixin, EightWayDirectionalMixin,
    Entity
)
from draftsman.errors import InvalidEntityID
from draftsman.utils import warn_user
import draftsman.signatures as signatures

from draftsman.data.entities import rail_signals


class RailSignal(ReadRailSignalMixin, CircuitConditionMixin, EnableDisableMixin, 
                 ControlBehaviorMixin, CircuitConnectableMixin, 
                 EightWayDirectionalMixin, Entity):
    """
    """
    def __init__(self, name: str = rail_signals[0], **kwargs):
        if name not in rail_signals:
            raise InvalidEntityID("'{}' is not a valid name for this type"
                                  .format(name))
        super(RailSignal, self).__init__(name, **kwargs)

        for unused_arg in self.unused_args:
            warn_user("{} has no attribute '{}'".format(type(self), unused_arg))

    def set_read_signal(self, value: bool) -> None:
        """
        """
        if value is None:
            self.control_behavior.pop("circuit_read_signal", None)
        else:
            value = signatures.BOOLEAN.validate(value)
            self.control_behavior["circuit_read_signal"] = value

    def set_enable_disable(self, value: bool) -> None:
        """
        TODO: write (overwritten)
        """
        if value is None:
            self.control_behavior.pop("circuit_close_signal", None)
        else:
            value = signatures.BOOLEAN.validate(value)
            self.control_behavior["circuit_close_signal"] = value