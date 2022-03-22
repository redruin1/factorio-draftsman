# fluid_wagon.py

from draftsman.classes import Entity
from draftsman.classes.mixins import OrientationMixin
from draftsman.warning import DraftsmanWarning

from draftsman.data.entities import fluid_wagons

import warnings


class FluidWagon(OrientationMixin, Entity):
    """
    """
    def __init__(self, name = fluid_wagons[0], **kwargs):
        # type: (str, **dict) -> None
        super(FluidWagon, self).__init__(name, fluid_wagons, **kwargs)

        for unused_arg in self.unused_args:
            warnings.warn(
                "{} has no attribute '{}'".format(type(self), unused_arg),
                DraftsmanWarning,
                stacklevel = 2
            )