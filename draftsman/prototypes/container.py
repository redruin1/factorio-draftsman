# container.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import (
    ItemRequestMixin,
    CircuitConnectableMixin,
    InventoryMixin,
)

from draftsman.data.entities import containers

import attrs


@attrs.define
class Container(InventoryMixin, ItemRequestMixin, CircuitConnectableMixin, Entity):
    """
    An entity that holds items.
    """

    @property
    def similar_entities(self) -> list[str]:
        return containers

    # =========================================================================

    __hash__ = Entity.__hash__


Container.add_schema(
    {
        "$id": "urn:factorio:entity:container",
    }
)
