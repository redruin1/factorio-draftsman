# elevated_curved_rail_b.py

from draftsman.classes.collision_set import CollisionSet
from draftsman.classes.entity import Entity
from draftsman.classes.mixins import DirectionalMixin
from draftsman.constants import Direction, EIGHT_WAY_DIRECTIONS
from draftsman.utils import Rectangle

from draftsman.data import entities
from draftsman.data.entities import elevated_curved_rails_b

import attrs
import math


for rail_name in elevated_curved_rails_b:  # TODO: FIXME
    entities.collision_sets[rail_name] = CollisionSet(
        [Rectangle((0, 0), 1.5, 2.516 * 2, (5.132284556 / 2) / 13 / (2 * math.pi))]
    )


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
