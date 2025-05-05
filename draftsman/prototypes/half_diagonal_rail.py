# half_diagonal_rail.py

from draftsman.classes.entity import Entity

from draftsman.data.entities import half_diagonal_rails

import attrs


@attrs.define
class HalfDiagonalRail(Entity):
    """
    Rail entities which lie halfway inbetween the classic 45 degree diagonals.
    """

    @property
    def similar_entities(self) -> list[str]:
        return half_diagonal_rails

    # =========================================================================

    __hash__ = Entity.__hash__
