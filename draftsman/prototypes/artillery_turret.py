# artillery_turret.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import (
    ArtilleryAutoTargetMixin,
    RequestItemsMixin,
    ReadAmmoMixin,
    CircuitConditionMixin,
    LogisticConditionMixin,
    CircuitEnableMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    DirectionalMixin,
)

from draftsman.data.entities import artillery_turrets

import attrs


@attrs.define
class ArtilleryTurret(
    ArtilleryAutoTargetMixin,
    RequestItemsMixin,
    ReadAmmoMixin,
    CircuitConditionMixin,
    LogisticConditionMixin,
    CircuitEnableMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    DirectionalMixin,
    Entity,
):
    """
    A turret which can only target fixed enemy structures and uses artillery
    ammunition.
    """

    @property
    def similar_entities(self) -> list[str]:
        return artillery_turrets

    # =========================================================================

    __hash__ = Entity.__hash__
