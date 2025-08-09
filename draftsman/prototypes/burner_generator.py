# burner_generator.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import (
    EnergySourceMixin,
    DirectionalMixin,
)
from draftsman.utils import fix_incorrect_pre_init

from draftsman.data.entities import burner_generators

import attrs


@fix_incorrect_pre_init
@attrs.define
class BurnerGenerator(EnergySourceMixin, DirectionalMixin, Entity):
    """
    A electrical generator that turns burnable fuel directly into electrical
    energy.
    """

    @property
    def similar_entities(self) -> list[str]:
        return burner_generators

    # =========================================================================

    __hash__ = Entity.__hash__
