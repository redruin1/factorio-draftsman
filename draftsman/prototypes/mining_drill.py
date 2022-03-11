# mining_drill.py

from draftsman.prototypes.mixins import (
    RequestItemsMixin, CircuitReadResourceMixin, CircuitConditionMixin,
    EnableDisableMixin, LogisticConditionMixin, ControlBehaviorMixin,
    CircuitConnectableMixin, DirectionalMixin, Entity
)
from draftsman.warning import DraftsmanWarning

from draftsman.data.entities import mining_drills

import warnings


class MiningDrill(RequestItemsMixin, CircuitReadResourceMixin, 
                  CircuitConditionMixin, EnableDisableMixin, 
                  LogisticConditionMixin, ControlBehaviorMixin, 
                  CircuitConnectableMixin, DirectionalMixin, Entity, object):
    def __init__(self, name = mining_drills[0], **kwargs):
        # type: (str, **dict) -> None
        super(MiningDrill, self).__init__(name, mining_drills, **kwargs)

        for unused_arg in self.unused_args:
            warnings.warn(
                "{} has no attribute '{}'".format(type(self), unused_arg),
                DraftsmanWarning,
                stacklevel = 2
            )