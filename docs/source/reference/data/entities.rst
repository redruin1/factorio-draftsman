.. py:currentmodule:: draftsman.data.entities

:py:mod:`~draftsman.data.entities`
==================================

.. py:data:: entities.raw

    A dictionary indexed with all of the valid entity names.
    The dict contains all entities, regardless of type, which provides a convenient place to query data about any entity.

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

.. py:data:: entities.containers

    A sorted list of all instances of :py:class:`.Container`.

.. py:data:: entities.storage_tanks

    A sorted list of all instances of :py:class:`.StorageTank`.

.. py:data:: entities.transport_belts

    A sorted list of all instances of :py:class:`.TransportBelt`.

.. py:data:: entities.underground_belts

    A sorted list of all instances of :py:class:`.UndergroundBelt`.

.. py:data:: entities.splitters

    A sorted list of all instances of :py:class:`.Splitter`.

.. py:data:: entities.inserters

    A sorted list of all instances of :py:class:`.Inserter`.

.. py:data:: entities.filter_inserters

    A sorted list of all instances of :py:class:`.FilterInserter`.

.. py:data:: entities.loaders

    A sorted list of all instances of :py:class:`.Loader`.

.. py:data:: entities.electric_poles

    A sorted list of all instances of :py:class:`.ElectricPole`.

.. py:data:: entities.pipes

    A sorted list of all instances of :py:class:`.Pipe`.

.. py:data:: entities.underground_pipes

    A sorted list of all instances of :py:class:`.UndergroundPipe`.

.. py:data:: entities.pumps

    A sorted list of all instances of :py:class:`.Pump`.

.. py:data:: entities.straight_rails

    A sorted list of all instances of :py:class:`.StraightRail`.

.. py:data:: entities.curved_rails

    A sorted list of all instances of :py:class:`.CurvedRail`.

.. py:data:: entities.train_stops

    A sorted list of all instances of :py:class:`.TrainStop`.

.. py:data:: entities.rail_signals

    A sorted list of all instances of :py:class:`.RailSignal`.

.. py:data:: entities.rail_chain_signals

    A sorted list of all instances of :py:class:`.RailChainSignal`.

.. py:data:: entities.locomotives

    A sorted list of all instances of :py:class:`.Locomotive`.

.. py:data:: entities.cargo_wagons

    A sorted list of all instances of :py:class:`.CargoWagon`.

.. py:data:: entities.fluid_wagons

    A sorted list of all instances of :py:class:`.FluidWagon`.

.. py:data:: entities.artillery_wagons

    A sorted list of all instances of :py:class:`.ArtilleryWagon`.

.. py:data:: entities.logistic_passive_containers

    A sorted list of all instances of :py:class:`.LogisticPassiveContainer`.

.. py:data:: entities.logistic_active_containers

    A sorted list of all instances of :py:class:`.LogisticActiveContainer`.

.. py:data:: entities.logistic_storage_containers

    A sorted list of all instances of :py:class:`.LogisticStorageContainer`.

.. py:data:: entities.logistic_buffer_containers

    A sorted list of all instances of :py:class:`.LogisticBufferContainer`.

.. py:data:: entities.logistic_request_containers

    A sorted list of all instances of :py:class:`.LogisticRequestContainer`.

.. py:data:: entities.roboports

    A sorted list of all instances of :py:class:`.Roboports`.

.. py:data:: entities.lamps

    A sorted list of all instances of :py:class:`.Lamp`.

.. py:data:: entities.arithmetic_combinators

    A sorted list of all instances of :py:class:`.ArithmeticCombinator`.

.. py:data:: entities.decider_combinators

    A sorted list of all instances of :py:class:`.DeciderCombinator`.

.. py:data:: entities.constant_combinators

    A sorted list of all instances of :py:class:`.ConstantCombinator`.

.. py:data:: entities.power_switches

    A sorted list of all instances of :py:class:`.PowerSwitch`.

.. py:data:: entities.programmable_speakers

    A sorted list of all instances of :py:class:`.ProgrammableSpeaker`.

.. py:data:: entities.boilers

    A sorted list of all instances of :py:class:`.Boiler`.
    Boilers convert a fuel to heat a fluid (usually water) into another (usually steam).

.. py:data:: entities.generators

    A sorted list of all instances of :py:class:`.Generator`.
    Generators convert a fluid (usually steam) into electricity.

.. py:data:: entities.solar_panels

    A sorted list of all instances of :py:class:`.SolarPanel`.

.. py:data:: entities.accumulators

    A sorted list of all instances of :py:class:`.Accumulator`.

.. py:data:: entities.reactors

    A sorted list of all instances of :py:class:`.Reactor`.

.. py:data:: entities.heat_pipes

    A sorted list of all instances of :py:class:`.HeatPipe`.

.. py:data:: entities.mining_drills

    A sorted list of all instances of :py:class:`.MiningDrill`.
    This includes pumpjacks and any other extraction machine.

.. py:data:: entities.offshore_pumps

    A sorted list of all instances of :py:class:`.OffshorePump`.

.. py:data:: entities.furnaces

    A sorted list of all instances of :py:class:`.Furnaces`.

.. py:data:: entities.assembling_machines

    A sorted list of all instances of :py:class:`.AssemblingMachine`.
    This includes chemical plants, oil refineries, and centrifuges.

.. py:data:: entities.labs

    A sorted list of all instances of :py:class:`.Lab`.

.. py:data:: entities.beacons

    A sorted list of all instances of :py:class:`.Beacon`.

.. py:data:: entities.rocket_silos

    A sorted list of all instances of :py:class:`.RocketSilo`.

.. py:data:: entities.land_mines

    A sorted list of all instances of :py:class:`.LandMine`.

.. py:data:: entities.walls

    A sorted list of all instances of :py:class:`.Wall`.

.. py:data:: entities.gates

    A sorted list of all instances of :py:class:`.Gate`.

.. py:data:: entities.turrets

    A sorted list of all instances of :py:class:`.Turret`.
    Includes the contents of Factorio's ``AmmoTurret``, ``EnergyTurret``, ``FluidTurret``, and ``ArtilleryTurret``.

.. py:data:: entities.radars

    A sorted list of all instances of :py:class:`.Radar`.

.. py:data:: entities.electric_energy_interfaces

    A sorted list of all instances of :py:class:`.ElectricEnergyInterface`.

.. py:data:: entities.linked_containers

    A sorted list of all instances of :py:class:`.LinkedContainer`.

.. py:data:: entities.heat_interfaces

    A sorted list of all instances of :py:class:`.HeatInterface`.

.. py:data:: entities.linked_belts

    A sorted list of all instances of :py:class:`.LinkedBelt`.

.. py:data:: entities.infinity_containers

    A sorted list of all instances of :py:class:`.InfinityContainer`.

.. py:data:: entities.infinity_pipes

    A sorted list of all instances of :py:class:`.InfinityPipe`.

.. py:data:: entities.burner_generators

    A sorted list of all instances of :py:class:`.BurnerGenerator`.