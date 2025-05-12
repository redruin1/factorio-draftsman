# burner_generator.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import (
    ItemRequestMixin,
    EnergySourceMixin,
    DirectionalMixin,
)
from draftsman.classes.vector import Vector, PrimitiveVector
from draftsman.constants import Direction, ValidationMode
from draftsman.signatures import uint32
from draftsman.utils import fix_incorrect_pre_init
from draftsman.warning import ItemLimitationWarning

from draftsman.data.entities import burner_generators
from draftsman.data import entities

import attrs


@fix_incorrect_pre_init
@attrs.define
class BurnerGenerator(ItemRequestMixin, EnergySourceMixin, DirectionalMixin, Entity):
    """
    A electrical generator that only requires fuel in order to function.
    """

    @property
    def similar_entities(self) -> list[str]:
        return burner_generators

    # =========================================================================

    __hash__ = Entity.__hash__
