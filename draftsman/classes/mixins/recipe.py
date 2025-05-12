# recipe.py

from draftsman.classes.exportable import Exportable
from draftsman.constants import ValidationMode
from draftsman.data import modules, recipes
from draftsman.serialization import draftsman_converters
from draftsman.signatures import (
    QualityName,
    RecipeName,
    AttrsItemRequest,
)
from draftsman.validators import instance_of, is_none, one_of, or_, and_, conditional
from draftsman.warning import (
    ItemLimitationWarning,
    ModuleLimitationWarning,
    RecipeLimitationWarning,
    UnknownRecipeWarning,
)

import attrs
from typing import Optional
import warnings


@attrs.define(slots=False)
class RecipeMixin(Exportable):
    """
    Enables the Entity to have a current recipe it's set to make and a set of
    recipes that it can make.
    """

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
        default=None, validator=instance_of(Optional[RecipeName])
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

    @recipe.validator
    @conditional(ValidationMode.STRICT)
    def _ensure_allowed_recipe(
        self,
        _: attrs.Attribute,
        value: Optional[RecipeName],
    ):
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
    @recipe.validator
    @conditional(ValidationMode.STRICT)
    def _(
        self,
        _: attrs.Attribute,
        value: Optional[RecipeName],
    ):
        """
        Ensure that the modules currently requested to this entity are permitted
        with the currently set recipe.
        """
        if value is None:  # Nothing to validate if empty
            return

        allowed_modules = modules.get_modules_from_effects(self.allowed_effects, value)
        if allowed_modules is None:  # This entity is not currently known
            return

        for item in self.item_requests:
            item: AttrsItemRequest
            if item.id.name not in allowed_modules:
                msg = "Module '{}' cannot be inserted into a machine with recipe '{}'".format(
                    item.id.name, value
                )
                warnings.warn(ItemLimitationWarning(msg))

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

    # =========================================================================

    def merge(self, other: "RecipeMixin"):
        self.recipe = other.recipe
        self.recipe_quality = other.recipe_quality

        super().merge(other)


RecipeMixin.add_schema(
    {
        "properties": {
            "recipe": {"type": "string"},
        }
    },
    version=(1, 0),
)

draftsman_converters.get_version((1, 0)).add_hook_fns(
    RecipeMixin,
    lambda fields: {
        "recipe": fields.recipe.name,
        "recipe_quality": fields.recipe_quality,
    },
    lambda fields, converter: {
        "recipe": fields.recipe.name,
        "recipe_quality": None,
    },
)

RecipeMixin.add_schema(
    {
        "properties": {
            "recipe": {"type": "string"},
            "recipe_quality": {"$ref": "urn:factorio:quality-name"},
        }
    },
    version=(2, 0),
)

draftsman_converters.get_version((2, 0)).add_hook_fns(
    RecipeMixin,
    lambda fields: {
        "recipe": fields.recipe.name,
        "recipe_quality": fields.recipe_quality.name,
    },
)
