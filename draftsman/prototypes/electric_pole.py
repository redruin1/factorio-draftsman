# electric_pole.py

from draftsman.prototypes.mixins import (
    CircuitConnectableMixin, PowerConnectableMixin, Entity
)
from draftsman.warning import DraftsmanWarning

from draftsman.data.entities import electric_poles

import warnings


class ElectricPole(CircuitConnectableMixin, PowerConnectableMixin, Entity):
    """
    """
    def __init__(self, name = electric_poles[0], **kwargs):
        # type: (str, **dict) -> None
        super(ElectricPole, self).__init__(name, electric_poles, **kwargs)

        for unused_arg in self.unused_args:
            warnings.warn(
                "{} has no attribute '{}'".format(type(self), unused_arg),
                DraftsmanWarning,
                stacklevel = 2
            )