# gate.py

from draftsman.prototypes.mixins import DirectionalMixin, Entity
from draftsman.warning import DraftsmanWarning

from draftsman.data.entities import gates

import warnings


class Gate(DirectionalMixin, Entity):
    def __init__(self, name = gates[0], **kwargs):
        # type: (str, **dict) -> None
        super(Gate, self).__init__(name, gates, **kwargs)

        for unused_arg in self.unused_args:
            warnings.warn(
                "{} has no attribute '{}'".format(type(self), unused_arg),
                DraftsmanWarning,
                stacklevel = 2
            )