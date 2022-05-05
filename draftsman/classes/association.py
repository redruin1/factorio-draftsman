# association.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.classes.entity import Entity

import copy
import weakref


class Association(weakref.ref):
    """
    A loose wrapper around weakref that permits deepcopying. Leads to better
    memory management and better displaying.
    """

    def __init__(self, item):
        # type: (Entity) -> None
        if not isinstance(item, Entity):
            raise TypeError("cannot create association to a non-Entity")

        super(Association, self).__init__(item)

    def __deepcopy__(self, memo):
        # type: (dict) -> Association
        entity_copy = copy.deepcopy(self(), memo)
        entity = memo.get(id(entity_copy), entity_copy)
        if entity is None:
            return None
        else:
            return Association(entity)

    def __repr__(self):  # pragma: no coverage
        # type: () -> str
        if self() is None:
            return "None"

        return "<Association to {}{}>".format(
            type(self()).__name__,
            " with id '{}'".format(self().id) if self().id is not None else "",
        )
