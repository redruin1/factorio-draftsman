# entity.py

from draftsman.entity import *

#from draftsman.errors import InvalidWireType
from schema import SchemaError

from unittest import TestCase

class EntityTesting(TestCase):
    def test_set_tags(self):
        container = Container("wooden-chest")
        container.set_tags({"wee": 500, "hello": "world"})
        container.set_tag("addition", 1 + 1)

        self.assertEqual(
            container.to_dict(),
            {
                "name": "wooden-chest",
                "position": {"x": 0.5, "y": 0.5},
                "tags": {
                    "wee": 500,
                    "hello": "world",
                    "addition": 2
                }
            }
        )

        # Removing by setting to None
        container.set_tag("addition", None)
        self.assertEqual(
            container.to_dict(),
            {
                "name": "wooden-chest",
                "position": {"x": 0.5, "y": 0.5},
                "tags": {
                    "wee": 500,
                    "hello": "world",
                }
            }
        )

        # Remove non-existant key should do nothing
        container.set_tag("unknown", None)
        self.assertEqual(
            container.to_dict(),
            {
                "name": "wooden-chest",
                "position": {"x": 0.5, "y": 0.5},
                "tags": {
                    "wee": 500,
                    "hello": "world",
                }
            }
        )

        # Resetting tags to empty should omit it based on its lambda func
        container.set_tags({})
        self.assertEqual(
            container.to_dict(),
            {
                "name": "wooden-chest",
                "position": {"x": 0.5, "y": 0.5},
            }
        )

    def test_to_dict(self):
        class TestEntity(Entity):
            pass

        # TODO
        pass

    def test_iter(self):
        container = Container("wooden-chest")
        values = dict()
        for key, value in container:
            values[key] = value

        values["exports"] = None # Make our lives easier

        self.assertEqual(
            values,
            {
                "exports": None,
                "name": "wooden-chest",
                "id": None,
                "width": 1,
                "height": 1,
                "power_connectable": False,
                "dual_power_connectable": False,
                "circuit_connectable": True,
                "dual_circuit_connectable": False,
                "position": {"x": 0.5, "y": 0.5},
                "grid_position": [0, 0],
                "tags": {},
                "inventory_size": 16,
                "bar": None,
                "connections": {}
            }
        )

    def test_repr(self):
        class TestEntity(Entity):
            pass

        test = TestEntity("loader")
        self.assertEqual(
            str(test),
            "<Entity>{'name': 'loader', 'position': {'x': 0.5, 'y': 1.0}}"
        )


class DirectionalMixinTesting(TestCase):
    pass


class TransportBeltTesting(TestCase):
    pass

class UndergroundBeltTesting(TestCase):
    pass

class SplitterTesting(TestCase):
    pass

class InserterTesting(TestCase):
    pass

class FilterInserterTesting(TestCase):
    pass

class LoaderTesting(TestCase):
    pass

class ElectricPoleTesting(TestCase):
    pass

class PipeTesting(TestCase):
    pass

class UndergroundPipeTesting(TestCase):
    pass

class PumpTesting(TestCase):
    pass

class StraightRailTesting(TestCase): # Hoo boy
    pass

class CurvedRailTesting(TestCase): # HOO BOY
    pass

class TrainStopTesting(TestCase):
    pass

class RailSignalTesting(TestCase):
    pass

class RailChainSignalTesting(TestCase):
    pass

class LocomotiveTesting(TestCase):
    pass

class CargoWagonTesting(TestCase):
    pass

class FluidWagonTesting(TestCase):
    pass

class ArtilleryWagonTesting(TestCase):
    pass

class LogisticStorageContainerTesting(TestCase):
    pass

class LogisticBufferContainerTesting(TestCase):
    pass

class LogisticRequestContainerTesting(TestCase):
    pass

class RoboportTesting(TestCase):
    pass

class LampTesting(TestCase):
    pass

class ArithmeticCombinatorTesting(TestCase):
    pass

class DeciderCombinatorTesting(TestCase):
    pass

class ConstantCombinatorTesting(TestCase):
    pass

class PowerSwitchTesting(TestCase):
    pass

class ProgrammableSpeakerTesting(TestCase):
    pass

class BoilerTesting(TestCase):
    pass

class GeneratorTesting(TestCase):
    pass

class SolarPanelTesting(TestCase):
    pass

class AccumulatorTesting(TestCase):
    pass

class ReactorTesting(TestCase):
    pass

class HeatPipeTesting(TestCase):
    pass

class MiningDrillTesting(TestCase):
    pass

class OffshorePumpTesting(TestCase):
    pass

class FurnaceTesting(TestCase):
    pass

class AssemblingMachineTesting(TestCase):
    pass

class LabTesting(TestCase):
    pass

class BeaconTesting(TestCase):
    pass

class RocketSiloTesting(TestCase):
    pass

class LandMineTesting(TestCase):
    pass

class WallTesting(TestCase):
    pass

class GateTesting(TestCase):
    pass

class TurretTesting(TestCase):
    pass

class RadarTesting(TestCase):
    pass

class ElectricEnergyInterfaceTesting(TestCase):
    pass

class LinkedContainerTesting(TestCase):
    pass

class HeatInterfaceTesting(TestCase):
    pass

class LinkedBeltTesting(TestCase):
    pass

class InfinityContainerTesting(TestCase):
    pass

class InfinityPipeTesting(TestCase):
    pass

class BurnerGeneratorTesting(TestCase):
    pass

