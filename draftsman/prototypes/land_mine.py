# land_mine.py

from draftsman.classes.entity import Entity

from draftsman.data.entities import land_mines

import attrs


@attrs.define
class LandMine(Entity):
    """
    An entity that explodes when in proximity to another force.
    """

    @property
    def similar_entities(self) -> list[str]:
        return land_mines

    # =========================================================================

    __hash__ = Entity.__hash__

