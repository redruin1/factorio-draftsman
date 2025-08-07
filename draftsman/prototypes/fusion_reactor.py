# fusion_reactor.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import EnergySourceMixin, DirectionalMixin

from draftsman.data.entities import fusion_reactors

import attrs


@attrs.define
class FusionReactor(EnergySourceMixin, DirectionalMixin, Entity):
    """
    .. versionadded:: 3.0.0 (Factorio 2.0)

    A reactor which produces hot plasma.
    """

    @property
    def similar_entities(self) -> list[str]:
        return fusion_reactors

    # =========================================================================

    __hash__ = Entity.__hash__
