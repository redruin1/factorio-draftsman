# underground_belt.py

from draftsman.prototypes.mixins import IOTypeMixin, DirectionalMixin, Entity
from draftsman.warning import DraftsmanWarning

from draftsman.data.entities import underground_belts

import warnings

class UndergroundBelt(IOTypeMixin, DirectionalMixin, Entity):
    """
    """
    def __init__(self, name = underground_belts[0], **kwargs):
        # type: (str, **dict) -> None
        super(UndergroundBelt, self).__init__(name, underground_belts, **kwargs)

        for unused_arg in self.unused_args:
            warnings.warn(
                "{} has no attribute '{}'".format(type(self), unused_arg),
                DraftsmanWarning,
                stacklevel = 2
            )