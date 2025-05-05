# mining_drill.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import (
    ModulesMixin,
    RequestItemsMixin,
    CircuitReadResourceMixin,
    CircuitConditionMixin,
    CircuitEnableMixin,
    LogisticConditionMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    EnergySourceMixin,
    DirectionalMixin,
)
from draftsman.constants import Inventory
from draftsman.signatures import ModuleName, QualityName
from draftsman.utils import fix_incorrect_pre_init

from draftsman.data.entities import mining_drills

import attrs
from typing import Iterable


@fix_incorrect_pre_init
@attrs.define
class MiningDrill(
    ModulesMixin,
    RequestItemsMixin,
    CircuitReadResourceMixin,
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
    An entity that extracts resources (item or fluid) from the environment.
    """

    @property
    def similar_entities(self) -> list[str]:
        return mining_drills

    # =========================================================================

    def request_modules(
        self,
        module_name: ModuleName,
        slots: int | Iterable[int],
        quality: QualityName = "normal",
    ):
        return super().request_modules(
            Inventory.mining_drill_modules, module_name, slots, quality
        )

    __hash__ = Entity.__hash__
