# fluid_turret.py

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
    DirectionalMixin,
)
from draftsman.classes.vector import Vector, PrimitiveVector
from draftsman.constants import Direction, ValidationMode
from draftsman.signatures import DraftsmanBaseModel, uint32
from draftsman.utils import get_first, fix_incorrect_pre_init

from draftsman.data.entities import fluid_turrets

import attrs
from pydantic import ConfigDict
from typing import Any, Literal, Optional, Union


@fix_incorrect_pre_init
@attrs.define
class FluidTurret(
    RequestItemsMixin,
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

    class Format(
        RequestItemsMixin.Format,
        ReadAmmoMixin.Format,
        TargetPrioritiesMixin.Format,
        CircuitConditionMixin.Format,
        LogisticConditionMixin.Format,
        CircuitEnableMixin.Format,
        ControlBehaviorMixin.Format,
        CircuitConnectableMixin.Format,
        DirectionalMixin.Format,
        Entity.Format,
    ):
        class ControlBehavior(
            ReadAmmoMixin.ControlFormat,
            TargetPrioritiesMixin.ControlFormat,
            CircuitConditionMixin.ControlFormat,
            LogisticConditionMixin.ControlFormat,
            CircuitEnableMixin.ControlFormat,
            DraftsmanBaseModel,
        ):
            pass

        control_behavior: Optional[ControlBehavior] = ControlBehavior()

        model_config = ConfigDict(title="AmmoTurret")

    # def __init__(
    #     self,
    #     name: Optional[str] = get_first(fluid_turrets),
    #     position: Union[Vector, PrimitiveVector] = None,
    #     tile_position: Union[Vector, PrimitiveVector] = (0, 0),
    #     direction: Direction = Direction.NORTH,
    #     items: dict[str, uint32] = {},  # TODO: ItemID
    #     tags: dict[str, Any] = {},
    #     validate_assignment: Union[
    #         ValidationMode, Literal["none", "minimum", "strict", "pedantic"]
    #     ] = ValidationMode.STRICT,
    #     **kwargs
    # ):
    #     """
    #     Construct a new fluid turret.

    #     TODO
    #     """

    #     super().__init__(
    #         name,
    #         fluid_turrets,
    #         position=position,
    #         tile_position=tile_position,
    #         direction=direction,
    #         items=items,
    #         tags=tags,
    #         **kwargs
    #     )

    #     self.validate_assignment = validate_assignment

    @property
    def similar_entities(self) -> list[str]:
        return fluid_turrets

    # =========================================================================

    __hash__ = Entity.__hash__
