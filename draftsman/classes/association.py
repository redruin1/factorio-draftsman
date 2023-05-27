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

        super(Association, self).__init__(item)

    def __eq__(self, other):
        # type: (Association) -> bool
        """
        Checking the equality of two associations checks to make sure that they
        point to the exact same entity in memory, which is important for entity
        resolution. However, entity comparisons themselves are on a per value
        basis. For example:

        .. code-block:: python

            entity1 = Container()
            entity2 = Container()
            # Both entities are "value-equivalent"
            assert entity1 == entity2
            # But they exist in different places in memory (entity1 is not entity2)
            assert Association(entity1) != Association(entity2)
        """
        return self() is other()  # TODO: think about

    def __deepcopy__(self, _):
        # type: (dict) -> Association
        return self

    def __repr__(self):  # pragma: no coverage
        # type: () -> str
        if self() is None:
            return "<Association to None>"

        return "<Association to {0} at 0x{1:016X}>".format(
            type(self()).__name__,
            id(self()),
        )
