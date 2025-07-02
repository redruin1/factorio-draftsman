# elevated_half_diagonal_rail.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import DirectionalMixin
from draftsman.constants import Direction, EIGHT_WAY_DIRECTIONS

from draftsman.data.entities import elevated_half_diagonal_rails

import attrs


@attrs.define
class ElevatedHalfDiagonalRail(DirectionalMixin, Entity):
    """
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

    __hash__ = Entity.__hash__
