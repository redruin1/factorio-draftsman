# entity.py

from draftsman import DEFAULT_FACTORIO_VERSION
from draftsman.blueprintable import *
from draftsman.classes.vector import Vector
from draftsman.constants import *
import draftsman.data.entities as data
from draftsman.data import mods
from draftsman.entity import *
from draftsman.error import *
from draftsman.warning import *
from draftsman.utils import AABB, version_tuple_to_string
import draftsman.validators
from draftsman.serialization import draftsman_converters

import pytest
from referencing import Registry, Resource
from jsonschema import Draft202012Validator

import itertools
import json
import os

from test.prototypes.test_accumulator import valid_accumulator
from test.prototypes.test_agricultural_tower import valid_agricultural_tower
from test.prototypes.test_ammo_turret import valid_ammo_turret
from test.prototypes.test_arithmetic_combinator import valid_arithmetic_combinator
from test.prototypes.test_artillery_turret import valid_artillery_turret
from test.prototypes.test_artillery_wagon import valid_artillery_wagon
from test.prototypes.test_assembling_machine import valid_assembling_machine
from test.prototypes.test_asteroid_collector import valid_asteroid_collector
from test.prototypes.test_beacon import valid_beacon
from test.prototypes.test_boiler import valid_boiler
from test.prototypes.test_burner_generator import valid_burner_generator
from test.prototypes.test_car import valid_car
from test.prototypes.test_cargo_bay import valid_cargo_bay
from test.prototypes.test_cargo_landing_pad import valid_cargo_landing_pad
from test.prototypes.test_cargo_wagon import valid_cargo_wagon
from test.prototypes.test_constant_combinator import valid_constant_combinator
from test.prototypes.test_container import valid_container
from test.prototypes.test_curved_rail_a import valid_curved_rail_a
from test.prototypes.test_curved_rail_b import valid_curved_rail_b
from test.prototypes.test_decider_combinator import valid_decider_combinator
from test.prototypes.test_display_panel import valid_display_panel
from test.prototypes.test_electric_energy_interface import (
    valid_electric_energy_interface,
)
from test.prototypes.test_electric_pole import valid_electric_pole
from test.prototypes.test_electric_turret import valid_electric_turret
from test.prototypes.test_elevated_curved_rail_a import valid_elevated_curved_rail_a
from test.prototypes.test_elevated_curved_rail_b import valid_elevated_curved_rail_b
from test.prototypes.test_elevated_half_diagonal_rail import (
    valid_elevated_half_diagonal_rail,
)
from test.prototypes.test_elevated_straight_rail import valid_elevated_straight_rail
from test.prototypes.test_fluid_turret import valid_fluid_turret
from test.prototypes.test_fluid_wagon import valid_fluid_wagon
from test.prototypes.test_furnace import valid_furnace
from test.prototypes.test_fusion_generator import valid_fusion_generator
from test.prototypes.test_fusion_reactor import valid_fusion_reactor
from test.prototypes.test_gate import valid_gate
from test.prototypes.test_generator import valid_generator
from test.prototypes.test_half_diagonal_rail import valid_half_diagonal_rail

