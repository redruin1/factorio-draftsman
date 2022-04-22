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
    from unittest import TestCase
else:  # pragma: no coverage
    from unittest2 import TestCase


class EntityTesting(TestCase):
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

        with self.assertRaises(DraftsmanError):
            blueprint.entities["whatever"].id = "new_id"
        # self.assertIs(blueprint.entities["new_id"].name, example.name)

    def test_flippable(self):
        belt = TransportBelt()
        self.assertEqual(belt.flippable, True)


# =============================================================================
# Factory function new_entity()
# =============================================================================


class EntityFactoryTesting(TestCase):
    def test_new_entity(self):
        self.assertIsInstance(new_entity("wooden-chest"), Container)
        self.assertIsInstance(new_entity("storage-tank"), StorageTank)
        self.assertIsInstance(new_entity("transport-belt"), TransportBelt)
        self.assertIsInstance(new_entity("underground-belt"), UndergroundBelt)
        self.assertIsInstance(new_entity("splitter"), Splitter)
        self.assertIsInstance(new_entity("burner-inserter"), Inserter)
        self.assertIsInstance(new_entity("filter-inserter"), FilterInserter)
        self.assertIsInstance(new_entity("loader"), Loader)
        self.assertIsInstance(new_entity("small-electric-pole"), ElectricPole)
        self.assertIsInstance(new_entity("pipe"), Pipe)
        self.assertIsInstance(new_entity("pipe-to-ground"), UndergroundPipe)
        self.assertIsInstance(new_entity("pump"), Pump)
        self.assertIsInstance(new_entity("straight-rail"), StraightRail)
        self.assertIsInstance(new_entity("curved-rail"), CurvedRail)
        self.assertIsInstance(new_entity("train-stop"), TrainStop)
        self.assertIsInstance(new_entity("rail-signal"), RailSignal)
        self.assertIsInstance(new_entity("rail-chain-signal"), RailChainSignal)
        self.assertIsInstance(new_entity("locomotive"), Locomotive)
        self.assertIsInstance(new_entity("cargo-wagon"), CargoWagon)
        self.assertIsInstance(new_entity("fluid-wagon"), FluidWagon)
        self.assertIsInstance(new_entity("artillery-wagon"), ArtilleryWagon)
        self.assertIsInstance(
            new_entity("logistic-chest-passive-provider"), LogisticPassiveContainer
        )
        self.assertIsInstance(
            new_entity("logistic-chest-active-provider"), LogisticActiveContainer
        )
        self.assertIsInstance(
            new_entity("logistic-chest-storage"), LogisticStorageContainer
        )
        self.assertIsInstance(
            new_entity("logistic-chest-buffer"), LogisticBufferContainer
        )
        self.assertIsInstance(
            new_entity("logistic-chest-requester"), LogisticRequestContainer
        )
        self.assertIsInstance(new_entity("roboport"), Roboport)
        self.assertIsInstance(new_entity("small-lamp"), Lamp)
        self.assertIsInstance(new_entity("arithmetic-combinator"), ArithmeticCombinator)
        self.assertIsInstance(new_entity("decider-combinator"), DeciderCombinator)
        self.assertIsInstance(new_entity("constant-combinator"), ConstantCombinator)
        self.assertIsInstance(new_entity("power-switch"), PowerSwitch)
        self.assertIsInstance(new_entity("programmable-speaker"), ProgrammableSpeaker)
        self.assertIsInstance(new_entity("boiler"), Boiler)
        self.assertIsInstance(new_entity("steam-engine"), Generator)
        self.assertIsInstance(new_entity("solar-panel"), SolarPanel)
        self.assertIsInstance(new_entity("accumulator"), Accumulator)
        self.assertIsInstance(new_entity("nuclear-reactor"), Reactor)
        self.assertIsInstance(new_entity("heat-pipe"), HeatPipe)
        self.assertIsInstance(new_entity("burner-mining-drill"), MiningDrill)
        self.assertIsInstance(new_entity("offshore-pump"), OffshorePump)
        self.assertIsInstance(new_entity("stone-furnace"), Furnace)
        self.assertIsInstance(new_entity("assembling-machine-1"), AssemblingMachine)
        self.assertIsInstance(new_entity("lab"), Lab)
        self.assertIsInstance(new_entity("beacon"), Beacon)
        self.assertIsInstance(new_entity("rocket-silo"), RocketSilo)
        self.assertIsInstance(new_entity("land-mine"), LandMine)
        self.assertIsInstance(new_entity("stone-wall"), Wall)
        self.assertIsInstance(new_entity("gate"), Gate)
        self.assertIsInstance(new_entity("gun-turret"), Turret)
        self.assertIsInstance(new_entity("radar"), Radar)
        self.assertIsInstance(
            new_entity("electric-energy-interface"), ElectricEnergyInterface
        )
        self.assertIsInstance(new_entity("linked-chest"), LinkedContainer)
        self.assertIsInstance(new_entity("heat-interface"), HeatInterface)
        self.assertIsInstance(new_entity("linked-belt"), LinkedBelt)
        self.assertIsInstance(new_entity("infinity-chest"), InfinityContainer)
        self.assertIsInstance(new_entity("infinity-pipe"), InfinityPipe)
        self.assertIsInstance(new_entity("burner-generator"), BurnerGenerator)

        self.assertRaises(
            InvalidEntityError,
            new_entity,
            "I have a lot of entities that I need to test...",
        )
