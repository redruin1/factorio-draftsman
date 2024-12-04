# furnace.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import (
    InputIngredientsMixin,
    BurnerEnergySourceMixin,
    ModulesMixin,
    RequestItemsMixin,
)
from draftsman.classes.vector import Vector, PrimitiveVector
from draftsman.constants import ValidationMode
from draftsman.signatures import uint32
from draftsman.utils import get_first
from draftsman.warning import ItemCapacityWarning, ItemLimitationWarning

from draftsman.data.entities import furnaces
from draftsman.data import entities, items, modules, recipes

from pydantic import ConfigDict, ValidationInfo, field_validator
from typing import Any, Literal, Optional, Union


_valid_input_ingredients: dict[str, set[str]] = {}


class Furnace(
    InputIngredientsMixin,
    BurnerEnergySourceMixin,
    ModulesMixin,
    RequestItemsMixin,
    Entity,
):
    """
    An entity that takes a fuel and an input item and creates an output item.
    """

    class Format(
        InputIngredientsMixin.Format,
        BurnerEnergySourceMixin.Format,
        ModulesMixin.Format,
        RequestItemsMixin.Format,
        Entity.Format,
    ):
        @field_validator("items")
        @classmethod
        def ensure_input_ingredients_are_valid(
            cls, value: Optional[dict[str, uint32]], info: ValidationInfo
        ):
            """
            Warns if the requested input items are not valid ingredients to this
            entity's recipe list.
            """
            if not info.context or value is None:
                return value
            if info.context["mode"] <= ValidationMode.MINIMUM:
                return value

            entity: "Furnace" = info.context["object"]
            warning_list: list = info.context["warning_list"]

            for item in entity.items:
                if (
                    item not in modules.raw
                    and item not in entity.allowed_input_ingredients
                ):
                    warning_list.append(
                        ItemLimitationWarning(
                            "Requested item '{}' cannot be smelted by furnace '{}'".format(
                                item, entity.name
                            ),
                        )
                    )

            return value

        @field_validator("items")
        @classmethod
        def ensure_input_ingredients_dont_exceed_stack_size(
            cls, value: Optional[dict[str, uint32]], info: ValidationInfo
        ):
            """
            Warns if the amount of a particular item requested exceeds 1 stack
            of that item, indicating that some items will be returned when
            placed.
            """
            if not info.context or value is None:
                return value
            if info.context["mode"] <= ValidationMode.MINIMUM:
                return value

            entity: "Furnace" = info.context["object"]
            warning_list: list = info.context["warning_list"]

            for item, count in entity.ingredient_items.items():
                stack_size = items.raw[item]["stack_size"]
                if count > stack_size:
                    warning_list.append(
                        ItemCapacityWarning(
                            "Cannot request more than {} of '{}' to a '{}'; will not fit in ingredient inputs".format(
                                stack_size, item, entity.name
                            )
                        )
                    )

            return value

        model_config = ConfigDict(title="Furnace")

    def __init__(
        self,
        name: Optional[str] = get_first(furnaces),
        position: Union[Vector, PrimitiveVector] = None,
        tile_position: Union[Vector, PrimitiveVector] = (0, 0),
        items: dict[str, uint32] = {},  # TODO: ItemID
        tags: dict[str, Any] = {},
        validate_assignment: Union[
            ValidationMode, Literal["none", "minimum", "strict", "pedantic"]
        ] = ValidationMode.STRICT,
        **kwargs
    ):
        """
        TODO
        """

        # Cache a set of valid ingredients for this entity, if they have not
        # been created for this entity beforehand
        if name not in _valid_input_ingredients:
            if name in entities.raw:
                crafting_categories = entities.raw[name]["crafting_categories"]
                total_recipes = []
                for crafting_category in crafting_categories:
                    total_recipes.extend(recipes.categories[crafting_category])

                _valid_input_ingredients[name] = set()
                for recipe_name in total_recipes:
                    # TODO: what about expensive mode?
                    _valid_input_ingredients[name].update(
                        recipes.get_recipe_ingredients(recipe_name)
                    )
            else:
                _valid_input_ingredients[name] = None

        super().__init__(
            name,
            furnaces,
            position=position,
            tile_position=tile_position,
            items=items,
            tags=tags,
            **kwargs
        )

        self.validate_assignment = validate_assignment

    # =========================================================================

    @property
    def allowed_effects(self) -> Optional[set[str]]:
        # If name not known, return None
        entity = entities.raw.get(self.name, None)
        if entity is None:
            return None
        # If name known, but no key, then return empty list
        result = entity.get("allowed_effects", [])
        # Normalize single string effect to a 1-length list
        return {result} if isinstance(result, str) else set(result)

    # =========================================================================

    @property
    def allowed_input_ingredients(self) -> set[str]:  # TODO: cache
        """
        A set of strings, each one an ingredient that can be used as a input for
        this particular furnace. Returns ``None`` if this entity is not
        recognized by Draftsman. Not exported; read only.
        """
        crafting_categories = entities.raw.get(
            self.name, {"crafting_categories": None}
        )["crafting_categories"]
        if crafting_categories is None:
            return None

        total_recipes = []
        for crafting_category in crafting_categories:
            total_recipes.extend(recipes.categories[crafting_category])

        return set(
            item
            for recipe_name in total_recipes
            for item in recipes.get_recipe_ingredients(recipe_name)
        )

    # =========================================================================

    # @reissue_warnings
    # def set_item_request(self, item: str, count: int) -> None:

    #     # TODO: handle fuel input items
    #     # TODO: limit item fuel requests to obey "fuel_inventory_size"

    #     # self._handle_module_slots(item, count)

    #     super().set_item_request(item, count)

    #     if item not in modules.raw and item not in self.allowed_input_ingredients:
    #         warnings.warn(
    #             "Cannot request items that this Furnace doesn't use ({})".format(item),
    #             ItemLimitationWarning,
    #             stacklevel=2,
    #         )

    # =========================================================================

    __hash__ = Entity.__hash__
