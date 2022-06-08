.. py:currentmodule:: draftsman.data.signals

:py:mod:`~draftsman.data.signals`
=================================

.. py:data:: raw

    A ``dict`` of all signals where the key is the name of the signal and the value is the type of the signal.

    :example:

    .. code-block:: python

        import json
        from draftsman.data import signals

        print(json.dumps(signals.raw, indent=4))

    .. code-block:: python

        {
            "hazard-concrete": "item",
            "electronic-circuit": "item",
            "heat-exchanger": "item",
            "processing-unit": "item",
            "nuclear-reactor": "item",
            "uranium-235": "item",
            "train-stop": "item",
            "steam-engine": "item",
            "substation": "item",
            "sulfur": "item",
            "crude-oil-barrel": "item",
            ...
        }

.. py:data:: item

    A list of all item signal names, sorted by their Factorio order.
    Dependent on mods.

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
    Dependent on mods.

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
    Dependent on mods.

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