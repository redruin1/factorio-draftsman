# container.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import (
    RequestItemsMixin,
    CircuitConnectableMixin,
    InventoryMixin,
)
from draftsman.constants import Inventory
from draftsman.utils import calculate_occupied_slots

from draftsman.data.entities import containers

import attrs


@attrs.define
class Container(InventoryMixin, RequestItemsMixin, CircuitConnectableMixin, Entity):
    """
    An entity that holds items.
    """

    @property
    def similar_entities(self) -> list[str]:
        return containers

    # =========================================================================

    __hash__ = Entity.__hash__
