# electric_pole.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import CircuitConnectableMixin, PowerConnectableMixin
from draftsman.data import entities
from draftsman.utils import get_first

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
        return entities.raw.get(self.name, {"maximum_wire_distance": None}).get(
            "maximum_wire_distance", 0
        )

    # =========================================================================

    __hash__ = Entity.__hash__


ElectricPole.add_schema({"$id": "urn:factorio:entity:electric-pole"})