class EntityUtilsTesting(TestCase):
    def test_new_entity(self):
        self.assertIsInstance(
            new_entity("wooden-chest"),
            Container
        )
        self.assertIsInstance(
            new_entity("storage-tank"),
            StorageTank
        )
        self.assertIsInstance(
            new_entity("transport-belt"),
            TransportBelt
        )
        self.assertIsInstance(
            new_entity("underground-belt"),
            UndergroundBelt
        )
        self.assertIsInstance(
            new_entity("splitter"),
            Splitter
        )
        self.assertIsInstance(
            new_entity("burner-inserter"),
            Inserter
        )
        self.assertIsInstance(
            new_entity("filter-inserter"),
            FilterInserter
        )
        self.assertIsInstance(
            new_entity("loader"),
            Loader
        )
        self.assertIsInstance(
            new_entity("small-electric-pole"),
            ElectricPole
        )
        self.assertIsInstance(
            new_entity("pipe"),
            Pipe
        )
        self.assertIsInstance(
            new_entity("pipe-to-ground"),
            UndergroundPipe
        )
        self.assertIsInstance(
            new_entity("pump"),
            Pump
        )
        self.assertIsInstance(
            new_entity("straight-rail"),
            StraightRail
        )
        self.assertIsInstance(
            new_entity("curved-rail"),
            CurvedRail
        )
        self.assertIsInstance(
            new_entity("train-stop"),
            TrainStop
        )
        self.assertIsInstance(
            new_entity("rail-signal"),
            RailSignal
        )
        self.assertIsInstance(
            new_entity("rail-chain-signal"),
            RailChainSignal
        )
        self.assertIsInstance(
            new_entity("locomotive"),
            Locomotive
        )
        self.assertIsInstance(
            new_entity("cargo-wagon"),
            CargoWagon
        )
        self.assertIsInstance(
            new_entity("fluid-wagon"),
            FluidWagon
        )
        self.assertIsInstance(
            new_entity("artillery-wagon"),
            ArtilleryWagon
        )
        self.assertIsInstance(
            new_entity("logistic-chest-storage"),
            LogisticStorageContainer
        )
        self.assertIsInstance(
            new_entity("logistic-chest-buffer"),
            LogisticBufferContainer
        )
        self.assertIsInstance(
            new_entity("logistic-chest-requester"),
            LogisticRequestContainer
        )
        self.assertIsInstance(
            new_entity("roboport"),
            Roboport
        )
        self.assertIsInstance(
            new_entity("small-lamp"),
            Lamp
        )
        self.assertIsInstance(
            new_entity("arithmetic-combinator"),
            ArithmeticCombinator
        )
        self.assertIsInstance(
            new_entity("decider-combinator"),
            DeciderCombinator
        )
        self.assertIsInstance(
            new_entity("constant-combinator"),
            ConstantCombinator
        )
        self.assertIsInstance(
            new_entity("power-switch"),
            PowerSwitch
        )
        self.assertIsInstance(
            new_entity("programmable-speaker"),
            ProgrammableSpeaker
        )
        self.assertIsInstance(
            new_entity("boiler"),
            Boiler
        )
        self.assertIsInstance(
            new_entity("steam-engine"),
            Generator
        )
        self.assertIsInstance(
            new_entity("solar-panel"),
            SolarPanel
        )
        self.assertIsInstance(
            new_entity("accumulator"),
            Accumulator
        )
        self.assertIsInstance(
            new_entity("nuclear-reactor"),
            Reactor
        )
        self.assertIsInstance(
            new_entity("heat-pipe"),
            HeatPipe
        )
        self.assertIsInstance(
            new_entity("burner-mining-drill"),
            MiningDrill
        )
        self.assertIsInstance(
            new_entity("offshore-pump"),
            OffshorePump
        )
        self.assertIsInstance(
            new_entity("stone-furnace"),
            Furnace
        )
        self.assertIsInstance(
            new_entity("assembling-machine-1"),
            AssemblingMachine
        )
        self.assertIsInstance(
            new_entity("lab"),
            Lab
        )
        self.assertIsInstance(
            new_entity("beacon"),
            Beacon
        )
        self.assertIsInstance(
            new_entity("rocket-silo"),
            RocketSilo
        )
        self.assertIsInstance(
            new_entity("land-mine"),
            LandMine
        )
        self.assertIsInstance(
            new_entity("stone-wall"),
            Wall
        )
        self.assertIsInstance(
            new_entity("gate"),
            Gate
        )
        self.assertIsInstance(
            new_entity("gun-turret"),
            Turret
        )
        self.assertIsInstance(
            new_entity("radar"),
            Radar
        )
        self.assertIsInstance(
            new_entity("electric-energy-interface"),
            ElectricEnergyInterface
        )
        self.assertIsInstance(
            new_entity("linked-chest"),
            LinkedContainer
        )
        self.assertIsInstance(
            new_entity("heat-interface"),
            HeatInterface
        )
        self.assertIsInstance(
            new_entity("linked-belt"),
            LinkedBelt
        )
        self.assertIsInstance(
            new_entity("infinity-chest"),
            InfinityContainer
        )
        self.assertIsInstance(
            new_entity("infinity-pipe"),
            InfinityPipe
        )
        self.assertIsInstance(
            new_entity("burner-generator"),
            BurnerGenerator
        )

        self.assertRaises(
            InvalidEntityID,
            new_entity,
            "I have a lot of entities that I need to test..."
        )