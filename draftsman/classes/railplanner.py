# railplanner.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.classes.entitylike import EntityLike
from draftsman.error import DraftsmanError

from draftsman.data import items


class RailPlanner(EntityLike):
    """
    Rail planner. Allows the user to specify rails in a pen-drawing or turtle-
    based manner. Currently unimplemented.
    """

    def __init__(self, name):
        if name in items.raw and items.raw[name]["type"] == "rail-planner":
            self.name = name
        else:
            raise DraftsmanError("'{}' is not a valid rail-planner")
        self.straight_rail = items.raw[name]["straight_rail"]
        self.curved_rail = items.raw[name]["curved_rail"]

        raise NotImplementedError

    def move_forward(amount=1):
        raise NotImplementedError

    def turn_left(amount=1):
        raise NotImplementedError

    def turn_right(amount=1):
        raise NotImplementedError
