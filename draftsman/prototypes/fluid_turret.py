# fluid_turret.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import (
    ReadAmmoMixin,
    TargetPrioritiesMixin,
    CircuitConditionMixin,
    LogisticConditionMixin,
    CircuitEnableMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    DirectionalMixin,
)

from draftsman.data.entities import fluid_turrets

import attrs


@attrs.define
class FluidTurret(
    ReadAmmoMixin,
    TargetPrioritiesMixin,
    CircuitConditionMixin,
    LogisticConditionMixin,
    CircuitEnableMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    DirectionalMixin,
    Entity,
):
    """
    An entity that automatically targets and attacks other forces within range.
    Uses fluids as ammunition.
    """

    @property
    def similar_entities(self) -> list[str]:
        return fluid_turrets

    # =========================================================================

    __hash__ = Entity.__hash__
