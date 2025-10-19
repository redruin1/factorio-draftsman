# elevated_curved_rail_a.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import DirectionalMixin
from draftsman.constants import Direction, EIGHT_WAY_DIRECTIONS
from draftsman.prototypes.curved_rail_a import CurvedRailA

from draftsman.data.entities import elevated_curved_rails_a

import attrs


@attrs.define
class ElevatedCurvedRailA(DirectionalMixin, Entity):
    """
    .. versionadded:: 3.0.0 (Factorio 2.0)

    Elevated curved rails which connect straight rails to half-diagonal rails.
    """

    @property
    def similar_entities(self) -> list[str]:
        return elevated_curved_rails_a

    # =========================================================================

    @property
    def double_grid_aligned(self) -> bool:
        return True

    # =========================================================================

    @property
    def valid_directions(self) -> set[Direction]:
        return EIGHT_WAY_DIRECTIONS

    # =========================================================================

    _specify_collision_sets = CurvedRailA._specify_collision_sets

    __hash__ = Entity.__hash__
