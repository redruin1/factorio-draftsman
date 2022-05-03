.. py:currentmodule:: draftsman.data.entities

:py:mod:`~draftsman.data.entities`
==================================

.. py:data:: raw

    A dictionary indexed with all of the valid entity names.
    The dict contains all entities, regardless of type, which provides a convenient place to query data about any entity.

    .. seealso::

        `<https://wiki.factorio.com/Prototype/Entity>`_

    .. code-block:: python

        import json
        from draftsman.data import entities

        print(json.dumps(entities.raw["small-electric-pole"], indent=4))

    .. code-block:: text

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
            "track_coverage_during_build_by_moving": true,
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

--------------------------------------------------------------------------------

.. py:data:: containers

    A sorted list of all instances of :py:class:`.Container`.

.. py:data:: storage_tanks

    A sorted list of all instances of :py:class:`.StorageTank`.

.. py:data:: transport_belts

    A sorted list of all instances of :py:class:`.TransportBelt`.

.. py:data:: underground_belts

    A sorted list of all instances of :py:class:`.UndergroundBelt`.

.. py:data:: splitters

    A sorted list of all instances of :py:class:`.Splitter`.

.. py:data:: inserters

    A sorted list of all instances of :py:class:`.Inserter`.

.. py:data:: filter_inserters

    A sorted list of all instances of :py:class:`.FilterInserter`.

.. py:data:: loaders

    A sorted list of all instances of :py:class:`.Loader`.

.. py:data:: electric_poles

    A sorted list of all instances of :py:class:`.ElectricPole`.

.. py:data:: pipes

    A sorted list of all instances of :py:class:`.Pipe`.

.. py:data:: underground_pipes

    A sorted list of all instances of :py:class:`.UndergroundPipe`.

.. py:data:: pumps

    A sorted list of all instances of :py:class:`.Pump`.

.. py:data:: straight_rails

    A sorted list of all instances of :py:class:`.StraightRail`.

.. py:data:: curved_rails

    A sorted list of all instances of :py:class:`.CurvedRail`.

.. py:data:: train_stops

    A sorted list of all instances of :py:class:`.TrainStop`.

.. py:data:: rail_signals

    A sorted list of all instances of :py:class:`.RailSignal`.

.. py:data:: rail_chain_signals

    A sorted list of all instances of :py:class:`.RailChainSignal`.

.. py:data:: locomotives

    A sorted list of all instances of :py:class:`.Locomotive`.

.. py:data:: cargo_wagons

    A sorted list of all instances of :py:class:`.CargoWagon`.

.. py:data:: fluid_wagons

    A sorted list of all instances of :py:class:`.FluidWagon`.

.. py:data:: artillery_wagons

    A sorted list of all instances of :py:class:`.ArtilleryWagon`.

.. py:data:: logistic_passive_containers

    A sorted list of all instances of :py:class:`.LogisticPassiveContainer`.

.. py:data:: logistic_active_containers

    A sorted list of all instances of :py:class:`.LogisticActiveContainer`.

.. py:data:: logistic_storage_containers

    A sorted list of all instances of :py:class:`.LogisticStorageContainer`.

.. py:data:: logistic_buffer_containers

    A sorted list of all instances of :py:class:`.LogisticBufferContainer`.

.. py:data:: logistic_request_containers

    A sorted list of all instances of :py:class:`.LogisticRequestContainer`.

.. py:data:: roboports

    A sorted list of all instances of :py:class:`.Roboports`.

.. py:data:: lamps

    A sorted list of all instances of :py:class:`.Lamp`.

.. py:data:: arithmetic_combinators

    A sorted list of all instances of :py:class:`.ArithmeticCombinator`.

.. py:data:: decider_combinators

    A sorted list of all instances of :py:class:`.DeciderCombinator`.

.. py:data:: constant_combinators

    A sorted list of all instances of :py:class:`.ConstantCombinator`.

.. py:data:: power_switches

    A sorted list of all instances of :py:class:`.PowerSwitch`.

.. py:data:: programmable_speakers

    A sorted list of all instances of :py:class:`.ProgrammableSpeaker`.

.. py:data:: boilers

    A sorted list of all instances of :py:class:`.Boiler`.
    Boilers convert a fuel to heat a fluid (usually water) into another (usually steam).

.. py:data:: generators

    A sorted list of all instances of :py:class:`.Generator`.
    Generators convert a fluid (usually steam) into electricity.

.. py:data:: solar_panels

    A sorted list of all instances of :py:class:`.SolarPanel`.

.. py:data:: accumulators

    A sorted list of all instances of :py:class:`.Accumulator`.

.. py:data:: reactors

    A sorted list of all instances of :py:class:`.Reactor`.

.. py:data:: heat_pipes

    A sorted list of all instances of :py:class:`.HeatPipe`.

.. py:data:: mining_drills

    A sorted list of all instances of :py:class:`.MiningDrill`.
    This includes pumpjacks and any other extraction machine.

.. py:data:: offshore_pumps

    A sorted list of all instances of :py:class:`.OffshorePump`.

.. py:data:: furnaces

    A sorted list of all instances of :py:class:`.Furnaces`.

.. py:data:: assembling_machines

    A sorted list of all instances of :py:class:`.AssemblingMachine`.
    This includes chemical plants, oil refineries, and centrifuges.

.. py:data:: labs

    A sorted list of all instances of :py:class:`.Lab`.

.. py:data:: beacons

    A sorted list of all instances of :py:class:`.Beacon`.

.. py:data:: rocket_silos

    A sorted list of all instances of :py:class:`.RocketSilo`.

.. py:data:: land_mines

    A sorted list of all instances of :py:class:`.LandMine`.

.. py:data:: walls

    A sorted list of all instances of :py:class:`.Wall`.

.. py:data:: gates

    A sorted list of all instances of :py:class:`.Gate`.

.. py:data:: turrets

    A sorted list of all instances of :py:class:`.Turret`.
    Includes the contents of Factorio's ``AmmoTurret``, ``EnergyTurret``, ``FluidTurret``, and ``ArtilleryTurret``.

.. py:data:: radars

    A sorted list of all instances of :py:class:`.Radar`.

.. py:data:: electric_energy_interfaces

    A sorted list of all instances of :py:class:`.ElectricEnergyInterface`.

.. py:data:: linked_containers

    A sorted list of all instances of :py:class:`.LinkedContainer`.

.. py:data:: heat_interfaces

    A sorted list of all instances of :py:class:`.HeatInterface`.

.. py:data:: linked_belts

    A sorted list of all instances of :py:class:`.LinkedBelt`.

.. py:data:: infinity_containers

    A sorted list of all instances of :py:class:`.InfinityContainer`.

.. py:data:: infinity_pipes

    A sorted list of all instances of :py:class:`.InfinityPipe`.

.. py:data:: burner_generators

    A sorted list of all instances of :py:class:`.BurnerGenerator`.