# schema tests stop here
from test.prototypes.test_heat_interface import valid_heat_interface
from test.prototypes.test_heat_pipe import valid_heat_pipe
from test.prototypes.test_infinity_container import valid_infinity_container
from test.prototypes.test_infinity_pipe import valid_infinity_pipe
from test.prototypes.test_inserter import valid_inserter
from test.prototypes.test_lab import valid_lab
from test.prototypes.test_lamp import valid_lamp
from test.prototypes.test_land_mine import valid_land_mine
from test.prototypes.test_legacy_curved_rail import valid_legacy_curved_rail
from test.prototypes.test_legacy_straight_rail import valid_legacy_straight_rail
from test.prototypes.test_lightning_attractor import valid_lightning_attractor
from test.prototypes.test_linked_belt import valid_linked_belt
from test.prototypes.test_linked_container import valid_linked_container
from test.prototypes.test_loader import valid_loader
from test.prototypes.test_locomotive import valid_locomotive
from test.prototypes.test_logistic_active_container import valid_active_container
from test.prototypes.test_logistic_buffer_container import valid_buffer_container
from test.prototypes.test_logistic_passive_container import valid_passive_container
from test.prototypes.test_logistic_request_container import valid_request_container
from test.prototypes.test_logistic_storage_container import valid_storage_container
from test.prototypes.test_mining_drill import valid_mining_drill
from test.prototypes.test_offshore_pump import valid_offshore_pump
from test.prototypes.test_pipe import valid_pipe
from test.prototypes.test_player_port import valid_player_port
from test.prototypes.test_power_switch import valid_power_switch
from test.prototypes.test_programmable_speaker import valid_programmable_speaker
from test.prototypes.test_pump import valid_pump
from test.prototypes.test_radar import valid_radar
from test.prototypes.test_rail_chain_signal import valid_rail_chain_signal
from test.prototypes.test_rail_ramp import valid_rail_ramp
from test.prototypes.test_rail_signal import valid_rail_signal
from test.prototypes.test_rail_support import valid_rail_support
from test.prototypes.test_reactor import valid_reactor
from test.prototypes.test_roboport import valid_roboport
from test.prototypes.test_rocket_silo import valid_rocket_silo
from test.prototypes.test_selector_combinator import valid_selector_combinator
from test.prototypes.test_simple_entity_with_force import valid_simple_entity_with_force
from test.prototypes.test_simple_entity_with_owner import valid_simple_entity_with_owner
from test.prototypes.test_solar_panel import valid_solar_panel
from test.prototypes.test_space_platform_hub import valid_space_platform_hub
from test.prototypes.test_spider_vehicle import valid_spider_vehicle
from test.prototypes.test_splitter import valid_splitter
from test.prototypes.test_storage_tank import valid_storage_tank
from test.prototypes.test_straight_rail import valid_straight_rail
from test.prototypes.test_thruster import valid_thruster
from test.prototypes.test_train_stop import valid_train_stop
from test.prototypes.test_transport_belt import valid_transport_belt
from test.prototypes.test_underground_belt import valid_underground_belt
from test.prototypes.test_underground_pipe import valid_underground_pipe
from test.prototypes.test_wall import valid_wall

entity_fixtures = [
    "valid_accumulator",
    "valid_agricultural_tower",
    "valid_ammo_turret",
    "valid_arithmetic_combinator",
    "valid_artillery_turret",
    "valid_artillery_wagon",
    "valid_assembling_machine",
    "valid_asteroid_collector",
    "valid_beacon",
    "valid_boiler",
    "valid_burner_generator",
    "valid_car",
    "valid_cargo_bay",
    "valid_cargo_landing_pad",
    "valid_cargo_wagon",
    "valid_constant_combinator",
    "valid_container",
    "valid_curved_rail_a",
    "valid_curved_rail_b",
    "valid_decider_combinator",
    "valid_display_panel",
    "valid_electric_energy_interface",
    "valid_electric_pole",
    "valid_electric_turret",
    "valid_elevated_curved_rail_a",
    "valid_elevated_curved_rail_b",
    "valid_elevated_half_diagonal_rail",
    "valid_elevated_straight_rail",
    "valid_fluid_turret",
    "valid_fluid_wagon",
    "valid_furnace",
    "valid_fusion_generator",
    "valid_fusion_reactor",
    "valid_gate",
    "valid_generator",
    "valid_half_diagonal_rail",
    "valid_heat_interface",
    "valid_heat_pipe",
    "valid_infinity_container",
    "valid_infinity_pipe",
    "valid_inserter",
    "valid_lab",
    "valid_lamp",
    "valid_land_mine",
    "valid_legacy_curved_rail",
    "valid_legacy_straight_rail",
    "valid_lightning_attractor",
    "valid_linked_belt",
    "valid_linked_container",
    "valid_loader",
    "valid_locomotive",
    "valid_active_container",
    "valid_buffer_container",
    "valid_passive_container",
    "valid_request_container",
    "valid_storage_container",
    "valid_mining_drill",
    "valid_offshore_pump",
    "valid_pipe",
    "valid_player_port",
    "valid_power_switch",
    "valid_programmable_speaker",
    "valid_pump",
    "valid_radar",
    "valid_rail_chain_signal",
    "valid_rail_ramp",
    "valid_rail_signal",
    "valid_rail_support",
    "valid_reactor",
    "valid_roboport",
    "valid_rocket_silo",
    "valid_selector_combinator",
    "valid_simple_entity_with_force",
    "valid_simple_entity_with_owner",
    "valid_solar_panel",
    "valid_space_platform_hub",
    "valid_spider_vehicle",
    "valid_splitter",
    "valid_storage_tank",
    "valid_straight_rail",
    "valid_thruster",
    "valid_train_stop",
    "valid_transport_belt",
    "valid_underground_belt",
    "valid_underground_pipe",
    "valid_wall",
]


