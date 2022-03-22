# cargo_wagon.py

from draftsman.classes import Entity
from draftsman.classes.mixins import InventoryFilterMixin, OrientationMixin
from draftsman.warning import DraftsmanWarning

from draftsman.data.entities import cargo_wagons

import warnings


class CargoWagon(InventoryFilterMixin, OrientationMixin, Entity):
    """
    """
    def __init__(self, name = cargo_wagons[0], **kwargs):
        # type: (str, **dict) -> None
        super(CargoWagon, self).__init__(name, cargo_wagons, **kwargs)

        for unused_arg in self.unused_args:
            warnings.warn(
                "{} has no attribute '{}'".format(type(self), unused_arg),
                DraftsmanWarning,
                stacklevel = 2
            )