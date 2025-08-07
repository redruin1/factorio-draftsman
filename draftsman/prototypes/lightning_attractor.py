# lightning_attractor.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import EnergySourceMixin

from draftsman.data.entities import lightning_attractors

import attrs


@attrs.define
class LightningAttractor(EnergySourceMixin, Entity):
    """
    .. versionadded:: 3.0.0 (Factorio 2.0)

    An entity that protects an area from lightning strike damage and converts
    their energy for a power grid.
    """

    @property
    def similar_entities(self) -> list[str]:
        return lightning_attractors

    # =========================================================================

    __hash__ = Entity.__hash__
