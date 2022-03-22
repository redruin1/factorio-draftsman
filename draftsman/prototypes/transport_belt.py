# transport_belt.py

from draftsman.classes import Entity
from draftsman.classes.mixins import (
    CircuitReadContentsMixin, LogisticConditionMixin, CircuitConditionMixin,
    EnableDisableMixin, ControlBehaviorMixin, CircuitConnectableMixin,
    DirectionalMixin
)
from draftsman.warning import DraftsmanWarning

from draftsman.data.entities import transport_belts

import warnings


class TransportBelt(CircuitReadContentsMixin, LogisticConditionMixin, 
                    CircuitConditionMixin, EnableDisableMixin, 
                    ControlBehaviorMixin, CircuitConnectableMixin, 
                    DirectionalMixin, Entity):
    """
    """
    def __init__(self, name = transport_belts[0], **kwargs):
        # type: (str, **dict) -> None
        super(TransportBelt, self).__init__(name, transport_belts, **kwargs)

        for unused_arg in self.unused_args:
            warnings.warn(
                "{} has no attribute '{}'".format(type(self), unused_arg),
                DraftsmanWarning,
                stacklevel = 2
            )