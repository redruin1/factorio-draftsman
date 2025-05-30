# underground_belt.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import IOTypeMixin, DirectionalMixin
from draftsman.utils import fix_incorrect_pre_init

from draftsman.data.entities import underground_belts

import attrs


@fix_incorrect_pre_init
@attrs.define
class UndergroundBelt(IOTypeMixin, DirectionalMixin, Entity):
    """
    A transport belt that transfers items underneath other entities.
    """

    @property
    def similar_entities(self) -> list[str]:
        return underground_belts

    # =========================================================================

    __hash__ = Entity.__hash__

