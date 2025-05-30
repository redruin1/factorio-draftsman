# solar_panel.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import EnergySourceMixin

from draftsman.data.entities import solar_panels

import attrs


@attrs.define
class SolarPanel(EnergySourceMixin, Entity):
    """
    An entity that produces electricity depending on the presence of the sun.
    """

    @property
    def similar_entities(self) -> list[str]:
        return solar_panels

    # =========================================================================

    __hash__ = Entity.__hash__

