.. py:currentmodule:: draftsman.data.entities

:py:mod:`~draftsman.data.entities`
==================================

.. py:data:: raw

    A dictionary indexed with all entities known to Draftsman's environment, 
    as well as their prototype definitions. This dict contains all entities, 
    regardless of type, which provides a convenient place to query data 
    about any entity.

    :example:

    .. code-block:: python

        import json
        from draftsman.data import entities

        print(entities.raw["small-electric-pole"])

    .. code-block:: python

        # Note: not all key-value pairs are represented for brevity
        {
            "fast_replaceable_group": "electric-pole",
            "collision_box": [
                [
                    -0.15,
                    -0.15
                ],
                [
                    0.15,
                    0.15
                ]
            ],
            "name": "small-electric-pole",
            "flags": [
                "placeable-neutral",
                "player-creation",
                "fast-replaceable-no-build-while-moving"
            ],
            "type": "electric-pole",
            "dying_explosion": "small-electric-pole-explosion",
            "minable": {
                "result": "small-electric-pole",
                "mining_time": 0.1
            },
            "icon_size": 64,
            "selection_box": [
                [
                    -0.4,
                    -0.4
                ],
                [
                    0.4,
                    0.4
                ]
            ],
            "track_coverage_during_build_by_moving": True,
            "corpse": "small-electric-pole-remnants",
            "connection_points": [...],
            "icon": "__base__/graphics/icons/small-electric-pole.png",
            "supply_area_distance": 2.5,
            "maximum_wire_distance": 7.5,
            "max_health": 100,
            "order": "a[energy]-a[small-electric-pole]",
            "subgroup": "energy-pipe-distribution"
            # and so on
            # ...
        }

    .. seealso::

        `<https://lua-api.factorio.com/latest/prototypes/EntityPrototype.html>`_
