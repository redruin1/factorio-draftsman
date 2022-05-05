# linked_belt.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import DirectionalMixin
from draftsman.error import DraftsmanError
from draftsman.warning import DraftsmanWarning

from draftsman.data.entities import linked_belts
from draftsman.data import entities

import warnings

try:  # pragma: no coverage
    default_linked_belt = linked_belts[0]
except IndexError:  # pragma: no coverage
    default_linked_belt = None


class LinkedBelt(DirectionalMixin, Entity):
    """
    A belt object that can transfer items over any distance, regardless of
    constraint, as long as the two are paired together.

    .. WARNING::

        Functionally, currently unimplemented. Need to analyze how mods use this
        entity, as I can't seem to figure out the example one in the game.
    """

    def __init__(self, name=default_linked_belt, **kwargs):
        # type: (str, **dict) -> None
        if len(linked_belts) == 0:  # pragma: no coverage
            raise DraftsmanError("There is no LinkedBelt to create")

        super(LinkedBelt, self).__init__(name, linked_belts, **kwargs)

        if "collision_mask" in entities.raw[self.name]:  # pragma: no coverage
            self._collision_mask = set(entities.raw[self.name]["collision_mask"])
        else:  # pragma: no coverage
            self._collision_mask = {
                "object-layer",
                "item-layer",
                "transport-belt-layer",
                "water-tile",
            }

        for unused_arg in self.unused_args:
            warnings.warn(
                "{} has no attribute '{}'".format(type(self), unused_arg),
                DraftsmanWarning,
                stacklevel=2,
            )
