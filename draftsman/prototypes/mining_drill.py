# mining_drill.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import (
    BurnerEnergySourceMixin,
    ModulesMixin,
    RequestItemsMixin,
    CircuitReadResourceMixin,
    CircuitConditionMixin,
    EnableDisableMixin,
    LogisticConditionMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    DirectionalMixin,
)
from draftsman.classes.vector import Vector, PrimitiveVector
from draftsman.constants import Direction, ValidationMode
from draftsman.error import InvalidItemError
from draftsman.signatures import Connections, DraftsmanBaseModel, uint32
from draftsman.utils import reissue_warnings
from draftsman.warning import ItemLimitationWarning

from draftsman.data.entities import mining_drills
from draftsman.data import entities

from pydantic import ConfigDict
from typing import Any, Literal, Optional, Union
import warnings


class MiningDrill(
    BurnerEnergySourceMixin,
    ModulesMixin,
    RequestItemsMixin,
    CircuitReadResourceMixin,
    CircuitConditionMixin,
    LogisticConditionMixin,
    EnableDisableMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    DirectionalMixin,
    Entity,
):
    """
    An entity that extracts resources from the environment.
    """

    class Format(
        BurnerEnergySourceMixin.Format,
        ModulesMixin.Format,
        RequestItemsMixin.Format,
        CircuitReadResourceMixin.Format,
        CircuitConditionMixin.Format,
        LogisticConditionMixin.Format,
        EnableDisableMixin.Format,
        ControlBehaviorMixin.Format,
        CircuitConnectableMixin.Format,
        DirectionalMixin.Format,
        Entity.Format,
    ):
        class ControlBehavior(
            CircuitReadResourceMixin.ControlFormat,
            CircuitConditionMixin.ControlFormat,
            LogisticConditionMixin.ControlFormat,
            EnableDisableMixin.ControlFormat,
            DraftsmanBaseModel,
        ):
            pass

        control_behavior: Optional[ControlBehavior] = ControlBehavior()

        model_config = ConfigDict(title="MiningDrill")

    def __init__(
        self,
        name: str = mining_drills[0],
        position: Union[Vector, PrimitiveVector] = None,
        tile_position: Union[Vector, PrimitiveVector] = (0, 0),
        direction: Direction = Direction.NORTH,
        items: dict[str, uint32] = {},  # TODO: ItemID
        connections: Connections = {},
        control_behavior: Format.ControlBehavior = {},
        tags: dict[str, Any] = {},
        validate: Union[
            ValidationMode, Literal["none", "minimum", "strict", "pedantic"]
        ] = ValidationMode.STRICT,
        validate_assignment: Union[
            ValidationMode, Literal["none", "minimum", "strict", "pedantic"]
        ] = ValidationMode.STRICT,
        **kwargs
    ):
        """
        TODO
        """

        super().__init__(
            name,
            mining_drills,
            position=position,
            tile_position=tile_position,
            direction=direction,
            items=items,
            connections=connections,
            control_behavior=control_behavior,
            tags=tags,
            **kwargs
        )

        self.validate_assignment = validate_assignment

        self.validate(mode=validate).reissue_all(stacklevel=3)

    # =========================================================================

    @property
    def allowed_items(self) -> Optional[set[str]]:
        if self.allowed_modules is None:  # Unknown entity
            return None
        return self.allowed_modules.union(self.allowed_fuel_items)

    # @reissue_warnings
    # def set_item_request(self, item: str, count: Optional[uint32]):  # TODO: ItemID
    #     # Make sure the item exists
    #     print("MiningDrill")
    #     print(item, count)
    #     if item not in items.raw:
    #         raise InvalidItemError(item)

    #     if item in items.raw and item not in modules.raw:
    #         warnings.warn(
    #             "Item '{}' cannot be placed in MiningDrill".format(item),
    #             ItemLimitationWarning,
    #             stacklevel=2,
    #         )

    #     super().set_item_request(item, count)

    # =========================================================================

    __hash__ = Entity.__hash__
