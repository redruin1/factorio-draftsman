# elevated_curved_rail_b.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import DirectionalMixin
from draftsman.constants import Direction, EIGHT_WAY_DIRECTIONS

from draftsman.data.entities import elevated_curved_rails_b

import attrs


@attrs.define
class ElevatedCurvedRailB(DirectionalMixin, Entity):
    """
    .. versionadded:: 3.0.0 (Factorio 2.0)

    Elevated curved rails which connect half-diagonal rails to diagonal rails.
    """

    @property
    def similar_entities(self) -> list[str]:
        return elevated_curved_rails_b

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
