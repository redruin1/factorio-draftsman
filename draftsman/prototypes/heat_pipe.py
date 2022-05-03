# heat_pipe.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.classes.entity import Entity
from draftsman.warning import DraftsmanWarning

from draftsman.data.entities import heat_pipes
from draftsman.data import entities

import warnings


class HeatPipe(Entity):
    """
    An entity used to transfer thermal energy.
    """

    def __init__(self, name=heat_pipes[0], **kwargs):
        # type: (str, **dict) -> None
        super(HeatPipe, self).__init__(name, heat_pipes, **kwargs)

        if "collision_mask" in entities.raw[self.name]:  # pragma: no coverage
            self._collision_mask = set(entities.raw[self.name]["collision_mask"])
        else:  # pragma: no coverage
            self._collision_mask = {"object-layer", "floor-layer", "water-tile"}

        for unused_arg in self.unused_args:
            warnings.warn(
                "{} has no attribute '{}'".format(type(self), unused_arg),
                DraftsmanWarning,
                stacklevel=2,
            )
