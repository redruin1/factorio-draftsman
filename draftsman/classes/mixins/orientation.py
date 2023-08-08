# orientation.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.classes.collision_set import CollisionSet
from draftsman.constants import Orientation
from draftsman.warning import ValueWarning
from draftsman.utils import Rectangle

import warnings

from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no coverage
    from draftsman.classes.entity import Entity


class OrientationMixin(object):
    """
    Used in trains and wagons to specify their direction.
    """

    _exports = {
        "orientation": {
            "format": "float[0.0, 1.0]",
            "description": "The floating point rotation of the entity",
            "required": lambda x: x is not None and x != 0,
        }
    }

    def __init__(self, name, similar_entities, **kwargs):
        # type: (str, list[str], **dict) -> None
        super(OrientationMixin, self).__init__(name, similar_entities, **kwargs)

        old = self._collision_set.shapes[0]
        width = old.bot_right[0] - old.top_left[0]
        height = old.bot_right[1] - old.top_left[1]

        # Need to make a per-instance copy
        self._collision_set = CollisionSet([Rectangle((0, 0), width, height, 0)])

        self.orientation = 0.0
        if "orientation" in kwargs:
            self.orientation = kwargs["orientation"]
            self.unused_args.pop("orientation")
        # self._add_export("orientation", lambda x: x is not None and x != 0)

    # =========================================================================

    @property
    def orientation(self):
        # type: () -> Orientation
        """
        The angle that the current Entity is facing, expressed as a ``float``
        in the range ``[0.0, 1.0)``, where ``0.0`` is North and increases
        clockwise. TODO: update

        Raises :py:class:`.ValueWarning` if set to a value not in the range
        ``[0.0, 1.0)``.

        .. NOTE::

            This is distinct from ``direction``, which is used on grid-aligned
            entities and can only be a max of 8 possible rotations.

        :getter: Gets the orientation of the Entity.
        :setter: Sets the orientation of the Entity.
        :type: ``float``

        :exception TypeError: If set to anything other than a ``float`` or
            ``None``.
        """
        return self._orientation

    @orientation.setter
    def orientation(self, value):
        # type: (Orientation) -> None
        if value is None:
            self._orientation = value
            self._collision_set.shapes[0].angle = 0
        elif isinstance(value, (float, int)):
            self._orientation = Orientation(value % 1.0)
            self._collision_set.shapes[0].angle = (value % 1.0) * 360.0
            # TODO: what if orientation changes when inside a EntityCollection?
            # Might end up intersecting neigbouring entities
        else:
            raise TypeError("'orientation' must be a float or None")

    def mergable_with(self, other):
        # type: (Entity) -> bool
        base_mergable = super(OrientationMixin, self).mergable_with(other)
        return base_mergable and self.orientation == other.orientation