def grab_json_file(*path) -> dict:
    with open(os.path.join(*path), "r") as json_file:
        return json.load(json_file)


def retrieve_from_path(uri: str) -> Resource:
    print(uri)
    return Resource.from_contents(
        grab_json_file("factorio-blueprint-schemas", "schemas", uri)
    )


registry = Registry(retrieve=retrieve_from_path)

versions_to_test = ((1, 0, 0), (2, 0, 0))


@pytest.mark.parametrize("entity", entity_fixtures)
class TestAllEntities:
    @pytest.mark.parametrize(
        "version",
        versions_to_test,
        ids=[version_tuple_to_string(t) for t in versions_to_test],
    )
    def test_output_matches_JSON_schema(
        self,
        entity: Entity,
        version: tuple[int, ...],
        request: pytest.FixtureRequest,
    ):
        """
        The result from `to_dict()` should pass validation from the entity's JSON
        schema. If not, there's either an error with `to_dict()`, the JSON schema,
        or both.
        """
        # Grab the fixture of the entity
        entity_name = entity
        entity = request.getfixturevalue(entity_name)
        if entity is None:
            pytest.skip(
                reason="No '{}' to test under current environment".format(entity_name)
            )

        try:
            entity_schema = grab_json_file(
                "factorio-blueprint-schemas",
                "schemas",
                version_tuple_to_string(version),
                "entity",
                entity.type + ".json",
            )
        except FileNotFoundError:
            pytest.skip(
                reason="No schema for '{}' on version {}".format(entity_name, version)
            )

        Draft202012Validator.check_schema(entity_schema)
        validator = Draft202012Validator(schema=entity_schema, registry=registry)
        # Test every `exclude_...` configuration
        for exclude_none, exclude_defaults in itertools.product(
            (True, False), (True, False)
        ):
            # Entity populated with defaults
            validator.validate(
                type(entity)().to_dict(
                    exclude_none=exclude_none,
                    exclude_defaults=exclude_defaults,
                    version=version,
                    entity_number=1,
                )
            )
            # Entity populated with non-defaults
            validator.validate(
                entity.to_dict(
                    exclude_none=exclude_none,
                    exclude_defaults=exclude_defaults,
                    version=version,
                    entity_number=1,
                )
            )


