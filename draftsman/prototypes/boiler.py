# boiler.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import (
    EnergySourceMixin,
    DirectionalMixin,
)
from draftsman.utils import fix_incorrect_pre_init

from draftsman.data.entities import boilers

import attrs


@fix_incorrect_pre_init
@attrs.define
class Boiler(EnergySourceMixin, DirectionalMixin, Entity):
    """
    An entity that uses a fuel to convert a fluid (usually water) to another
    fluid (usually steam).
    """

    # TODO: ensure fuel requests to this entity match it's allowed fuel categories

    @property
    def similar_entities(self) -> list[str]:
        return boilers

    # =========================================================================

    __hash__ = Entity.__hash__
