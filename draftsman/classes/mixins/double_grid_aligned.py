# double_grid_aligned.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.warning import RailAlignmentWarning

import math
from typing import Union
import warnings


class DoubleGridAlignedMixin(object):
    """
    Makes the Entity issue warnings if set to an odd tile-position coordinate.
    Sets the ``double_grid_aligned`` attribute to ``True``.
    """

    def __init__(self, name, similar_entities, **kwargs):
        # type: (str, list[str], **dict) -> None
        super(DoubleGridAlignedMixin, self).__init__(name, similar_entities, **kwargs)

        self._double_grid_aligned = True

    # =========================================================================

    @property
    def position(self):
        # type: () -> dict
        """
        The "canonical" position of the Entity, or the one that Factorio uses.
        Positions of most entities are located at their center, which can either
        be in the middle of a tile or on it's transition, depending on the
        Entity's ``tile_width`` and ``tile_height``.

        ``position`` can be specified as a ``dict`` with ``"x"`` and ``"y"``
        keys, or more succinctly as a sequence of floats, usually a ``list`` or
        ``tuple``.

        This property is updated in tandem with ``tile_position``, so using them
        both interchangeably is both allowed and encouraged.

        Raises :py:class:`~draftsman.warning.RailAlignmentWarning` if the x or y
        position is odd.

        :getter: Gets the position of the Entity.
        :setter: Sets the position of the Entity.
        :type: ``dict{"x": float, "y": float}``

        :exception IndexError: If the set value does not match the above
            specification.
        :exception DraftsmanError: If the entities position is modified when
            inside a EntityCollection, :ref:`which is forbidden.
            <handbook.blueprints.forbidden_entity_attributes>`
        """
        return self._position

    @position.setter
    def position(self, value):
        # type: (Union[dict, list, tuple]) -> None

        # Call Entity's position property setter
        super(DoubleGridAlignedMixin, type(self)).position.fset(self, value)

        # if the grid alignment is off, warn the user
        if self._tile_position["x"] % 2 == 1 or self._tile_position["y"] % 2 == 1:
            cast_position = [
                math.floor(self._tile_position["x"] / 2) * 2,
                math.floor(self._tile_position["y"] / 2) * 2,
            ]
            warnings.warn(
                "Double-grid aligned entity is not placed along chunk grid; "
                "entity's position will be cast from {} to {} when imported".format(
                    self._tile_position, cast_position
                ),
                RailAlignmentWarning,
                stacklevel=2,
            )

    # =========================================================================

    @property
    def tile_position(self):
        # type: () -> dict
        """
        The tile-position of the Entity. The tile position is the position
        according the the LuaSurface tile grid, and is the top left corner of
        the top-leftmost tile of the Entity.

        ``tile_position`` can be specified as a ``dict`` with ``"x"`` and
        ``"y"`` keys, or more succinctly as a sequence of floats, usually a
        ``list`` or ``tuple``.

        This property is updated in tandem with ``position``, so using them both
        interchangeably is both allowed and encouraged.

        Raises :py:class:`~draftsman.warning.RailAlignmentWarning` if the x or y
        position is odd.

        :getter: Gets the tile position of the Entity.
        :setter: Sets the tile position of the Entity.
        :type: ``dict{"x": int, "y": int}``

        :exception IndexError: If the set value does not match the above
            specification.
        :exception DraftsmanError: If the entities position is modified when
            inside a EntityCollection, :ref:`which is forbidden.
            <handbook.blueprints.forbidden_entity_attributes>`
        """
        return self._tile_position

    @tile_position.setter
    def tile_position(self, value):
        # type: (Union[dict, list, tuple]) -> None

        # Call Entity's tile_position property setter
        super(DoubleGridAlignedMixin, type(self)).tile_position.fset(self, value)

        # if the grid alignment is off, warn the user
        if self._tile_position["x"] % 2 == 1 or self._tile_position["y"] % 2 == 1:
            cast_position = [
                math.floor(self._tile_position["x"] / 2) * 2,
                math.floor(self._tile_position["y"] / 2) * 2,
            ]
            warnings.warn(
                "Double-grid aligned entity is not placed along chunk grid; "
                "entity's position will be cast from {} to {} when imported".format(
                    self._tile_position, cast_position
                ),
                RailAlignmentWarning,
                stacklevel=2,
            )
