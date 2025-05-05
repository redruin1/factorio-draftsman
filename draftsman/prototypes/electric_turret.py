# electric_turret.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import (
    RequestItemsMixin,
    ReadAmmoMixin,
    TargetPrioritiesMixin,
    CircuitConditionMixin,
    LogisticConditionMixin,
    CircuitEnableMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    EnergySourceMixin,
    DirectionalMixin,
)

from draftsman.data.entities import electric_turrets

import attrs


@attrs.define
class ElectricTurret(
    RequestItemsMixin,
    ReadAmmoMixin,
    TargetPrioritiesMixin,
    CircuitConditionMixin,
    LogisticConditionMixin,
    CircuitEnableMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    EnergySourceMixin,
    DirectionalMixin,
    Entity,
):
    """
    An entity that automatically targets and attacks other forces within range.
    Uses electricity as ammunition.
    """

    @property
    def similar_entities(self) -> list[str]:
        return electric_turrets

    # =========================================================================

    __hash__ = Entity.__hash__
