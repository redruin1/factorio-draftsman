# furnace.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import (
    InputIngredientsMixin,
    ModulesMixin,
    ItemRequestMixin,
    CraftingMachineMixin,
    EnergySourceMixin,
    LogisticConditionMixin,
    CircuitConditionMixin,
    CircuitEnableMixin,
    CircuitConnectableMixin,
    ControlBehaviorMixin,
    DirectionalMixin,
)
from draftsman.utils import fix_incorrect_pre_init

from draftsman.data.entities import furnaces
from draftsman.data import entities, recipes

import attrs
from typing import Optional


# _valid_input_ingredients: dict[str, set[str]] = {}


@fix_incorrect_pre_init
@attrs.define
class Furnace(
    InputIngredientsMixin,
    ModulesMixin,
    ItemRequestMixin,
    CraftingMachineMixin,
    EnergySourceMixin,
    LogisticConditionMixin,
    CircuitConditionMixin,
    CircuitEnableMixin,
    CircuitConnectableMixin,
    ControlBehaviorMixin,
    DirectionalMixin,
    Entity,
):
    """
    An entity that takes a fuel and an input item and creates an output item.
    """

    @property
    def similar_entities(self) -> list[str]:
        return furnaces

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
            for item in recipes.get_recipe_ingredients(
                recipe_name, "normal"
            )  # TODO: how to handle qualities?
        )

    # =========================================================================

    __hash__ = Entity.__hash__


Furnace.add_schema(
    {
        "$id": "urn:factorio:entity:furnace",
    },
    version=(1, 0),
    mro=(ItemRequestMixin, DirectionalMixin, Entity),
)

Furnace.add_schema({"$id": "urn:factorio:entity:furnace"}, version=(2, 0))
