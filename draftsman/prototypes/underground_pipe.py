# underground_pipe.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import DirectionalMixin

from draftsman.data.entities import underground_pipes

import attrs


@attrs.define
class UndergroundPipe(DirectionalMixin, Entity):
    """
    A pipe that transports fluids underneath other entities.
    """

    @property
    def similar_entities(self) -> list[str]:
        return underground_pipes

    # =========================================================================

    __hash__ = Entity.__hash__
