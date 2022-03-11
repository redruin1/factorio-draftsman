# lamp.py

from draftsman.prototypes.mixins import (
    CircuitConditionMixin, ControlBehaviorMixin, CircuitConnectableMixin, Entity
)
import draftsman.signatures as signatures
from draftsman.warning import DraftsmanWarning

from draftsman.data.entities import lamps

import warnings


class Lamp(CircuitConditionMixin, ControlBehaviorMixin, CircuitConnectableMixin,
           Entity):
    """
    """
    def __init__(self, name = lamps[0], **kwargs):
        # type: (str, **dict) -> None
        super(Lamp, self).__init__(name, lamps, **kwargs)

        for unused_arg in self.unused_args:
            warnings.warn(
                "{} has no attribute '{}'".format(type(self), unused_arg),
                DraftsmanWarning,
                stacklevel = 2
            )

    def set_use_colors(self, value):
        # type: (bool) -> None
        """
        """
        if value is None:
            self.control_behavior.pop("use_colors", None)
        else:
            value = signatures.BOOLEAN.validate(value)
            self.control_behavior["use_colors"] = value