# radar.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import CircuitConnectableMixin, EnergySourceMixin

from draftsman.data.entities import radars

import attrs


@attrs.define
class Radar(CircuitConnectableMixin, EnergySourceMixin, Entity):
    """
    An entity that reveals and scans neighbouring chunks.
    """

    @property
    def similar_entities(self) -> list[str]:
        return radars

    # =========================================================================

    __hash__ = Entity.__hash__
