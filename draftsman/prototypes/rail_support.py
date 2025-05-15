# rail_support.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import DoubleGridAlignedMixin, DirectionalMixin
from draftsman.constants import Direction, SIXTEEN_WAY_DIRECTIONS

from draftsman.data.entities import rail_supports

import attrs


@attrs.define
class RailSupport(DoubleGridAlignedMixin, DirectionalMixin, Entity):
    """
    An entity that permits the construction of elevated rails above it.
    """

    @property
    def similar_entities(self) -> list[str]:
        return rail_supports

    # =========================================================================

    @property
    def valid_directions(self) -> set[Direction]:
        return SIXTEEN_WAY_DIRECTIONS

    # =========================================================================

    __hash__ = Entity.__hash__


RailSupport.add_schema(None, version=(1, 0))

RailSupport.add_schema({"$id": "urn:factorio:entity:rail-support"}, version=(2, 0))
