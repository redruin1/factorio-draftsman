.. py:currentmodule:: draftsman.data.modules

:py:mod:`~draftsman.data.modules`
=================================

.. py:data:: raw

    A ``dict`` of all modules indexed by their name.

    .. seealso::

        | `<https://wiki.factorio.com/Data.raw#module>`_
        | `<https://wiki.factorio.com/Prototype/Module>`_

    :example:

    .. code-block:: python

        import json
        from draftsman.data import modules

        print(json.dumps(modules.raw["productivity-module-3"], indent=4))

    .. code-block:: text

        {
            "type": "module",
            "icon_mipmaps": 4,
            "effect": {
                "consumption": {
                    "bonus": 0.8
                },
                "productivity": {
                    "bonus": 0.1
                },
                "speed": {
                    "bonus": -0.15
                },
                "pollution": {
                    "bonus": 0.1
                }
            },
            "stack_size": 50,
            "localised_description": [
                "item-description.productivity-module"
            ],
            "limitation_message_key": "production-module-usable-only-on-intermediates",
            "limitation": [
                "sulfuric-acid",
                "basic-oil-processing",
                "advanced-oil-processing",
                "coal-liquefaction",
                "heavy-oil-cracking",
                "light-oil-cracking",
                "solid-fuel-from-light-oil",
                "solid-fuel-from-heavy-oil",
                "solid-fuel-from-petroleum-gas",
                "lubricant",
                "iron-plate",
                "copper-plate",
                "steel-plate",
                "stone-brick",
                "sulfur",
                "plastic-bar",
                "empty-barrel",
                "uranium-processing",
                "copper-cable",
                "iron-stick",
                "iron-gear-wheel",
                "electronic-circuit",
                "advanced-circuit",
                "processing-unit",
                "engine-unit",
                "electric-engine-unit",
                "uranium-fuel-cell",
                "explosives",
                "battery",
                "flying-robot-frame",
                "low-density-structure",
                "rocket-fuel",
                "nuclear-fuel",
                "nuclear-fuel-reprocessing",
                "rocket-control-unit",
                "rocket-part",
                "automation-science-pack",
                "logistic-science-pack",
                "chemical-science-pack",
                "military-science-pack",
                "production-science-pack",
                "utility-science-pack",
                "kovarex-enrichment-process"
            ],
            "order": "c[productivity]-c[productivity-module-3]",
            "tier": 3,
            "category": "productivity",
            "icon_size": 64,
            "subgroup": "module",
            "icon": "__base__/graphics/icons/productivity-module-3.png",
            "name": "productivity-module-3"
        }

.. py:data:: categories

    A ``dict`` of lists of each module category. Exists in the format:

    .. code-block:: python

        {
            "module_type": [
                "module-name-1",
                "module-name-2",
                "module-name-3"
            ],
            # ...
        }

    .. seealso::

        | `<https://wiki.factorio.com/Data.raw#module-category>`_
        | `<https://wiki.factorio.com/Prototype/ModuleCategory>`_

    :example:

    .. code-block:: python

        import json
        from draftsman.data import modules

        print(json.dumps(modules.categories, indent=4))

    .. code-block:: text

        {
            "productivity": [
                "productivity-module-2",
                "productivity-module",
                "productivity-module-3"
            ],
            "effectivity": [
                "effectivity-module-3",
                "effectivity-module-2",
                "effectivity-module"
            ],
            "speed": [
                "speed-module-3",
                "speed-module-2",
                "speed-module"
            ]
        }