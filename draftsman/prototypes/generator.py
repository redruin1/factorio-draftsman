# generator.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import EnergySourceMixin, DirectionalMixin
from draftsman.utils import fix_incorrect_pre_init

from draftsman.data.entities import generators

import attrs


@fix_incorrect_pre_init
@attrs.define
class Generator(EnergySourceMixin, DirectionalMixin, Entity):
    """
    An entity that converts a fluid (usually steam) to electricity.
    """

    @property
    def similar_entities(self) -> list[str]:
        return generators

    # =========================================================================

    __hash__ = Entity.__hash__
