# furnace.py

from draftsman.prototypes.mixins import RequestItemsMixin, Entity
from draftsman.warning import DraftsmanWarning

from draftsman.data.entities import furnaces

import warnings


class Furnace(RequestItemsMixin, Entity):
    def __init__(self, name = furnaces[0], **kwargs):
        # type: (str, **dict) -> None
        super(Furnace, self).__init__(name, furnaces, **kwargs)

        for unused_arg in self.unused_args:
            warnings.warn(
                "{} has no attribute '{}'".format(type(self), unused_arg),
                DraftsmanWarning,
                stacklevel = 2
            )