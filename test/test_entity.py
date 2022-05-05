# entity.py
# -*- encoding: utf-8 -*-

from draftsman.blueprintable import *
from draftsman.constants import *
from draftsman.entity import *
from draftsman.error import *
from draftsman.warning import *

from schema import SchemaError

import sys

if sys.version_info >= (3, 3):  # pragma: no coverage
    import unittest
else:  # pragma: no coverage
    import unittest2 as unittest


class EntityTesting(unittest.TestCase):
    def test_get_type(self):
        container = Container("wooden-chest")
        self.assertEqual(container.type, "container")

    def test_set_tags(self):
        container = Container("wooden-chest")
        container.tags = {"wee": 500, "hello": "world"}
        container.tags["addition"] = 1 + 1

        self.assertEqual(
            container.to_dict(),
            {
                "name": "wooden-chest",
                "position": {"x": 0.5, "y": 0.5},
                "tags": {"wee": 500, "hello": "world", "addition": 2},
            },
        )

        # Resetting tags to empty should omit it based on its lambda func
        container.tags = {}
        self.assertEqual(
            container.to_dict(),
            {
                "name": "wooden-chest",
                "position": {"x": 0.5, "y": 0.5},
            },
        )

        container.tags = None
        self.assertEqual(
            container.to_dict(),
            {
                "name": "wooden-chest",
                "position": {"x": 0.5, "y": 0.5},
            },
        )

        # Errors
        # Setting tags to anything other than a dict raises errors
        with self.assertRaises(TypeError):
            container.tags = "incorrect"

    def test_get_area(self):
        combinator = DeciderCombinator(tile_position=[3, 3], direction=Direction.EAST)
        self.assertEqual(combinator.get_area(), [[3.35, 3.15], [4.65, 3.85]])

    # def test_set_name(self):
    #     iron_chest = Container("iron-chest")
    #     iron_chest.name = "steel-chest"
    #     self.assertEqual(iron_chest.name, "steel-chest")

    #     with self.assertRaises(InvalidEntityError):
    #         iron_chest.name = "incorrect"

    def test_set_position(self):
        iron_chest = Container("iron-chest")
        iron_chest.position = (1.23, 1.34)
        self.assertAlmostEqual(iron_chest.position, {"x": 1.23, "y": 1.34})
        self.assertEqual(iron_chest.tile_position, {"x": 1, "y": 1})

        with self.assertRaises(ValueError):
            iron_chest.position = ("fish", 10)

        iron_chest.tile_position = (10, 10.1)  # should cast float to int
        self.assertEqual(iron_chest.tile_position, {"x": 10, "y": 10})
        self.assertAlmostEqual(iron_chest.position, {"x": 10.5, "y": 10.5})

        with self.assertRaises(TypeError):
            iron_chest.tile_position = (1.0, "raw-fish")

    # def test_repr(self):
    #     class TestEntity(Entity):
    #         def __init__(self, name, **kwargs):
    #             examples = ["loader", "other-loader"]
    #             super(TestEntity, self).__init__(name, examples, **kwargs)

    #     test = TestEntity("loader")
    #     self.assertEqual(
    #         str(test),
    #         "<TestEntity>{'name': 'loader', 'position': {'x': 0.5, 'y': 1.0}}"
    #     )

    # def test_change_name_in_blueprint(self):
    #     blueprint = Blueprint()
    #     example = Container("wooden-chest", id="whatever")
    #     blueprint.entities.append(example)
    #     self.assertEqual(blueprint.entities["whatever"].name, example.name)

    #     with self.assertRaises(DraftsmanError):
    #         blueprint.entities["whatever"].name = "steel-chest"

    def test_change_id_in_blueprint(self):
        blueprint = Blueprint()
        example = Container("wooden-chest", id="whatever")
        blueprint.entities.append(example)
        self.assertEqual(blueprint.entities["whatever"].name, example.name)

        blueprint.entities["whatever"].id = "something else"
        self.assertIs(blueprint.entities[0], blueprint.entities["something else"])
        self.assertEqual(blueprint.entities[0].id, "something else")
        with self.assertRaises(KeyError):
            blueprint.entities["whatever"]

        blueprint.entities["something else"].id = None
        self.assertEqual(blueprint.entities[0].id, None)
        with self.assertRaises(KeyError):
            blueprint.entities["something else"]
        with self.assertRaises(KeyError):
            blueprint.entities["whatever"]

        # Add a new entity and check for duplicate ID error
        blueprint.entities.append("wooden-chest", tile_position=(1, 0))
        blueprint.entities[0].id = "duplicate"
        with self.assertRaises(DuplicateIDError):
            blueprint.entities[1].id = "duplicate"

    def test_flippable(self):
        belt = TransportBelt()
        self.assertEqual(belt.flippable, True)


