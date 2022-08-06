# association.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

import copy
import weakref

from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no coverage
    from draftsman.classes.entity import Entity


class Association(weakref.ref):
    """
    A loose wrapper around weakref that permits deepcopying. Used to represent
    wire and circuit connections, as well as associating train entities with
    specific schedules. Leads to better memory management and better displaying.
    """

    def __init__(self, item):
        # type: (Entity) -> None
        # if not isinstance(item, Entity):
        #     raise TypeError("cannot create association to a non-Entity")

        super(Association, self).__init__(item)

    def __deepcopy__(self, memo):
        return self

    # def __deepcopy__(self, memo):
    #     # type: (dict) -> Association
    #     entity = memo.get(id(self()), copy.deepcopy(self(), memo))
    #     #print(entity.id)
    #     if entity is None:
    #         return None
    #     else:
    #         result = Association(entity)
    #         memo[id(self)] = result
    #         return result

    def __repr__(self):  # pragma: no coverage
        # type: () -> str
        if self() is None:
            return "<Association to None>"

        return "<Association to {0} at 0x{1:016X}>".format(
            type(self()).__name__,
            id(self()),
        )
