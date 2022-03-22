# land_mine.py

from draftsman.classes import Entity
from draftsman.warning import DraftsmanWarning

from draftsman.data.entities import land_mines

import warnings


class LandMine(Entity):
    def __init__(self, name = land_mines[0], **kwargs):
        # type: (str, **dict) -> None
        super(LandMine, self).__init__(name, land_mines, **kwargs)

        for unused_arg in self.unused_args:
            warnings.warn(
                "{} has no attribute '{}'".format(type(self), unused_arg),
                DraftsmanWarning,
                stacklevel = 2
            )