# rail_ramp.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import DirectionalMixin

from draftsman.data.entities import rail_ramps

import attrs


@attrs.define
class RailRamp(DirectionalMixin, Entity):
    """
    A ramp which transitions between ground and elevated rails.
    """

    @property
    def similar_entities(self) -> list[str]:
        return rail_ramps

    # =========================================================================

    @property
    def double_grid_aligned(self) -> bool:
        return True

    # =========================================================================

    __hash__ = Entity.__hash__
