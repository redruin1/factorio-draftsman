# recipe.py

from draftsman.classes.exportable import attempt_and_reissue
from draftsman.constants import ValidationMode
from draftsman.data import modules, recipes
from draftsman.signatures import QualityName, RecipeName, get_suggestion
from draftsman.validators import instance_of, is_none, one_of, or_
from draftsman.warning import (
    ItemLimitationWarning,
    RecipeLimitationWarning,
    UnknownRecipeWarning,
)

import attrs
from pydantic import BaseModel, Field, ValidationInfo, field_validator
from typing import TYPE_CHECKING, Literal, Optional

if TYPE_CHECKING:  # pragma: no coverage
    from draftsman.classes.entity import Entity


@attrs.define(slots=False)
class RecipeMixin:
    """
    Enables the Entity to have a current recipe it's set to make and a set of
    recipes that it can make.
    """

    class Format(BaseModel):
        recipe: Optional[str] = Field(
            None, description="""The name of the entity's selected recipe."""
        )
        recipe_quality: Optional[
            Literal["normal", "uncommon", "rare", "epic", "legendary"]
        ] = Field(
            "normal", description="""The specified quality of the selected recipe."""
        )

        @field_validator("recipe")
        @classmethod
        def ensure_recipe_known(cls, value: Optional[str], info: ValidationInfo):
            if not info.context or value is None:
                return value
            if info.context["mode"] <= ValidationMode.MINIMUM:
                return value

            warning_list: list = info.context["warning_list"]

            if value not in recipes.raw:
                warning_list.append(
                    UnknownRecipeWarning(
                        "'{}' is not a known recipe{}".format(
                            value, get_suggestion(value, recipes.raw.keys(), 1)
                        )
                    )
                )

            return value

        @field_validator("recipe")
        @classmethod
        def ensure_recipe_allowed_in_machine(
            cls, value: Optional[str], info: ValidationInfo
        ):
            if not info.context or value is None:
                return value
            if info.context["mode"] <= ValidationMode.MINIMUM:
                return value

            entity: "RecipeMixin" = info.context["object"]
            warning_list: list = info.context["warning_list"]

            if entity.allowed_recipes is None:  # entity not recognized
                return value

            if value in recipes.raw and value not in entity.allowed_recipes:
                warning_list.append(
                    RecipeLimitationWarning(
                        "'{}' is not a valid recipe for '{}'; allowed recipes are: {}".format(
                            value, entity.name, entity.allowed_recipes
                        )
                    )
                )

            return value

        @field_validator("recipe", mode="after")
        @classmethod
        def check_items_fit_in_recipe(cls, value: Optional[str], info: ValidationInfo):
            if not info.context or value is None:
                return value
            if info.context["mode"] <= ValidationMode.MINIMUM:
                return value

            entity: "RecipeMixin" = info.context["object"]
            if entity.items == {}:
                return value

            warning_list: list = info.context["warning_list"]

            # TODO: display all items that don't fit with the current recipe in
            # one warnings
            for item in entity.items:
                if item["id"]["name"] not in entity.allowed_items:
                    warning_list.append(
                        ItemLimitationWarning(
                            "Item '{}' is not used with the current recipe ({})".format(
                                item["id"]["name"], entity.recipe
                            ),
                        )
                    )
                    break

            return value

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

    recipe: Optional[RecipeName] = attrs.field(
        default=None,
        validator=instance_of(Optional[RecipeName])
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
        default="normal",
        validator=or_(one_of(QualityName), is_none)
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

    # =========================================================================

    def __eq__(self, other) -> bool:
        return super().__eq__(other) and self.recipe == other.recipe
