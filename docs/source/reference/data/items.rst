.. py:currentmodule:: draftsman.data.items

:py:mod:`~draftsman.data.items`
===============================

.. py:data:: items.raw

    A dictionary indexed with all of the valid item names.
    Provides a convenient place to query data about any item.

    :example:

    .. code-block:: python

        import json
        from draftsman.data import items

        print(json.dumps(items.raw["transport-belt"], indent=4))

    .. code-block:: text

        {
            "stack_size": 100,
            "type": "item",
            "name": "transport-belt",
            "icon_size": 64,
            "order": "a[transport-belt]-a[transport-belt]",
            "place_result": "transport-belt",
            "subgroup": "belt",
            "icon": "__base__/graphics/icons/transport-belt.png",
            "icon_mipmaps": 4
        }

.. py:data:: items.subgroups

    A dict of all item subgroups. Each entry is of the format:

    .. code-block:: python

        {
            "name": "name of the subgroup"
            "type": "type of the subgroup"
            "order": "order string of the subgroup"
            "group": "name of the group this subgroup belongs to"
            "items": {...} # Dict of items entries in this subgroup
        }

    :example:

    .. code-block:: python

        from draftsman.data import items

        for belt in items.subgroups["belt"]["items"]:
            print(belt)

    .. code-block:: text

        transport-belt
        fast-transport-belt
        express-transport-belt
        underground-belt
        fast-underground-belt
        express-underground-belt
        splitter
        fast-splitter
        express-splitter
        loader
        fast-loader
        express-loader        

.. py:data:: items.groups

    A dict of all item groups. Each entry is of the format:

    .. code-block:: python

        {
            "name": "name of the group"
            "type": "type of the group"
            "icon_size": "size of the icon image"
            "icon": "icon used on the crafting menu"
            "icon_mipmaps": "number of mipmaps"
            "order": "order string of the subgroup"
            "subgroups": {...} # Dict of subgroups in this group
        }

    :example:

    .. code-block:: python

        from draftsman.data import items

        for subgroup in items.group["logistics"]["subgroups"]:
            print(subgroup)

    .. code-block:: text

        storage
        belt
        inserter
        energy-pipe-distribution
        train-transport
        transport
        logistic-network
        circuit-network
        terrain  