class TestEntityBase:
    def test_similar_entities(self):
        with draftsman.validators.set_mode(ValidationMode.DISABLED):
            assert Entity("entity").similar_entities == []

    def test_get_type(self):
        with draftsman.validators.set_mode(ValidationMode.DISABLED):
            assert Entity("entity", validate_assignment="none").type is None

        container = Container("wooden-chest")
        assert container.type == "container"

    def test_entity_number_not_retained(self):
        container = Container.from_dict(
            {
                "name": "wooden-chest",
                "position": {"x": 0.5, "y": 0.5},
                "entity_number": 10,
            }
        )
        # assert container.entity_number == 10
        # Stripped on output
        assert container.to_dict() == {
            "name": "wooden-chest",
            "position": {"x": 0.5, "y": 0.5},
        }

    def test_flags(self):
        container = Container("wooden-chest")
        assert container.flags == ["placeable-neutral", "player-creation"]

    def test_set_tags(self):
        container = Container("wooden-chest")
        container.tags = {"wee": 500, "hello": "world"}
        container.tags["addition"] = 1 + 1

        assert container.to_dict() == {
            "name": "wooden-chest",
            "position": {"x": 0.5, "y": 0.5},
            "tags": {"wee": 500, "hello": "world", "addition": 2},
        }

        # Resetting tags to empty dict should be omitted
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
        with pytest.raises(DataFormatError):
            container.tags = "incorrect"

    def test_get_world_bounding_box(self):
        combinator = DeciderCombinator(tile_position=[3, 3], direction=Direction.EAST)
        assert combinator.get_world_bounding_box() == AABB(3.35, 3.15, 4.65, 3.85)
        recycler = new_entity(
            "assembling-machine-1", tile_position=[3, 3], direction=Direction.EAST
        )
        assert recycler.get_world_bounding_box() == AABB(3.3, 3.3, 5.7, 5.7)

    def test_set_name(self):
        iron_chest = Container("iron-chest")
        iron_chest.name = "steel-chest"
        assert iron_chest.name == "steel-chest"

        with pytest.warns(
            UnknownEntityWarning,
            match="'electric-furnace' is not a known name for a Container",
        ):
            iron_chest.name = "electric-furnace"

        with pytest.warns(UnknownEntityWarning, match="Unknown entity 'unknown'"):
            iron_chest.name = "unknown"

        assert iron_chest.collision_set == None
        assert iron_chest.collision_mask == None
        assert (iron_chest.tile_width, iron_chest.tile_height) == (0, 0)
        assert iron_chest.inventory_bar_enabled == True  # enabled by default
        assert iron_chest.get_world_bounding_box() == None

        with pytest.raises(DataFormatError):
            iron_chest.name = {"wrong"}

    def test_suggest_similar_name(self):
        with pytest.warns(
            UnknownEntityWarning,
            match="Unknown entity 'wodenchest'; did you mean 'wooden-chest'?",
        ):
            Container("wodenchest")

    def test_create_with_position(self):
        iron_chest = new_entity("iron-chest", tile_position=(3, 3))
        assert iron_chest.position.x == 3.5 and iron_chest.position.y == 3.5

        inserter = new_entity("inserter", tile_position=(10, 10))
        assert inserter.position.x == 10.5 and inserter.position.y == 10.5

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

    def test_modify_position_attributes(self):
        iron_chest = Container("iron-chest")

        iron_chest.position.x += 1
        assert iron_chest.position == Vector(1.5, 0.5)
        assert iron_chest.tile_position == Vector(1, 0)

        iron_chest.position.y += 1
        assert iron_chest.position == Vector(1.5, 1.5)
        assert iron_chest.tile_position == Vector(1, 1)

    def test_modify_tile_position_attributes(self):
        iron_chest = Container("iron-chest")

        iron_chest.tile_position.x += 1
        assert iron_chest.position == Vector(1.5, 0.5)
        assert iron_chest.tile_position == Vector(1, 0)

        iron_chest.tile_position.y += 1
        assert iron_chest.position == Vector(1.5, 1.5)
        assert iron_chest.tile_position == Vector(1, 1)

    def test_change_name_in_blueprint(self):
        blueprint = Blueprint()
        example = Container("wooden-chest", id="whatever")
        blueprint.entities.append(example)
        assert blueprint.entities["whatever"].name == example.name

        # TODO: think about
        # with pytest.raises(DraftsmanError):
        #     blueprint.entities["whatever"].name = "steel-chest"

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

    def test_change_position_in_blueprint(self):
        blueprint = Blueprint()
        example = Container("wooden-chest")
        blueprint.entities.append(example, copy=False)
        # TODO: think about
        # with pytest.raises(DraftsmanError):
        #     example.position = (10.5, 10.5)

    def test_flippable(self):
        belt = TransportBelt()
        assert belt.flippable == True


# =============================================================================
# Factory function new_entity()
# =============================================================================

