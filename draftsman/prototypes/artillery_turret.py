# artillery_turret.py

from draftsman.classes.entity import Entity
from draftsman.classes.exportable import attempt_and_reissue
from draftsman.classes.mixins import (
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

        artillery_auto_targeting: Optional[bool] = Field(
            True,
            description="""
            Whether or not this turret automatically targets enemy structures 
            in its range.
            """,
        )

        model_config = ConfigDict(title="ArtilleryTurret")

    def __init__(
        self,
        name: Optional[str] = get_first(artillery_turrets),
        position: Union[Vector, PrimitiveVector] = None,
        tile_position: Union[Vector, PrimitiveVector] = (0, 0),
        direction: Direction = Direction.NORTH,
        connections: Connections = {},
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
            connections=connections,
            control_behavior=control_behavior,
            tags=tags,
            **kwargs
        )

        self.validate_assignment = validate_assignment

    # =========================================================================

    @property
    def auto_target(self) -> bool:
        """
        TODO
        """
        return self._root.artillery_auto_targeting

    @auto_target.setter
    def auto_target(self, value: Optional[bool]) -> None:
        if self.validate_assignment:
            result = attempt_and_reissue(
                self,
                self.Format,
                self._root,
                "artillery_auto_targeting",
                value,
            )
            self.control_behavior.artillery_auto_targeting = result
        else:
            self.control_behavior.artillery_auto_targeting = value

    # =========================================================================

    __hash__ = Entity.__hash__
