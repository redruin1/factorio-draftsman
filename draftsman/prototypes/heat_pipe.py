# heat_pipe.py

from draftsman.prototypes.mixins import Entity
from draftsman.warning import DraftsmanWarning

from draftsman.data.entities import heat_pipes

import warnings


class HeatPipe(Entity):
    def __init__(self, name = heat_pipes[0], **kwargs):
        # type: (str, **dict) -> None
        super(HeatPipe, self).__init__(name, heat_pipes, **kwargs)

        for unused_arg in self.unused_args:
            warnings.warn(
                "{} has no attribute '{}'".format(type(self), unused_arg),
                DraftsmanWarning,
                stacklevel = 2
            )