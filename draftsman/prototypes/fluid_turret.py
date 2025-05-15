# fluid_turret.py

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
    DirectionalMixin,
)
from draftsman.utils import fix_incorrect_pre_init

from draftsman.data.entities import fluid_turrets

import attrs


@fix_incorrect_pre_init
@attrs.define
class FluidTurret(
    ItemRequestMixin,
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


FluidTurret.add_schema(
    {
        "$id": "urn:factorio:entity:fluid-turret",
    },
    version=(1, 0),
    mro=(ItemRequestMixin, DirectionalMixin, Entity),
)

FluidTurret.add_schema({"$id": "urn:factorio:entity:fluid-turret"}, version=(2, 0))
