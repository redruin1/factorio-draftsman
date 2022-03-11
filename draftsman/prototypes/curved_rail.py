# curved_rail.py

from draftsman.prototypes.mixins import (
    DoubleGridAlignedMixin, EightWayDirectionalMixin, Entity
)
from draftsman.warning import DraftsmanWarning

from draftsman.data.entities import curved_rails

import warnings


class CurvedRail(DoubleGridAlignedMixin, EightWayDirectionalMixin, Entity):
    """
    """
    def __init__(self, name = curved_rails[0], **kwargs):
        # type: (str, **dict) -> None
        super(CurvedRail, self).__init__(name, curved_rails, **kwargs)

        for unused_arg in self.unused_args:
            warnings.warn(
                "{} has no attribute '{}'".format(type(self), unused_arg),
                DraftsmanWarning,
                stacklevel = 2
            )