# =============================================================================
# Factory function new_entity()
# =============================================================================

# fmt: off
class EntityFactoryTesting(unittest.TestCase):
    def test_container(self):
        self.assertIsInstance(new_entity("wooden-chest"), Container)

    def test_storage_tank(self):
        self.assertIsInstance(new_entity("storage-tank"), StorageTank)

    def test_transport_belt(self):
        self.assertIsInstance(new_entity("transport-belt"), TransportBelt)

    def test_underground_belt(self):
        self.assertIsInstance(new_entity("underground-belt"), UndergroundBelt)

    def test_splitter(self):
        self.assertIsInstance(new_entity("splitter"), Splitter)

    def test_inserter(self):
        self.assertIsInstance(new_entity("burner-inserter"), Inserter)

    def test_filter_inserter(self):
        self.assertIsInstance(new_entity("filter-inserter"), FilterInserter)

    def test_loader(self):
        self.assertIsInstance(new_entity("loader"), Loader)

    def test_electric_pole(self):
        self.assertIsInstance(new_entity("small-electric-pole"), ElectricPole)

    def test_pipe(self):
        self.assertIsInstance(new_entity("pipe"), Pipe)

    def test_underground_pipe(self):
        self.assertIsInstance(new_entity("pipe-to-ground"), UndergroundPipe)

    def test_pump(self):
        self.assertIsInstance(new_entity("pump"), Pump)

    def test_straight_rail(self):
        self.assertIsInstance(new_entity("straight-rail"), StraightRail)

    def test_curved_rail(self):
        self.assertIsInstance(new_entity("curved-rail"), CurvedRail)

    def test_train_stop(self):
        self.assertIsInstance(new_entity("train-stop"), TrainStop)

    def test_rail_signal(self):
        self.assertIsInstance(new_entity("rail-signal"), RailSignal)

    def test_rail_chain_signal(self):
        self.assertIsInstance(new_entity("rail-chain-signal"), RailChainSignal)

    def test_locomotive(self):
        self.assertIsInstance(new_entity("locomotive"), Locomotive)

    def test_cargo_wagon(self):
        self.assertIsInstance(new_entity("cargo-wagon"), CargoWagon)

    def test_fluid_wagon(self):
        self.assertIsInstance(new_entity("fluid-wagon"), FluidWagon)

    def test_artillery_wagon(self):
        self.assertIsInstance(new_entity("artillery-wagon"), ArtilleryWagon)

    def test_logistic_passive_container(self):
        self.assertIsInstance(new_entity("logistic-chest-passive-provider"), LogisticPassiveContainer)

    def test_logistic_active_container(self):
        self.assertIsInstance(new_entity("logistic-chest-active-provider"), LogisticActiveContainer)

    def test_logistic_storage_container(self):
        self.assertIsInstance(new_entity("logistic-chest-storage"), LogisticStorageContainer)

    def test_logistic_buffer_container(self):
        self.assertIsInstance(new_entity("logistic-chest-buffer"), LogisticBufferContainer)

    def test_logistic_request_container(self):
        self.assertIsInstance(new_entity("logistic-chest-requester"), LogisticRequestContainer)

    def test_roboport(self):
        self.assertIsInstance(new_entity("roboport"), Roboport)

    def test_lamp(self):
        self.assertIsInstance(new_entity("small-lamp"), Lamp)

    def test_arithmetic_combinator(self):
        self.assertIsInstance(new_entity("arithmetic-combinator"), ArithmeticCombinator)

    def test_decider_combinator(self):
        self.assertIsInstance(new_entity("decider-combinator"), DeciderCombinator)

    def test_constant_combinator(self):
        self.assertIsInstance(new_entity("constant-combinator"), ConstantCombinator)

    def test_power_switch(self):
        self.assertIsInstance(new_entity("power-switch"), PowerSwitch)

    def test_programmable_speaker(self):
        self.assertIsInstance(new_entity("programmable-speaker"), ProgrammableSpeaker)

    def test_boiler(self):
        self.assertIsInstance(new_entity("boiler"), Boiler)

    def test_generator(self):
        self.assertIsInstance(new_entity("steam-engine"), Generator)

    def test_solar_panel(self):
        self.assertIsInstance(new_entity("solar-panel"), SolarPanel)

    def test_accumulator(self):
        self.assertIsInstance(new_entity("accumulator"), Accumulator)

    def test_reactor(self):
        self.assertIsInstance(new_entity("nuclear-reactor"), Reactor)

    def test_heat_pipe(self):
        self.assertIsInstance(new_entity("heat-pipe"), HeatPipe)

    def test_mining_drill(self):
        self.assertIsInstance(new_entity("burner-mining-drill"), MiningDrill)

    def test_offshore_pump(self):
        self.assertIsInstance(new_entity("offshore-pump"), OffshorePump)

    def test_furnace(self):
        self.assertIsInstance(new_entity("stone-furnace"), Furnace)

    def test_assembling_machine(self):
        self.assertIsInstance(new_entity("assembling-machine-1"), AssemblingMachine)

    def test_lab(self):
        self.assertIsInstance(new_entity("lab"), Lab)

    def test_beacon(self):
        self.assertIsInstance(new_entity("beacon"), Beacon)

    def test_rocket_silo(self):
        self.assertIsInstance(new_entity("rocket-silo"), RocketSilo)

    def test_land_mine(self):
        self.assertIsInstance(new_entity("land-mine"), LandMine)

    def test_wall(self):
        self.assertIsInstance(new_entity("stone-wall"), Wall)

    def test_gate(self):
        self.assertIsInstance(new_entity("gate"), Gate)

    def test_turret(self):
        self.assertIsInstance(new_entity("gun-turret"), Turret)

    def test_radar(self):
        self.assertIsInstance(new_entity("radar"), Radar)

    def test_electric_energy_interface(self):
        self.assertIsInstance(new_entity("electric-energy-interface"), ElectricEnergyInterface)

    @unittest.skipIf(len(linked_containers) == 0, "No linked containers to test")
    def test_linked_container(self):
        self.assertIsInstance(new_entity("linked-chest"), LinkedContainer)

    def test_heat_interface(self):
        self.assertIsInstance(new_entity("heat-interface"), HeatInterface)

    @unittest.skipIf(len(linked_belts) == 0, "No linked belts to test")
    def test_linked_belt(self):
        self.assertIsInstance(new_entity("linked-belt"), LinkedBelt)

    def test_infinity_container(self):
        self.assertIsInstance(new_entity("infinity-chest"), InfinityContainer)

    def test_infinity_pipe(self):
        self.assertIsInstance(new_entity("infinity-pipe"), InfinityPipe)

    def test_burner_generator(self):
        self.assertIsInstance(new_entity("burner-generator"), BurnerGenerator)

    def test_errors(self):
        self.assertRaises(
            InvalidEntityError,
            new_entity,
            "I have a lot of entities that I need to test...",
        )

# fmt: on
