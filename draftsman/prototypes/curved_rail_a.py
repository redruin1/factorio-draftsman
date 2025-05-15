# curved_rail_a.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import DoubleGridAlignedMixin, DirectionalMixin
from draftsman.constants import Direction, EIGHT_WAY_DIRECTIONS

from draftsman.data.entities import curved_rails_a

import attrs


@attrs.define
class CurvedRailA(DoubleGridAlignedMixin, DirectionalMixin, Entity):
    """
    First set of curved rail entities with 2.0 rails. (TODO)
    """

    @property
    def similar_entities(self) -> list[str]:
        return curved_rails_a

    # =========================================================================

    @property
    def valid_directions(self) -> set[Direction]:
        return EIGHT_WAY_DIRECTIONS

    # =========================================================================

    __hash__ = Entity.__hash__


CurvedRailA.add_schema(None, version=(1, 0))

CurvedRailA.add_schema(
    {
        "$id": "urn:factorio:entity:curved-rail-a",
    },
    version=(2, 0),
)