# fmt: off
class TestEntityFactory:
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

    # def test_filter_inserter(self):
    #     assert isinstance(new_entity("filter-inserter"), FilterInserter)

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

    def test_legacy_straight_rail(self):
        if mods.versions.get("base", DEFAULT_FACTORIO_VERSION) < (2, 0):
            entity_name = "straight-rail"
        else:
            entity_name = "legacy-straight-rail"
        assert isinstance(new_entity(entity_name), LegacyStraightRail)

    def test_legacy_curved_rail(self):
        if mods.versions.get("base", DEFAULT_FACTORIO_VERSION) < (2, 0):
            entity_name = "curved-rail"
        else:
            entity_name = "legacy-curved-rail"
        assert isinstance(new_entity(entity_name), LegacyCurvedRail)

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
        if mods.versions.get("base", DEFAULT_FACTORIO_VERSION) < (2, 0):
            entity_name = "logistic-chest-passive-provider"
        else:
            entity_name = "passive-provider-chest"
        assert isinstance(new_entity(entity_name), LogisticPassiveContainer)

    def test_logistic_active_container(self):
        if mods.versions.get("base", DEFAULT_FACTORIO_VERSION) < (2, 0):
            entity_name = "logistic-chest-active-provider"
        else:
            entity_name = "active-provider-chest"
        assert isinstance(new_entity(entity_name), LogisticActiveContainer)

    def test_logistic_storage_container(self):
        if mods.versions.get("base", DEFAULT_FACTORIO_VERSION) < (2, 0):
            entity_name = "logistic-chest-storage"
        else:
            entity_name = "storage-chest"
        assert isinstance(new_entity(entity_name), LogisticStorageContainer)

    def test_logistic_buffer_container(self):
        if mods.versions.get("base", DEFAULT_FACTORIO_VERSION) < (2, 0):
            entity_name = "logistic-chest-buffer"
        else:
            entity_name = "buffer-chest"
        assert isinstance(new_entity(entity_name), LogisticBufferContainer)

    def test_logistic_request_container(self):
        if mods.versions.get("base", DEFAULT_FACTORIO_VERSION) < (2, 0):
            entity_name = "logistic-chest-requester"
        else:
            entity_name = "requester-chest"
        assert isinstance(new_entity(entity_name), LogisticRequestContainer)

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
        assert isinstance(new_entity("gun-turret"), AmmoTurret)

    def test_radar(self):
        assert isinstance(new_entity("radar"), Radar)

    def test_simple_entity_with_owner(self):
        assert isinstance(new_entity("simple-entity-with-owner"), SimpleEntityWithOwner)

    def test_simple_entity_with_force(self):
        assert isinstance(new_entity("simple-entity-with-force"), SimpleEntityWithForce)

    def test_electric_energy_interface(self):
        assert isinstance(new_entity("electric-energy-interface"), ElectricEnergyInterface)

    @pytest.mark.skipif(len(linked_containers) == 0, reason="No linked containers to test")
    def test_linked_container(self):
        assert isinstance(new_entity("linked-chest"), LinkedContainer)

    def test_heat_interface(self):
        assert isinstance(new_entity("heat-interface"), HeatInterface)

    @pytest.mark.skipif(len(linked_belts) == 0, reason="No linked belts to test")
    def test_linked_belt(self):
        assert isinstance(new_entity("linked-belt"), LinkedBelt)

    def test_infinity_container(self):
        assert isinstance(new_entity("infinity-chest"), InfinityContainer)

    def test_infinity_pipe(self):
        assert isinstance(new_entity("infinity-pipe"), InfinityPipe)

    def test_burner_generator(self):
        assert isinstance(new_entity("burner-generator"), BurnerGenerator)

    @pytest.mark.skipif(
        mods.versions.get("base", DEFAULT_FACTORIO_VERSION) >= (2, 0, 0), 
        reason="Player ports deprecated > Factorio 2.0"
    )
    def test_player_port(self):
        assert isinstance(new_entity("player-port"), PlayerPort)

    def test_new_entity_from_dict(self):
        e = new_entity_from_dict({
            "name": "wooden-chest",
            "position": {"x": 0.5, "y": 0.5},
            "bar": 5
        })
        assert isinstance(e, Container)
        assert e.name == "wooden-chest"
        assert e.position.x == 0.5 and e.position.y == 0.5
        assert e.bar == 5

        with pytest.warns(UnknownEntityWarning):
            e = new_entity_from_dict(
                {
                    "name": "who knows",
                    "position": {"x": 0.5, "y": 0.5},
                    "bar": 5,
                }
            )
        assert isinstance(e, Entity)
        assert e.name == "who knows"
        assert e.position.x == 0.5 and e.position.y == 0.5
        assert e.extra_keys["bar"] == 5

    def test_unknown(self):
        # Try and treat as a generic entity
        with pytest.warns(UnknownEntityWarning):
            result = new_entity("unknown", position=(0.5, 0.5))
        assert isinstance(result, Entity)
        
        # Generic entities should be able to handle attribute access and serialization
        assert result.name == "unknown"
        assert result.position == Vector(0.5, 0.5)
        assert result.to_dict() == {
            "name": "unknown",
            "position": {"x": 0.5, "y": 0.5}
        }
        
        # You should also be able to set new attributes to them without Draftsman
        # complaining
        with pytest.warns(UnknownEntityWarning):
            result = new_entity("unknown", position=(0.5, 0.5), direction=4)
        assert result.to_dict() == {
            "name": "unknown",
            "position": {"x": 0.5, "y": 0.5},
            "direction": 4
        }

        # After construction, as well
        result.extra_keys["new_thing"] = "extra!"
        assert result.to_dict() == {
            "name": "unknown",
            "position": {"x": 0.5, "y": 0.5},
            "direction": 4,
            "new_thing": "extra!"
        }

        # Draftsman will still complain about the unknown entity, but it doesn't 
        # panic unless you want it to
        with pytest.warns(UnknownEntityWarning):
            result.validate(mode=ValidationMode.PEDANTIC).reissue_all()

        # However, setting known attributes incorrectly should still create
        # issues
        result.validate_assignment = ValidationMode.STRICT
        with pytest.raises(DataFormatError):
            result.tags = "incorrect"


# fmt: on
