# recipe.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman import signatures
from draftsman.data import recipes, modules
from draftsman.error import InvalidRecipeError
from draftsman.warning import ModuleLimitationWarning, ItemLimitationWarning

from schema import SchemaError
import six
import warnings


class RecipeMixin(object):
    """
    TODO
    """

    def __init__(self, name, similar_entities, **kwargs):
        # type: (str, list[str], **dict) -> None
        super(RecipeMixin, self).__init__(name, similar_entities, **kwargs)

        # List of all recipes that this machine can make
        self._recipes = recipes.for_machine[self.name]

        # Recipe that this machine is currently set to
        self.recipe = None
        if "recipe" in kwargs:
            self.recipe = kwargs["recipe"]
            self.unused_args.pop("recipe")
        self._add_export("recipe", lambda x: x is not None)

    # =========================================================================

    @property
    def recipes(self):
        # type: () -> list
        """
        Read only
        TODO
        """
        return self._recipes

    # =========================================================================

    @property
    def recipe(self):
        # type: () -> str
        """
        TODO
        """
        return self._recipe

    @recipe.setter
    def recipe(self, value):
        # type: (str) -> None
        if value is None:
            self._recipe = None
            return

        try:
            value = signatures.STRING.validate(value)
        except SchemaError as e:
            six.raise_from(TypeError(e), None)

        if value in self.recipes:
            self._recipe = value
        else:
            raise InvalidRecipeError(
                "'{}' not in this entity's valid recipes".format(value)
            )

        # I'm gonna put this here, this technically only applies to
        # AssemblingMachine but technically this whole mixin only applies to
        # AssemblingMachine
        # Later on there might be a reason to split this out but this is
        # good enough for now

        # Check to make sure the recipe matches the module specification
        if self.items:
            for item in self.items:
                # If the item is a module
                if item in modules.raw:
                    module = modules.raw[item]
                    # Check to see if the module is allowed with this recipe
                    if "limitation" in module:
                        if self.recipe not in module["limitation"]:
                            warnings.warn(
                                "Cannot use module '{}' with new recipe '{}'".format(
                                    item, self.recipe
                                ),
                                ModuleLimitationWarning,
                                stacklevel=2,
                            )
                elif item not in recipes.get_recipe_ingredients(self.recipe):
                    warnings.warn(
                        "Item '{}' is not used in the current recipe ({})".format(
                            item, self.recipe
                        ),
                        ItemLimitationWarning,
                        stacklevel=2,
                    )
