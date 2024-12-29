# assembling_machine.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import (
    InputIngredientsMixin,
    ModulesMixin,
    RequestItemsMixin,
    CircuitConnectableMixin,
    RecipeMixin,
    DirectionalMixin,
)
from draftsman.classes.vector import Vector, PrimitiveVector
from draftsman.constants import Direction, ValidationMode
from draftsman.signatures import uint32
from draftsman.utils import get_first
from draftsman.warning import ModuleLimitationWarning

from draftsman.data.entities import assembling_machines
from draftsman.data import entities, modules

from pydantic import ConfigDict, ValidationInfo, field_validator
from typing import Any, Literal, Optional, Union


class AssemblingMachine(
    InputIngredientsMixin,
    ModulesMixin,
    RequestItemsMixin,
    CircuitConnectableMixin,
    RecipeMixin,
    DirectionalMixin,
    Entity,
):
    """
    A machine that takes input items and produces output items. Includes
    assembling machines, chemical plants, oil refineries, and centrifuges, but
    does not include :py:class:`.RocketSilo`.
    """

    class Format(
        InputIngredientsMixin.Format,
        ModulesMixin.Format,
        RequestItemsMixin.Format,
        RecipeMixin.Format,
        DirectionalMixin.Format,
        Entity.Format,
    ):
        @field_validator("items")
        @classmethod
        def ensure_module_permitted_with_recipe(
            cls, value: Optional[dict[str, uint32]], info: ValidationInfo
        ):
            if not info.context or value is None:
                return value
            if info.context["mode"] <= ValidationMode.MINIMUM:
                return value

            entity: "AssemblingMachine" = info.context["object"]
            warning_list: list = info.context["warning_list"]

            if entity.recipe is None:  # Cannot check in this case
                return value

            for item in entity.items:
                # Check to make sure the recipe is within the module's limitations
                # (If it has any)
                module = modules.raw.get(item, {})
                if "limitation" in module:
                    if (  # pragma: no branch
                        entity.recipe is not None
                        and entity.recipe not in module["limitation"]
                    ):
                        tooltip = module.get("limitation_message_key", "no message key")
                        warning_list.append(
                            ModuleLimitationWarning(
                                "Cannot use module '{}' with recipe '{}' ({})".format(
                                    item, entity.recipe, tooltip
                                ),
                            )
                        )

            return value

        model_config = ConfigDict(title="AssemblingMachine")

    def __init__(
        self,
        name: Optional[str] = get_first(assembling_machines),
        position: Union[Vector, PrimitiveVector] = None,
        tile_position: Union[Vector, PrimitiveVector] = (0, 0),
        direction: Direction = Direction.NORTH,
        recipe: str = None,
        items: dict[str, uint32] = {},
        tags: dict[str, Any] = {},
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
            assembling_machines,
            position=position,
            tile_position=tile_position,
            direction=direction,
            recipe=recipe,
            items=items,
            tags=tags,
            **kwargs
        )

        self.validate_assignment = validate_assignment

    # @utils.reissue_warnings
    # def set_item_request(self, item: str, count: uint32):
    #     super().set_item_request(item, count)

    #     # if item in modules.raw:
    #     #     # Check to make sure the recipe is within the module's limitations
    #     #     # (If it has any)
    #     #     module = modules.raw[item]
    #     #     if "limitation" in module:
    #     #         if self.recipe is not None and self.recipe not in module["limitation"]:
    #     #             tooltip = module.get("limitation_message_key", "no message key")
    #     #             warnings.warn(
    #     #                 "Cannot use module '{}' with recipe '{}' ({})".format(
    #     #                     item, self.recipe, tooltip
    #     #                 ),
    #     #                 ModuleLimitationWarning,
    #     #                 stacklevel=2,
    #     #             )

    #     # Make sure the item is one of the input ingredients for the recipe
    #     if self.recipe is not None:
    #         ingredients = recipes.get_recipe_ingredients(self.recipe)

    #         if item not in ingredients:
    #             warnings.warn(
    #                 "Cannot request items that the recipe '{}' doesn't use ({})".format(
    #                     self.recipe, item
    #                 ),
    #                 ItemLimitationWarning,
    #                 stacklevel=2,
    #             )

    # TODO: overwrite direction.setter so that it only works with specific recipes
    # TODO: technically assembling machines can have burner energy sources, so
    # it should inhert BurnerEnergySourceMixin

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

    @property  # TODO abstractproperty
    def allowed_items(self) -> Optional[set[str]]:
        if self.allowed_input_ingredients is None:
            return None
        else:
            return self.allowed_modules.union(self.allowed_input_ingredients)

    @property
    def allowed_modules(self) -> Optional[set[str]]:  # TODO: maybe set?
        if self.recipe is None:
            return super().allowed_modules
        else:
            return modules.get_modules_from_effects(self.allowed_effects, self.recipe)

    # =========================================================================

    __hash__ = Entity.__hash__
