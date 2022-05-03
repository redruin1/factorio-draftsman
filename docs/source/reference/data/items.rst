.. py:currentmodule:: draftsman.data.items

:py:mod:`~draftsman.data.items`
===============================

.. py:data:: raw

    A ``dict`` indexed with all of the valid item *signal* names.
    Provides a convenient place to query data about almost every item.

    .. NOTE::

        Factorio has a lot of "items", and they're spread out over multiple different prototype categories.
        Draftsman accumulates all of the placable items and any item that can be used as a signal.
        This includes all production items, as well as items like ``rail-planner``, ``"blueprint``, ``upgrade-planner``, etc.
        There are however a number of more abstract items (usually used for modding) that are *not* included, such as ``item-with-label``, ``item-with-tags``, ``item-with-entity-data`` and any other generic template item that cannot be manifested inside a blueprint.

    .. seealso::

        | `<https://wiki.factorio.com/Data.raw#item>`_
        | `<https://wiki.factorio.com/Prototype/Item>`_

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

.. py:data:: subgroups

    A ``dict`` of all item subgroups.
    Each entry is equivalent to Factorio's ``data.raw``, except for an extra ``"items"`` key which holds a dictionary of all items that this group holds.

    .. seealso::

        | `<https://wiki.factorio.com/Data.raw#item-subgroup>`_
        | `<https://wiki.factorio.com/Prototype/ItemSubGroup>`_

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

.. py:data:: groups

    A ``dict`` of all item groups. 
    Each entry is equivalent to Factorio's ``data.raw``, except for an extra ``"subgroups"`` key which holds a dictionary of all subgroups that this group holds.

    .. seealso::

        | `<https://wiki.factorio.com/Data.raw#item-group>`_
        | `<https://wiki.factorio.com/Prototype/ItemGroup>`_

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