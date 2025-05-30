# ammo_turret.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import (
    ItemRequestMixin,
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
from draftsman.utils import fix_incorrect_pre_init

from draftsman.data.entities import ammo_turrets

import attrs


@fix_incorrect_pre_init
@attrs.define
class AmmoTurret(
    ItemRequestMixin,
    ReadAmmoMixin,
    TargetPrioritiesMixin,
    CircuitConditionMixin,
    LogisticConditionMixin,
    CircuitEnableMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    DirectionalMixin,
    EnergySourceMixin,
    Entity,
):
    """
    An entity that automatically targets and attacks other forces within range.
    Consumes item-based ammunition.
    """

    @property
    def similar_entities(self) -> list[str]:
        return ammo_turrets

    # =========================================================================

    __hash__ = Entity.__hash__

