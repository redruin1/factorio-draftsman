# recipe.py

from draftsman.constants import ValidationMode
from draftsman.data import modules, recipes
from draftsman.serialization import draftsman_converters
from draftsman.signatures import (
    QualityName,
    RecipeName,
    get_suggestion,
    AttrsItemRequest,
)
from draftsman.validators import instance_of, is_none, one_of, or_, and_
from draftsman.warning import (
    ItemLimitationWarning,
    ModuleLimitationWarning,
    RecipeLimitationWarning,
    UnknownRecipeWarning,
)

import attrs
from pydantic import BaseModel, Field, ValidationInfo, field_validator
from typing import TYPE_CHECKING, Literal, Optional
import warnings

if TYPE_CHECKING:  # pragma: no coverage
    from draftsman.classes.entity import Entity


@attrs.define(slots=False)
class RecipeMixin:
    """
    Enables the Entity to have a current recipe it's set to make and a set of
    recipes that it can make.
    """

    # class Format(BaseModel):
    #     recipe: Optional[str] = Field(
    #         None, description="""The name of the entity's selected recipe."""
    #     )
    #     recipe_quality: Optional[
    #         Literal["normal", "uncommon", "rare", "epic", "legendary"]
    #     ] = Field(
    #         "normal", description="""The specified quality of the selected recipe."""
    #     )

    #     @field_validator("recipe")
    #     @classmethod
    #     def ensure_recipe_known(cls, value: Optional[str], info: ValidationInfo):
    #         if not info.context or value is None:
    #             return value
    #         if info.context["mode"] <= ValidationMode.MINIMUM:
    #             return value

    #         warning_list: list = info.context["warning_list"]

    #         if value not in recipes.raw:
    #             warning_list.append(
    #                 UnknownRecipeWarning(
    #                     "'{}' is not a known recipe{}".format(
    #                         value, get_suggestion(value, recipes.raw.keys(), 1)
    #                     )
    #                 )
    #             )

    #         return value

    #     @field_validator("recipe")
    #     @classmethod
    #     def ensure_recipe_allowed_in_machine(
    #         cls, value: Optional[str], info: ValidationInfo
    #     ):
    #         if not info.context or value is None:
    #             return value
    #         if info.context["mode"] <= ValidationMode.MINIMUM:
    #             return value

    #         entity: "RecipeMixin" = info.context["object"]
    #         warning_list: list = info.context["warning_list"]

    #         if entity.allowed_recipes is None:  # entity not recognized
    #             return value

    #         if value in recipes.raw and value not in entity.allowed_recipes:
    #             warning_list.append(
    #                 RecipeLimitationWarning(
    #                     "'{}' is not a valid recipe for '{}'; allowed recipes are: {}".format(
    #                         value, entity.name, entity.allowed_recipes
    #                     )
    #                 )
    #             )

    #         return value

    #     @field_validator("recipe", mode="after")
    #     @classmethod
    #     def check_items_fit_in_recipe(cls, value: Optional[str], info: ValidationInfo):
    #         if not info.context or value is None:
    #             return value
    #         if info.context["mode"] <= ValidationMode.MINIMUM:
    #             return value

    #         entity: "RecipeMixin" = info.context["object"]
    #         if entity.items == {}:
    #             return value

    #         warning_list: list = info.context["warning_list"]

    #         # TODO: display all items that don't fit with the current recipe in
    #         # one warnings
    #         for item in entity.items:
    #             if item["id"]["name"] not in entity.allowed_items:
    #                 warning_list.append(
    #                     ItemLimitationWarning(
    #                         "Item '{}' is not used with the current recipe ({})".format(
    #                             item["id"]["name"], entity.recipe
    #                         ),
    #                     )
    #                 )
    #                 break

    #         return value

    # def __init__(self, name: str, similar_entities: list[str], **kwargs):
    #     self._root: __class__.Format

    #     super().__init__(name, similar_entities, **kwargs)

    #     # Recipe that this machine is currently set to
    #     self.recipe = kwargs.get("recipe", None)
    #     self.recipe_quality = kwargs.get("recipe_quality", None)

    # =========================================================================

    @property
    def allowed_recipes(self) -> list[str]:
        """
        A list of all the recipes that this Entity can set itself to assemble.
        Returns ``None`` if the entity's name is not recognized by Draftsman.
        Not exported; read only.
        """
        return recipes.for_machine.get(self.name, None)

    # =========================================================================

    @property
    def allowed_input_ingredients(self):
        """
        Returns a ``set`` of all ingredient names that are valid inputs for the
        currently selected recipe and recipe quality. Returns ``None`` if there
        is insufficient information to deduce this. Not exported; read only.
        """
        return recipes.get_recipe_ingredients(self.recipe, self.recipe_quality)

    # =========================================================================

    def _ensure_allowed_recipe(
        self, attr, value, mode: Optional[ValidationMode] = None
    ):
        mode = mode if mode is not None else self.validate_assignment

        if mode >= ValidationMode.STRICT:
            if value is None:  # Nothing to validate if empty
                return
            if self.allowed_recipes is None:  # This entity is not currently known
                return
            if value not in self.allowed_recipes:
                msg = "'{}' is not a valid recipe for '{}'; allowed recipes are: {}".format(
                    value, self.name, self.allowed_recipes
                )
                warnings.warn(RecipeLimitationWarning(msg))

    # TODO: this should be in ModulesMixin
    def _ensure_modules_permitted_with_recipe(
        self, attr, value, mode: Optional[ValidationMode] = None
    ):
        mode = mode if mode is not None else self.validate_assignment

        if mode >= ValidationMode.STRICT:
            allowed_modules = modules.get_modules_from_effects(
                self.allowed_effects, value
            )
            if allowed_modules is None:
                return
            for item in self.item_requests:
                item: AttrsItemRequest
                if item.id.name not in allowed_modules:
                    msg = "Module '{}' cannot be inserted into a machine with recipe '{}'".format(
                        item.id.name, value
                    )
                    warnings.warn(ItemLimitationWarning(msg))

    recipe: Optional[RecipeName] = attrs.field(
        default=None,
        validator=and_(
            instance_of(Optional[RecipeName]),
            _ensure_allowed_recipe,
            _ensure_modules_permitted_with_recipe,
        ),
    )
    """
    The recipe that this Entity is currently set to make.

    Raises a :py:class:`~draftsman.warning.ModuleLimitationWarning` if the
    recipe changes to one that conflicts with the current module requests.

    Raises a :py:class:`~draftsman.warning.ItemLimtiationWarning` if the
    recipe changes to one whose input ingredients no longer match the
    current item requests.

    warns UnknownRecipeWarning if set to a string that is not contained within
    this entity's recipes.

    :exception DataFormatError: If set to anything other than a ``str`` or
        ``None``.
    """

    # @property
    # def recipe(self) -> str:
    #     """
    #     The recipe that this Entity is currently set to make.

    #     Raises a :py:class:`~draftsman.warning.ModuleLimitationWarning` if the
    #     recipe changes to one that conflicts with the current module requests.

    #     Raises a :py:class:`~draftsman.warning.ItemLimtiationWarning` if the
    #     recipe changes to one whose input ingredients no longer match the
    #     current item requests.

    #     :getter: Gets the current recipe of the Entity.
    #     :setter: Sets the current recipe of the Entity.

    #     :exception TypeError: If set to anything other than a ``str`` or
    #         ``None``.
    #     :exception InvalidRecipeError: If set to a string that is not contained
    #         within this Entity's ``recipes``.
    #     """
    #     return self._root.recipe

    # @recipe.setter
    # def recipe(self, value: str):
    #     if self.validate_assignment:
    #         self._root.recipe = value  # TODO: FIXME; this is bad practice
    #         result = attempt_and_reissue(
    #             self, type(self).Format, self._root, "recipe", value
    #         )
    #         self._root.recipe = result
    #     else:
    #         self._root.recipe = value

    # =========================================================================

    recipe_quality: Optional[QualityName] = attrs.field(
        default="normal", validator=or_(one_of(QualityName), is_none)
    )
    """
    The quality of the recipe that this Entity is selected to make.

    :getter: Gets the current recipe quality of the Entity.
    :setter: Sets the current recipe quality of the Entity.

    :exception DataFormatError: If set to anything other than a ``str`` or
        ``None``.
    """

    # @property
    # def recipe_quality(self) -> Optional[str]:
    #     """
    #     The quality of the recipe that this Entity is selected to make.

    #     :getter: Gets the current recipe quality of the Entity.
    #     :setter: Sets the current recipe quality of the Entity.

    #     :exception DataFormatError: If set to anything other than a ``str`` or
    #         ``None``.
    #     """
    #     return self._root.recipe

    # @recipe_quality.setter
    # def recipe_quality(self, value: str):
    #     if self.validate_assignment:
    #         self._root.recipe_quality = value  # TODO: FIXME; this is bad practice
    #         result = attempt_and_reissue(
    #             self, type(self).Format, self._root, "recipe_quality", value
    #         )
    #         self._root.recipe_quality = result
    #     else:
    #         self._root.recipe_quality = value

    # =========================================================================

    def merge(self, other: "RecipeMixin"):
        self.recipe = other.recipe
        self.recipe_quality = other.recipe_quality

        super().merge(other)


draftsman_converters.get_version((1, 0)).add_schema(
    {"$id": "factorio:recipe_mixin"},
    RecipeMixin,
    lambda fields: {
        fields.recipe.name: "recipe",
        fields.recipe_quality: "recipe_quality",  # TODO: Should this go to extra keys?
    },
    lambda fields: {
        "recipe": fields.recipe.name,
        "recipe_quality": None,
    },
)


draftsman_converters.get_version((2, 0)).add_schema(
    {"$id": "factorio:recipe_mixin"},
    RecipeMixin,
    lambda fields: {
        fields.recipe.name: "recipe",
        fields.recipe_quality.name: "recipe_quality",
    },
)
