# burner_generator.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import (
    RequestItemsMixin,
    EnergySourceMixin,
    DirectionalMixin,
)
from draftsman.classes.vector import Vector, PrimitiveVector
from draftsman.constants import Direction, ValidationMode
from draftsman.signatures import ItemRequest, uint32
from draftsman.utils import fix_incorrect_pre_init
from draftsman.warning import ItemLimitationWarning

from draftsman.data.entities import burner_generators
from draftsman.data import entities

import attrs


@fix_incorrect_pre_init
@attrs.define
class BurnerGenerator(
    RequestItemsMixin, EnergySourceMixin, DirectionalMixin, Entity
):
    """
    A electrical generator that only requires fuel in order to function.
    """

    # class Format(
    #     BurnerEnergySourceMixin.Format,
    #     RequestItemsMixin.Format,
    #     DirectionalMixin.Format,
    #     Entity.Format,
    # ):
    #     @field_validator("items")
    #     @classmethod
    #     def only_allow_fuel_item_requests(
    #         cls, value: Optional[dict[str, uint32]], info: ValidationInfo
    #     ):
    #         """
    #         Warn the user if they set anything other than a fuel item request
    #         for this entity.
    #         """
    #         if not info.context or value is None:
    #             return value
    #         if info.context["mode"] <= ValidationMode.MINIMUM:
    #             return value

    #         entity: "BurnerGenerator" = info.context["object"]
    #         warning_list: list = info.context["warning_list"]

    #         if entity.allowed_fuel_items is None:  # entity not recognized
    #             return value

    #         for item in entity.items:
    #             if item in items.raw and item not in items.all_fuel_items:
    #                 warning_list.append(
    #                     ItemLimitationWarning(
    #                         "Cannot add item '{}' to '{}'; this entity only can only recieve fuel items".format(
    #                             item, entity.name
    #                         )
    #                     )
    #                 )

    #         return value

    #     model_config = ConfigDict(title="BurnerGenerator")

    # def __init__(
    #     self,
    #     name: Optional[str] = get_first(burner_generators),
    #     position: Union[Vector, PrimitiveVector] = None,
    #     tile_position: Union[Vector, PrimitiveVector] = (0, 0),
    #     direction: Direction = Direction.NORTH,
    #     items: Optional[list[ItemRequest]] = [],  # TODO: ItemID
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
    #         burner_generators,
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
        return burner_generators

    # =========================================================================

    @property
    def input_energy_source(self) -> dict:
        return entities.raw.get(self.name, {"burner": None})["burner"]

    # =========================================================================

    __hash__ = Entity.__hash__
