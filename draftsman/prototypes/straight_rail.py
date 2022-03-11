# straight_rail.py

from draftsman.prototypes.mixins import (
    DoubleGridAlignedMixin, EightWayDirectionalMixin, Entity
)
from draftsman.warning import DraftsmanWarning

from draftsman.data.entities import straight_rails

import warnings


class StraightRail(DoubleGridAlignedMixin, EightWayDirectionalMixin, Entity):
    """
    """
    def __init__(self, name = straight_rails[0], **kwargs):
        # type: (str, **dict) -> None
        super(StraightRail, self).__init__(name, straight_rails, **kwargs)

        for unused_arg in self.unused_args:
            warnings.warn(
                "{} has no attribute '{}'".format(type(self), unused_arg),
                DraftsmanWarning,
                stacklevel = 2
            )