# fusion_generator.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import EnergySourceMixin, DirectionalMixin
from draftsman.utils import fix_incorrect_pre_init

from draftsman.data.entities import fusion_generators

import attrs


@fix_incorrect_pre_init
@attrs.define
class FusionGenerator(EnergySourceMixin, DirectionalMixin, Entity):
    """
    .. versionadded:: 3.0.0 (Factorio 2.0)

    An entity which converts plasma into energy.
    """

    @property
    def similar_entities(self) -> list[str]:
        return fusion_generators

    # =========================================================================

    __hash__ = Entity.__hash__
