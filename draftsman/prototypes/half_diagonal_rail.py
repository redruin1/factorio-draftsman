# half_diagonal_rail.py

from draftsman.constants import Direction, EIGHT_WAY_DIRECTIONS
from draftsman.classes.entity import Entity
from draftsman.classes.mixins import DirectionalMixin

from draftsman.data.entities import half_diagonal_rails

import attrs


@attrs.define
class HalfDiagonalRail(DirectionalMixin, Entity):
    """
    Rail entities which lie halfway inbetween the classic 45 degree diagonals.
    """

    @property
    def similar_entities(self) -> list[str]:
        return half_diagonal_rails

    # =========================================================================

    @property
    def valid_directions(self) -> set[Direction]:
        return EIGHT_WAY_DIRECTIONS

    # =========================================================================

    __hash__ = Entity.__hash__

