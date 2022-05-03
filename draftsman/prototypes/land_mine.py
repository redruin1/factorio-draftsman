# land_mine.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.classes.entity import Entity
from draftsman.warning import DraftsmanWarning

from draftsman.data.entities import land_mines
from draftsman.data import entities

import warnings


class LandMine(Entity):
    """
    An entity that explodes when in proximity to another force.
    """

    def __init__(self, name=land_mines[0], **kwargs):
        # type: (str, **dict) -> None
        super(LandMine, self).__init__(name, land_mines, **kwargs)

        if "collision_mask" in entities.raw[self.name]:  # pragma: no coverage
            self._collision_mask = set(entities.raw[self.name]["collision_mask"])
        else:  # pragma: no coverage
            self._collision_mask = {"object-layer", "water-tile"}

        for unused_arg in self.unused_args:
            warnings.warn(
                "{} has no attribute '{}'".format(type(self), unused_arg),
                DraftsmanWarning,
                stacklevel=2,
            )
