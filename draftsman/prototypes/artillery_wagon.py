# artillery_wagon.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import (
    ArtilleryAutoTargetMixin,
    EquipmentGridMixin,
    OrientationMixin,
)

from draftsman.data.entities import artillery_wagons

import attrs


@attrs.define
class ArtilleryWagon(
    ArtilleryAutoTargetMixin,
    EquipmentGridMixin,
    OrientationMixin,
    Entity,
):
    """
    An artillery train car.
    """

    # TODO: read the gun prototype for this entity and use that to determine the
    # kinds of ammo it uses
    # Though what about mods?

    # @property # TODO: cache
    # def allowed_items(self) -> Optional[set[str]]:
    #     pass

    # =========================================================================

    @property
    def similar_entities(self) -> list[str]:
        return artillery_wagons

    # =========================================================================

    __hash__ = Entity.__hash__
