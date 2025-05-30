# electric_pole.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import CircuitConnectableMixin, PowerConnectableMixin
from draftsman.data import entities, qualities

from draftsman.data.entities import electric_poles

import attrs


@attrs.define
class ElectricPole(CircuitConnectableMixin, PowerConnectableMixin, Entity):
    """
    An entity used to distribute electrical energy as a network.
    """

    @property
    def similar_entities(self) -> list[str]:
        return electric_poles

    # =========================================================================

    @property
    def circuit_wire_max_distance(self) -> float:
        # Electric poles use a custom key (for some reason)
        wire_max_dist = entities.raw.get(self.name, {}).get("maximum_wire_distance", None)
        if wire_max_dist is None:
            return None
        buff = 2 * qualities.raw.get(self.quality, {"level": 0})["level"]
        return wire_max_dist + buff

    # =========================================================================

    __hash__ = Entity.__hash__

