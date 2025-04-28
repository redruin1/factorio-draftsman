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
from draftsman.utils import fix_incorrect_pre_init

from draftsman.data.entities import mining_drills

import attrs
from typing import Optional


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

    # class Format(
    #     BurnerEnergySourceMixin.Format,
    #     ModulesMixin.Format,
    #     RequestItemsMixin.Format,
    #     CircuitReadResourceMixin.Format,
    #     CircuitConditionMixin.Format,
    #     LogisticConditionMixin.Format,
    #     CircuitEnableMixin.Format,
    #     ControlBehaviorMixin.Format,
    #     CircuitConnectableMixin.Format,
    #     DirectionalMixin.Format,
    #     Entity.Format,
    # ):
    #     class ControlBehavior(
    #         CircuitReadResourceMixin.ControlFormat,
    #         CircuitConditionMixin.ControlFormat,
    #         LogisticConditionMixin.ControlFormat,
    #         CircuitEnableMixin.ControlFormat,
    #         DraftsmanBaseModel,
    #     ):
    #         pass

    #     control_behavior: Optional[ControlBehavior] = ControlBehavior()

    #     model_config = ConfigDict(title="MiningDrill")

    # def __init__(
    #     self,
    #     name: Optional[str] = get_first(mining_drills),
    #     position: Union[Vector, PrimitiveVector] = None,
    #     tile_position: Union[Vector, PrimitiveVector] = (0, 0),
    #     direction: Direction = Direction.NORTH,
    #     items: Optional[list[ItemRequest]] = [],  # TODO: ItemID
    #     control_behavior: Format.ControlBehavior = {},
    #     tags: dict[str, Any] = {},
    #     validate_assignment: Union[
    #         ValidationMode, Literal["none", "minimum", "strict", "pedantic"]
    #     ] = ValidationMode.STRICT,
    #     **kwargs
    # ):
    #     """
    #     TODO
    #     """

    #     super().__init__(
    #         name,
    #         mining_drills,
    #         position=position,
    #         tile_position=tile_position,
    #         direction=direction,
    #         items=items,
    #         control_behavior=control_behavior,
    #         tags=tags,
    #         **kwargs
    #     )

    #     self.validate_assignment = validate_assignment

    # =========================================================================

    @property
    def similar_entities(self) -> list[str]:
        return mining_drills

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
