# test_recipes.py

from draftsman.data import recipes

import pytest


class TestRecipeData:
    def test_add_recipe(self):
        # TODO: complete
        with pytest.raises(NotImplementedError):
            recipes.add_recipe("new-recipe", [["iron-ore", 5]], "new-item")

    def test_get_recipe_ingredients(self):
        # Normal, list-type
        assert recipes.get_recipe_ingredients("wooden-chest") == {"wood"}
        # Normal, dict-type
        assert recipes.get_recipe_ingredients("plastic-bar") == {
            "petroleum-gas",
            "coal",
        }
        # Expensive, list-type
        assert recipes.get_recipe_ingredients("iron-gear-wheel") == {"iron-plate"}
        # Custom examples
        recipes.raw["test-1"] = {"ingredients": [["iron-plate", 2]]}
        assert recipes.get_recipe_ingredients("test-1") == {"iron-plate"}
        recipes.raw["test-2"] = {"normal": {"ingredients": [{"name": "iron-plate"}]}}
        assert recipes.get_recipe_ingredients("test-2") == {"iron-plate"}
