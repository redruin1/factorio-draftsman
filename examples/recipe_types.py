# recipe_types.py
"""
Extracts different types of recipes into logical data structures and displays
their contents to stdout.
"""

from draftsman.data import planets, recipes
from draftsman.entity import AssemblingMachine


def main():
    # All recipes where productivity modules are allowed
    productivity_recipes = {}
    # All recipes where quality modules are allowed
    quality_recipes = {}
    # Recipes allowed on specific planets
    planet_recipes = {planet_name: {} for planet_name in planets.raw}

    for recipe_name, recipe in recipes.raw.items():
        if "allow_quality" in recipe:
            productivity_recipes[recipe_name] = recipe
        if "allow_quality" in recipe:
            quality_recipes[recipe_name] = recipe
        for planet_name, planet in planets.raw.items():
            if recipes.is_usable_on(recipe, planet):
                planet_recipes[planet_name][recipe_name] = recipe

    print("\t", productivity_recipes.keys())
    print("\t", quality_recipes.keys())
    for planet_name in planet_recipes:
        print("\t{}:\t{}".format(planet_name, planet_recipes[planet_name].keys()))

    # Recipes available for crafting in machines separately
    print("\t", recipes.for_machine["assembling-machine-1"])
    # or, equivalently:
    machine = AssemblingMachine("assembling-machine-1")
    assert machine.allowed_recipes == recipes.for_machine[machine.name]


if __name__ == "__main__":
    main()
