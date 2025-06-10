# elevated_curved_rail_a.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import DoubleGridAlignedMixin, DirectionalMixin
from draftsman.constants import Direction, EIGHT_WAY_DIRECTIONS

from draftsman.data.entities import elevated_curved_rails_a

import attrs


@attrs.define
class ElevatedCurvedRailA(DoubleGridAlignedMixin, DirectionalMixin, Entity):
    """
    First set of elevated curved rail entities with 2.0 rails. (TODO)
    """

    @property
    def similar_entities(self) -> list[str]:
        return elevated_curved_rails_a

    # =========================================================================

    @property
    def valid_directions(self) -> set[Direction]:
        return EIGHT_WAY_DIRECTIONS

    # =========================================================================

    __hash__ = Entity.__hash__
