# elevated_half_diagonal_rail.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import DirectionalMixin
from draftsman.constants import Direction, EIGHT_WAY_DIRECTIONS
from draftsman.prototypes.half_diagonal_rail import HalfDiagonalRail

from draftsman.data.entities import elevated_half_diagonal_rails

import attrs


@attrs.define
class ElevatedHalfDiagonalRail(DirectionalMixin, Entity):
    """
    .. versionadded:: 3.0.0 (Factorio 2.0)

    Elevated rail entities which lie halfway in-between the classic 45 degree
    diagonals.
    """

    @property
    def similar_entities(self) -> list[str]:
        return elevated_half_diagonal_rails

    # =========================================================================

    @property
    def double_grid_aligned(self) -> bool:
        return True

    # =========================================================================

    @property
    def valid_directions(self) -> set[Direction]:
        return EIGHT_WAY_DIRECTIONS

    # =========================================================================

    _specify_collision_sets = HalfDiagonalRail._specify_collision_sets

    __hash__ = Entity.__hash__
