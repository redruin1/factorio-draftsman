# entity.py
# -*- encoding: utf-8 -*-

from draftsman.blueprintable import *
from draftsman.classes.vector import Vector
from draftsman.constants import *
from draftsman.entity import *
from draftsman.error import *
from draftsman.warning import *
from draftsman.utils import AABB

import sys
import pytest

if sys.version_info >= (3, 3):  # pragma: no coverage
    import unittest
else:  # pragma: no coverage
    import unittest2 as unittest


class EntityTesting(unittest.TestCase):
    def test_get_type(self):
        container = Container("wooden-chest")
        assert container.type == "container"

    def test_set_tags(self):
        container = Container("wooden-chest")
        container.tags = {"wee": 500, "hello": "world"}
        container.tags["addition"] = 1 + 1

        assert container.to_dict() == {
            "name": "wooden-chest",
            "position": {"x": 0.5, "y": 0.5},
            "tags": {"wee": 500, "hello": "world", "addition": 2},
        }

        # Resetting tags to empty should omit it based on its lambda func
        container.tags = {}
        assert container.to_dict() == {
            "name": "wooden-chest",
            "position": {"x": 0.5, "y": 0.5},
        }

        container.tags = None
        assert container.to_dict() == {
            "name": "wooden-chest",
            "position": {"x": 0.5, "y": 0.5},
        }

        # Errors
        # Setting tags to anything other than a dict raises errors
        with pytest.raises(TypeError):
            container.tags = "incorrect"

    def test_get_world_bounding_box(self):
        combinator = DeciderCombinator(tile_position=[3, 3], direction=Direction.EAST)
        assert combinator.get_world_bounding_box() == AABB(3.35, 3.15, 4.65, 3.85)

    # def test_set_name(self):
    #     iron_chest = Container("iron-chest")
    #     iron_chest.name = "steel-chest"
    #     self.assertEqual(iron_chest.name, "steel-chest")

    #     with self.assertRaises(InvalidEntityError):
    #         iron_chest.name = "incorrect"

    def test_set_position(self):
        iron_chest = Container("iron-chest")
        iron_chest.position = (1.23, 1.34)
        assert round(abs(iron_chest.position - Vector(1.23, 1.34)), 7) == Vector(0, 0)
        assert round(abs(iron_chest.position.to_dict()["x"] - 1.23), 7) == 0
        assert round(abs(iron_chest.position.to_dict()["y"] - 1.34), 7) == 0
        assert iron_chest.tile_position == Vector(1, 1)
        assert iron_chest.tile_position.to_dict() == {"x": 1, "y": 1}

        with pytest.raises(ValueError):
            iron_chest.position = ("fish", 10)

        iron_chest.tile_position = (10, 10.1)  # should cast float to int
        assert iron_chest.tile_position == Vector(10, 10)
        assert iron_chest.tile_position.to_dict() == {"x": 10, "y": 10}
        assert round(abs(iron_chest.position.x - 10.5), 7) == 0
        assert round(abs(iron_chest.position.y - 10.5), 7) == 0
        assert round(abs(iron_chest.position.to_dict()["x"] - 10.5), 7) == 0
        assert round(abs(iron_chest.position.to_dict()["y"] - 10.5), 7) == 0

        with pytest.raises(ValueError):
            iron_chest.tile_position = (1.0, "raw-fish")

    def test_modify_position_attribute(self):
        iron_chest = Container("iron-chest")

        iron_chest.position.x += 1
        assert iron_chest.position == Vector(1.5, 0.5)
        assert iron_chest.tile_position == Vector(1, 0)
        
        iron_chest.position.y += 1
        assert iron_chest.position == Vector(1.5, 1.5)

    def test_change_name_in_blueprint(self):
        blueprint = Blueprint()
        example = Container("wooden-chest", id="whatever")
        blueprint.entities.append(example)
        assert blueprint.entities["whatever"].name == example.name

        with pytest.raises(DraftsmanError):
            blueprint.entities["whatever"].name = "steel-chest"

    def test_deepcopy(self):
        example = Container("wooden-chest", id="test")
        blueprint = Blueprint()
        blueprint.entities.append(example, copy=False)

        import copy

        copy_example = copy.deepcopy(example)
        assert example is not copy_example
        assert example.name == copy_example.name
        assert example.id == copy_example.id
        assert example.position == copy_example.position
        assert example.parent is blueprint
        assert copy_example.parent is None  # Make sure parent in copy is None

    def test_change_id_in_blueprint(self):
        blueprint = Blueprint()
        example = Container("wooden-chest", id="whatever")
        blueprint.entities.append(example)
        assert blueprint.entities["whatever"].name == example.name

        blueprint.entities["whatever"].id = "something else"
        assert blueprint.entities[0] is blueprint.entities["something else"]
        assert blueprint.entities[0].id == "something else"
        with pytest.raises(KeyError):
            blueprint.entities["whatever"]

        blueprint.entities["something else"].id = None
        assert blueprint.entities[0].id == None
        with pytest.raises(KeyError):
            blueprint.entities["something else"]
        with pytest.raises(KeyError):
            blueprint.entities["whatever"]

        # Add a new entity and check for duplicate ID error
        blueprint.entities.append("wooden-chest", tile_position=(1, 0))
        blueprint.entities[0].id = "duplicate"
        with pytest.raises(DuplicateIDError):
            blueprint.entities[1].id = "duplicate"

    def test_flippable(self):
        belt = TransportBelt()
        assert belt.flippable == True


