.. py:currentmodule:: draftsman.data.signals

:py:mod:`~draftsman.data.signals`
=================================

.. py:data:: raw

    An ``OrderedDict`` of all signals extracted from ``data.raw``, sorted by the signal processing order.
    The signal processing order is the sorted virtual signals, followed by the sorted fluid signals, followed by all the sorted item signals.
    The order of signals in ``signals.raw`` can be considered equivalent to ``signals.virtual + signals.fluid + signals.item``.
    The exact format of the data depends on what type of item/fluid/signal is being queried.
    Allows the user to iterate over all signals in order, and query specific properties about them, such as their order string for custom sorting orders.
    Order and content are dependent on loaded mods.

    :example:

    .. code-block:: python

        import json
        from draftsman.data import signals

        print(json.dumps(signals.raw["iron-ore"], indent=4))

    .. code-block:: python

        {
            "order": "e[iron-ore]",
            "pictures": [ ... ],
            "stack_size": 50,
            "type": "item",
            "icon_mipmaps": 4,
            "name": "iron-ore",
            "icon": "__base__/graphics/icons/iron-ore.png",
            "subgroup": "raw-resource",
            "icon_size": 64
        }

.. py:data:: type_of

    A ``dict`` of all signals where the key is the name of the signal and the value is the *signal* type of the signal.
    Note that this value may differ from the value of ``signals.raw[signal_name]["type"]``; this value is used specifically during the construction of :py:data:`.SIGNAL_ID`.
    The returned value can be one of ``"item"``, ``"fluid"``, or ``"virtual"``.
    Order is dependent on loaded mods.

    .. NOTE::

        This structure is **unsorted**. If you want to iterate over signals in order, consider using ``signals.raw`` instead:

        .. code-block:: python

            from draftsman.data import signals

            for signal_name in signals.raw:
                print(signals.type_of[signal_name])

.. py:data:: item

    A list of all item signal names, sorted by their Factorio order.
    Order and content are dependent on mods.

    .. code-block:: python

        # Possible contents
        [
            "wooden-chest",
            "iron-chest",
            "steel-chest",
            "storage-tank",
            "transport-belt",
            "fast-transport-belt",
            "express-transport-belt",
            "underground-belt",
            "fast-underground-belt",
            "express-underground-belt",
            ...
        ]

.. py:data:: fluid

    A list of all fluid signal names, sorted by their Factorio order.
    Order and content are dependent on loaded mods.

    .. code-block:: python

        # Possible contents
        [
            "water",
            "crude-oil",
            "steam",
            "heavy-oil",
            "light-oil",
            "petroleum-gas",
            "sulfuric-acid",
            "lubricant"
        ]

.. py:data:: virtual

    A list of all virtual signal names, sorted by their Factorio order.
    Order and content are dependent on loaded mods.

    .. code-block:: python

        # Possible contents
        [
            "signal-everything",
            "signal-anything",
            "signal-each",
            "signal-0",
            "signal-1",
            "signal-2",
            "signal-3",
            "signal-4",
            "signal-5",
            "signal-6",
            ...
        ]

    .. NOTE::

        ``signals.virtual`` contains the signals in ``signals.pure_virtual``,
        as illustrated above.

.. py:data:: pure_virtual

    A list of all pure virtual signal names, sorted by their Factorio order.
    This list is constant, independent of mods, and is always equivalent to:

    .. code-block:: python

        ["signal-everything", "signal-anything", "signal-each"]

.. autofunction:: get_signal_type

.. autofunction:: signal_dict