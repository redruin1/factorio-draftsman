# artillery_turret.py

from draftsman.classes.entity import Entity
from draftsman.classes.exportable import attempt_and_reissue
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
from draftsman.classes.vector import Vector, PrimitiveVector
from draftsman.constants import Direction, ValidationMode
from draftsman.signatures import Connections, DraftsmanBaseModel, uint8
from draftsman.utils import get_first

from typing import Optional

from draftsman.data.entities import artillery_turrets

from pydantic import ConfigDict, Field
from typing import Any, Literal, Optional, Union


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

    class Format(
        ArtilleryAutoTargetMixin.Format,
        RequestItemsMixin.Format,
        ReadAmmoMixin.Format,
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
            CircuitConditionMixin.ControlFormat,
            LogisticConditionMixin.ControlFormat,
            CircuitEnableMixin.ControlFormat,
            DraftsmanBaseModel,
        ):
            pass

        control_behavior: Optional[ControlBehavior] = ControlBehavior()

        model_config = ConfigDict(title="ArtilleryTurret")

    def __init__(
        self,
        name: Optional[str] = get_first(artillery_turrets),
        position: Union[Vector, PrimitiveVector] = None,
        tile_position: Union[Vector, PrimitiveVector] = (0, 0),
        direction: Direction = Direction.NORTH,
        artillery_auto_targeting: Optional[bool] = True,
        control_behavior: Format.ControlBehavior = {},
        tags: dict[str, Any] = {},
        validate_assignment: Union[
            ValidationMode, Literal["none", "minimum", "strict", "pedantic"]
        ] = ValidationMode.STRICT,
        **kwargs
    ):
        self._root: self.__class__.Format
        super().__init__(
            name,
            artillery_turrets,
            position=position,
            tile_position=tile_position,
            direction=direction,
            artillery_auto_targeting=artillery_auto_targeting,
            control_behavior=control_behavior,
            tags=tags,
            **kwargs
        )

        self.validate_assignment = validate_assignment

    # =========================================================================

    __hash__ = Entity.__hash__
