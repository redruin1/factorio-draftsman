.. py:currentmodule:: draftsman.data.recipes

:py:mod:`~draftsman.data.recipes`
=================================

.. py:data:: raw

    A collection of all recipes indexed by their name.

    .. seealso::

        | `<https://wiki.factorio.com/Data.raw#recipe>`_
        | `<https://wiki.factorio.com/Prototype/Recipe>`_

    :example:

    .. code-block:: python

        import json
        from draftsman.data import recipes

        print(json.dumps(recipes.raw["iron-plate"], indent=4))

    .. code-block:: text

        {
            "type": "recipe",
            "ingredients": [
                [
                    "iron-ore",
                    1
                ]
            ],
            "result": "iron-plate",
            "energy_required": 3.2,
            "category": "smelting",
            "name": "iron-plate"
        }

.. py:data:: categories

    A ``dict`` of lists of valid recipes organized by their category.
    Exists as the format:

    .. seealso::

        | `<https://wiki.factorio.com/Data.raw#recipe-category>`_
        | `<https://wiki.factorio.com/Prototype/RecipeCategory>`_

    .. code-block:: python

        {
            "category_name": [
                "recipe_1",
                "recipe_2",
                # ...
            ],
            # ...
        }

    :example:

    .. code-block:: python

        import json
        from draftsman.data import recipes

        print(json.dumps(recipes.categories["centrifuging"], indent=4))

    .. code-block:: text

        [
            "uranium-processing",
            "nuclear-fuel",
            "nuclear-fuel-reprocessing",
            "kovarex-enrichment-process"
        ]

.. py:data:: for_machine

    A ``dict`` of lists of valid recipes for each :py:class:`.AssemblingMachine`.
    Exists as the format:

    .. code-block:: python

        {
            "machine_name" : [
                "recipe_1",
                "recipe_2",
                # ...
            ],
            # ...
        }

    :example:

    .. code-block:: python

        import json
        from draftsman.data import recipes

        print(json.dumps(recipes.for_machine["oil-refinery"], indent=4))

    .. code-block:: text

        [
            "advanced-oil-processing",
            "coal-liquefaction",
            "basic-oil-processing"
        ]

.. autofunction:: get_recipe_ingredients