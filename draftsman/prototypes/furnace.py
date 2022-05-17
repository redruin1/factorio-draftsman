# furnace.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import ModulesMixin, RequestItemsMixin
from draftsman import utils
from draftsman.warning import DraftsmanWarning, ItemLimitationWarning

from draftsman.data.entities import furnaces, raw
from draftsman.data import modules, recipes

import warnings


class Furnace(ModulesMixin, RequestItemsMixin, Entity):
    """
    An entity that takes a fuel and an input item and creates an output item.
    """

    def __init__(self, name=furnaces[0], **kwargs):
        # type: (str, **dict) -> None
        super(Furnace, self).__init__(name, furnaces, **kwargs)

        # Create a set of valid ingredients for this entity
        crafting_categories = raw[self.name]["crafting_categories"]
        total_recipes = []
        for crafting_category in crafting_categories:
            total_recipes.extend(recipes.categories[crafting_category])

        self._valid_input_ingredients = set()
        for name in total_recipes:
            self._valid_input_ingredients.update(recipes.get_recipe_ingredients(name))

        # Get a set of valid fuel items for this entity
        # self._valid_fuel_items = set()
        # energy_source = raw[self.name]["energy_source"]

        for unused_arg in self.unused_args:
            warnings.warn(
                "{} has no attribute '{}'".format(type(self), unused_arg),
                DraftsmanWarning,
                stacklevel=2,
            )

    # =========================================================================

    @property
    def valid_input_ingredients(self):
        # type: () -> set
        """
        A set of strings, each one an ingredient that can be used as a input for
        some recipe. Not exported; read only.

        :type: ``set{str}``
        """
        return self._valid_input_ingredients

    # =========================================================================

    @utils.reissue_warnings
    def set_item_request(self, item, count):
        # type: (str, int) -> None
        if item not in modules.raw and item not in self.valid_input_ingredients:
            warnings.warn(
                "Cannot request items that this Furnace doesn't use ({})".format(item),
                ItemLimitationWarning,
                stacklevel=2,
            )

        # TODO: handle fuel input items

        # self._handle_module_slots(item, count)

        super(Furnace, self).set_item_request(item, count)
