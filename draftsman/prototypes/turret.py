# turret.py

from draftsman.prototypes.mixins import DirectionalMixin, Entity
from draftsman.warning import DraftsmanWarning

from draftsman.data.entities import turrets

import warnings


class Turret(DirectionalMixin, Entity):
    def __init__(self, name = turrets[0], **kwargs):
        # type: (str, **dict) -> None
        super(Turret, self).__init__(name, turrets, **kwargs)

        for unused_arg in self.unused_args:
            warnings.warn(
                "{} has no attribute '{}'".format(type(self), unused_arg),
                DraftsmanWarning,
                stacklevel = 2
            )