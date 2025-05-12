# beacon.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import (
    ModulesMixin,
    ItemRequestMixin,
    EnergySourceMixin,
)

from draftsman.data.entities import beacons

import attrs


@attrs.define
class Beacon(ModulesMixin, ItemRequestMixin, EnergySourceMixin, Entity):
    """
    An entity designed to apply module effects to other machines in its radius.
    """

    @property
    def similar_entities(self) -> list[str]:
        return beacons

    # =========================================================================

    __hash__ = Entity.__hash__


Beacon.add_schema({"$id": "urn:factorio:entity:beacon"})
