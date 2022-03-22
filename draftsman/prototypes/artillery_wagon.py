# artillery_wagon.py

from draftsman.classes import Entity
from draftsman.classes.mixins import OrientationMixin
from draftsman.warning import DraftsmanWarning

from draftsman.data.entities import artillery_wagons

import warnings


class ArtilleryWagon(OrientationMixin, Entity):
    """
    """
    def __init__(self, name = artillery_wagons[0], **kwargs):
        # type: (str, **dict) -> None
        super(ArtilleryWagon, self).__init__(name, artillery_wagons, **kwargs)

        for unused_arg in self.unused_args:
            warnings.warn(
                "{} has no attribute '{}'".format(type(self), unused_arg),
                DraftsmanWarning,
                stacklevel = 2
            )