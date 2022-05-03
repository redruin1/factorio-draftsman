# fluid_wagon.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import OrientationMixin
from draftsman.warning import DraftsmanWarning

from draftsman.data.entities import fluid_wagons
from draftsman.data import entities

import warnings


class FluidWagon(OrientationMixin, Entity):
    """
    A train wagon that holds a fluid as cargo.
    """

    def __init__(self, name=fluid_wagons[0], **kwargs):
        # type: (str, **dict) -> None
        super(FluidWagon, self).__init__(name, fluid_wagons, **kwargs)

        if "collision_mask" in entities.raw[self.name]:  # pragma: no coverage
            self._collision_mask = set(entities.raw[self.name]["collision_mask"])
        else:  # pragma: no coverage
            self._collision_mask = {"train-layer"}

        for unused_arg in self.unused_args:
            warnings.warn(
                "{} has no attribute '{}'".format(type(self), unused_arg),
                DraftsmanWarning,
                stacklevel=2,
            )
