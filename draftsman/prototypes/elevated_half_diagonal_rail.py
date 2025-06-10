# elevated_half_diagonal_rail.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import DoubleGridAlignedMixin, DirectionalMixin
from draftsman.constants import Direction, EIGHT_WAY_DIRECTIONS

from draftsman.data.entities import elevated_half_diagonal_rails

import attrs


@attrs.define
class ElevatedHalfDiagonalRail(DoubleGridAlignedMixin, DirectionalMixin, Entity):
    """
    Elevated rail entities which lie halfway inbetween the classic 45 degree diagonals. (TODO)
    """

    @property
    def similar_entities(self) -> list[str]:
        return elevated_half_diagonal_rails

    # =========================================================================

    @property
    def valid_directions(self) -> set[Direction]:
        return EIGHT_WAY_DIRECTIONS

    # =========================================================================

    __hash__ = Entity.__hash__
