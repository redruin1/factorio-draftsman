# furnace.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import (
    InputIngredientsMixin,
    ModulesMixin,
    CraftingMachineMixin,
    EnergySourceMixin,
    LogisticConditionMixin,
    CircuitConditionMixin,
    CircuitEnableMixin,
    CircuitConnectableMixin,
    ControlBehaviorMixin,
    DirectionalMixin,
)
from draftsman.constants import InventoryType
from draftsman.signatures import ModuleID, QualityID
from draftsman.utils import fix_incorrect_pre_init

from draftsman.data.entities import furnaces
from draftsman.data import entities, modules, recipes

import attrs
from typing import Iterable


@fix_incorrect_pre_init
@attrs.define
class Furnace(
    InputIngredientsMixin,
    ModulesMixin,
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
    An entity that automatically determines it's recipe from it's input items.
    Obviously includes regular furnaces, but can also include other machines
    like recyclers.
    """

    @property
    def similar_entities(self) -> list[str]:
        return furnaces

    # =========================================================================

    @property
    def allowed_input_ingredients(self) -> set[str]:  # TODO: cache
        """
        A set of strings, each one an ingredient that can be used as a input for
        this particular furnace. Returns ``None`` if this entity is not
        recognized by Draftsman.
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

    @property
    def module_slots_occupied(self) -> int:
        return len(
            {
                inv_pos.stack
                for req in self.item_requests
                if req.id.name in modules.raw
                for inv_pos in req.items.in_inventory
                if inv_pos.inventory == InventoryType.FURNACE_MODULES
            }
        )

    # =========================================================================

    def request_modules(
        self,
        module_name: str, # TODO: should be ModuleID
        slots: int | Iterable[int],
        quality: QualityID = "normal",
    ):
        return super().request_modules(
            InventoryType.FURNACE_MODULES, module_name, slots, quality
        )

    # =========================================================================

    __hash__ = Entity.__hash__
