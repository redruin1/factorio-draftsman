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

    .. code-block:: text

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

.. py:data:: fluid

    A list of all fluid signal names, sorted by their Factorio order.

.. py:data:: virtual

    A list of all virtual signal names, sorted by their Factorio order.

.. autofunction:: get_signal_type

.. autofunction:: signal_dict