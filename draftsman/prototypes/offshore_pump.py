# offshore_pump.py

from draftsman.prototypes.mixins import (
    CircuitConditionMixin, LogisticConditionMixin, ControlBehaviorMixin,
    CircuitConnectableMixin, DirectionalMixin, Entity
)
from draftsman.warning import DraftsmanWarning

from draftsman.data.entities import offshore_pumps

import warnings


class OffshorePump(CircuitConditionMixin, LogisticConditionMixin, 
                   ControlBehaviorMixin, CircuitConnectableMixin, 
                   DirectionalMixin, Entity):
    def __init__(self, name = offshore_pumps[0], **kwargs):
        # type: (str, **dict) -> None
        super(OffshorePump, self).__init__(name, offshore_pumps, **kwargs)

        for unused_arg in self.unused_args:
            warnings.warn(
                "{} has no attribute '{}'".format(type(self), unused_arg),
                DraftsmanWarning,
                stacklevel = 2
            )