# =============================================================================
# Factory function new_entity()
# =============================================================================

# fmt: off
class EntityFactoryTesting(unittest.TestCase):
    def test_container(self):
        assert isinstance(new_entity("wooden-chest"), Container)

    def test_storage_tank(self):
        assert isinstance(new_entity("storage-tank"), StorageTank)

    def test_transport_belt(self):
        assert isinstance(new_entity("transport-belt"), TransportBelt)

    def test_underground_belt(self):
        assert isinstance(new_entity("underground-belt"), UndergroundBelt)

    def test_splitter(self):
        assert isinstance(new_entity("splitter"), Splitter)

    def test_inserter(self):
        assert isinstance(new_entity("burner-inserter"), Inserter)

    def test_filter_inserter(self):
        assert isinstance(new_entity("filter-inserter"), FilterInserter)

    def test_loader(self):
        assert isinstance(new_entity("loader"), Loader)

    def test_electric_pole(self):
        assert isinstance(new_entity("small-electric-pole"), ElectricPole)

    def test_pipe(self):
        assert isinstance(new_entity("pipe"), Pipe)

    def test_underground_pipe(self):
        assert isinstance(new_entity("pipe-to-ground"), UndergroundPipe)

    def test_pump(self):
        assert isinstance(new_entity("pump"), Pump)

    def test_straight_rail(self):
        assert isinstance(new_entity("straight-rail"), StraightRail)

    def test_curved_rail(self):
        assert isinstance(new_entity("curved-rail"), CurvedRail)

    def test_train_stop(self):
        assert isinstance(new_entity("train-stop"), TrainStop)

    def test_rail_signal(self):
        assert isinstance(new_entity("rail-signal"), RailSignal)

    def test_rail_chain_signal(self):
        assert isinstance(new_entity("rail-chain-signal"), RailChainSignal)

    def test_locomotive(self):
        assert isinstance(new_entity("locomotive"), Locomotive)

    def test_cargo_wagon(self):
        assert isinstance(new_entity("cargo-wagon"), CargoWagon)

    def test_fluid_wagon(self):
        assert isinstance(new_entity("fluid-wagon"), FluidWagon)

    def test_artillery_wagon(self):
        assert isinstance(new_entity("artillery-wagon"), ArtilleryWagon)

    def test_logistic_passive_container(self):
        assert isinstance(new_entity("logistic-chest-passive-provider"), LogisticPassiveContainer)

    def test_logistic_active_container(self):
        assert isinstance(new_entity("logistic-chest-active-provider"), LogisticActiveContainer)

    def test_logistic_storage_container(self):
        assert isinstance(new_entity("logistic-chest-storage"), LogisticStorageContainer)

    def test_logistic_buffer_container(self):
        assert isinstance(new_entity("logistic-chest-buffer"), LogisticBufferContainer)

    def test_logistic_request_container(self):
        assert isinstance(new_entity("logistic-chest-requester"), LogisticRequestContainer)

    def test_roboport(self):
        assert isinstance(new_entity("roboport"), Roboport)

    def test_lamp(self):
        assert isinstance(new_entity("small-lamp"), Lamp)

    def test_arithmetic_combinator(self):
        assert isinstance(new_entity("arithmetic-combinator"), ArithmeticCombinator)

    def test_decider_combinator(self):
        assert isinstance(new_entity("decider-combinator"), DeciderCombinator)

    def test_constant_combinator(self):
        assert isinstance(new_entity("constant-combinator"), ConstantCombinator)

    def test_power_switch(self):
        assert isinstance(new_entity("power-switch"), PowerSwitch)

    def test_programmable_speaker(self):
        assert isinstance(new_entity("programmable-speaker"), ProgrammableSpeaker)

    def test_boiler(self):
        assert isinstance(new_entity("boiler"), Boiler)

    def test_generator(self):
        assert isinstance(new_entity("steam-engine"), Generator)

    def test_solar_panel(self):
        assert isinstance(new_entity("solar-panel"), SolarPanel)

    def test_accumulator(self):
        assert isinstance(new_entity("accumulator"), Accumulator)

    def test_reactor(self):
        assert isinstance(new_entity("nuclear-reactor"), Reactor)

    def test_heat_pipe(self):
        assert isinstance(new_entity("heat-pipe"), HeatPipe)

    def test_mining_drill(self):
        assert isinstance(new_entity("burner-mining-drill"), MiningDrill)

    def test_offshore_pump(self):
        assert isinstance(new_entity("offshore-pump"), OffshorePump)

    def test_furnace(self):
        assert isinstance(new_entity("stone-furnace"), Furnace)

    def test_assembling_machine(self):
        assert isinstance(new_entity("assembling-machine-1"), AssemblingMachine)

    def test_lab(self):
        assert isinstance(new_entity("lab"), Lab)

    def test_beacon(self):
        assert isinstance(new_entity("beacon"), Beacon)

    def test_rocket_silo(self):
        assert isinstance(new_entity("rocket-silo"), RocketSilo)

    def test_land_mine(self):
        assert isinstance(new_entity("land-mine"), LandMine)

    def test_wall(self):
        assert isinstance(new_entity("stone-wall"), Wall)

    def test_gate(self):
        assert isinstance(new_entity("gate"), Gate)

    def test_turret(self):
        assert isinstance(new_entity("gun-turret"), Turret)

    def test_radar(self):
        assert isinstance(new_entity("radar"), Radar)

    def test_electric_energy_interface(self):
        assert isinstance(new_entity("electric-energy-interface"), ElectricEnergyInterface)

    @unittest.skipIf(len(linked_containers) == 0, "No linked containers to test")
    def test_linked_container(self):
        assert isinstance(new_entity("linked-chest"), LinkedContainer)

    def test_heat_interface(self):
        assert isinstance(new_entity("heat-interface"), HeatInterface)

    @unittest.skipIf(len(linked_belts) == 0, "No linked belts to test")
    def test_linked_belt(self):
        assert isinstance(new_entity("linked-belt"), LinkedBelt)

    def test_infinity_container(self):
        assert isinstance(new_entity("infinity-chest"), InfinityContainer)

    def test_infinity_pipe(self):
        assert isinstance(new_entity("infinity-pipe"), InfinityPipe)

    def test_burner_generator(self):
        assert isinstance(new_entity("burner-generator"), BurnerGenerator)

    def test_errors(self):
        with pytest.raises(InvalidEntityError):
            new_entity("I have a lot of entities that I need to test...",)

# fmt: on
