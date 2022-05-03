.. py:currentmodule:: draftsman.data.tiles

:py:mod:`~draftsman.data.tiles`
===============================

.. py:data:: raw

    A ``dict`` of all tiles indexed by their names. 
    Equivalent to the values in Factorio's ``data.raw``.

    .. seealso::

        | `<https://wiki.factorio.com/Data.raw#tile>`_
        | `<https://wiki.factorio.com/Prototype/Tile>`_

    :example:

    .. code-block:: python

        import json
        from draftsman.data import tiles

        print(json.dumps(tiles.raw["landfill"], indent=4))

    .. code-block:: text

        {
            # An EXCEEDING amount of data
        }