# entity.py

"""
Entity alias module. Imports the base-class :py:class:`.Entity`, as well as
all the prototypes in :py:mod:`draftsman.prototypes`.
"""

from draftsman import __factorio_version_info__
from draftsman.classes.entity import Entity
from draftsman.constants import ValidationMode
from draftsman.error import InvalidEntityError
from draftsman.data.entities import of_type, raw

# fmt: off
from draftsman.prototypes.accumulator import Accumulator, accumulators
from draftsman.prototypes.agricultural_tower import AgriculturalTower, agricultural_towers
from draftsman.prototypes.ammo_turret import AmmoTurret, ammo_turrets
from draftsman.prototypes.arithmetic_combinator import ArithmeticCombinator, arithmetic_combinators
from draftsman.prototypes.artillery_turret import ArtilleryTurret, artillery_turrets
from draftsman.prototypes.artillery_wagon import ArtilleryWagon, artillery_wagons
from draftsman.prototypes.assembling_machine import AssemblingMachine, assembling_machines
from draftsman.prototypes.asteroid_collector import AsteroidCollector, asteroid_collectors
from draftsman.prototypes.beacon import Beacon, beacons
from draftsman.prototypes.boiler import Boiler, boilers
from draftsman.prototypes.burner_generator import BurnerGenerator, burner_generators
from draftsman.prototypes.car import Car, cars
from draftsman.prototypes.cargo_bay import CargoBay, cargo_bays
from draftsman.prototypes.cargo_landing_pad import CargoLandingPad, cargo_landing_pads
from draftsman.prototypes.cargo_wagon import CargoWagon, cargo_wagons
from draftsman.prototypes.constant_combinator import ConstantCombinator, constant_combinators
from draftsman.prototypes.container import Container, containers
from draftsman.prototypes.curved_rail_a import CurvedRailA, curved_rails_a
from draftsman.prototypes.curved_rail_b import CurvedRailB, curved_rails_b
from draftsman.prototypes.decider_combinator import DeciderCombinator, decider_combinators
from draftsman.prototypes.display_panel import DisplayPanel, display_panels
from draftsman.prototypes.electric_energy_interface import ElectricEnergyInterface, electric_energy_interfaces
from draftsman.prototypes.electric_pole import ElectricPole, electric_poles
from draftsman.prototypes.electric_turret import ElectricTurret, electric_turrets
from draftsman.prototypes.elevated_curved_rail_a import ElevatedCurvedRailA, elevated_curved_rails_a
from draftsman.prototypes.elevated_curved_rail_b import ElevatedCurvedRailB, elevated_curved_rails_b
from draftsman.prototypes.elevated_half_diagonal_rail import ElevatedHalfDiagonalRail, elevated_half_diagonal_rails
from draftsman.prototypes.elevated_straight_rail import ElevatedStraightRail, elevated_straight_rails
from draftsman.prototypes.fluid_turret import FluidTurret, fluid_turrets
from draftsman.prototypes.fluid_wagon import FluidWagon, fluid_wagons
from draftsman.prototypes.furnace import Furnace, furnaces
from draftsman.prototypes.fusion_generator import FusionGenerator, fusion_generators
from draftsman.prototypes.fusion_reactor import FusionReactor, fusion_reactors
from draftsman.prototypes.gate import Gate, gates
from draftsman.prototypes.generator import Generator, generators
from draftsman.prototypes.half_diagonal_rail import HalfDiagonalRail, half_diagonal_rails
from draftsman.prototypes.heat_interface import HeatInterface, heat_interfaces
from draftsman.prototypes.heat_pipe import HeatPipe, heat_pipes
from draftsman.prototypes.infinity_container import InfinityContainer, infinity_containers
from draftsman.prototypes.infinity_pipe import InfinityPipe, infinity_pipes
from draftsman.prototypes.inserter import Inserter, inserters
from draftsman.prototypes.lab import Lab, labs
from draftsman.prototypes.lamp import Lamp, lamps
from draftsman.prototypes.land_mine import LandMine, land_mines
from draftsman.prototypes.legacy_curved_rail import LegacyCurvedRail, legacy_curved_rails
from draftsman.prototypes.legacy_straight_rail import LegacyStraightRail, legacy_straight_rails
from draftsman.prototypes.lightning_attractor import LightningAttractor, lightning_attractors
from draftsman.prototypes.linked_belt import LinkedBelt, linked_belts
from draftsman.prototypes.linked_container import LinkedContainer, linked_containers
from draftsman.prototypes.loader import Loader, loaders
# from draftsman.prototypes.loader_1x1 import Loader1x1, loaders_1x1
from draftsman.prototypes.locomotive import Locomotive, locomotives
from draftsman.prototypes.logistic_active_container import LogisticActiveContainer, logistic_active_containers
from draftsman.prototypes.logistic_buffer_container import LogisticBufferContainer, logistic_buffer_containers
from draftsman.prototypes.logistic_passive_container import LogisticPassiveContainer, logistic_passive_containers
from draftsman.prototypes.logistic_request_container import LogisticRequestContainer, logistic_request_containers
from draftsman.prototypes.logistic_storage_container import LogisticStorageContainer, logistic_storage_containers
from draftsman.prototypes.mining_drill import MiningDrill, mining_drills
from draftsman.prototypes.offshore_pump import OffshorePump, offshore_pumps
from draftsman.prototypes.pipe import Pipe, pipes
from draftsman.prototypes.player_port import PlayerPort, player_ports
from draftsman.prototypes.power_switch import PowerSwitch, power_switches
from draftsman.prototypes.programmable_speaker import ProgrammableSpeaker, programmable_speakers
from draftsman.prototypes.pump import Pump, pumps
from draftsman.prototypes.radar import Radar, radars
from draftsman.prototypes.rail_chain_signal import RailChainSignal, rail_chain_signals
from draftsman.prototypes.rail_ramp import RailRamp, rail_ramps
from draftsman.prototypes.rail_signal import RailSignal, rail_signals
from draftsman.prototypes.rail_support import RailSupport, rail_supports
from draftsman.prototypes.reactor import Reactor, reactors
from draftsman.prototypes.roboport import Roboport, roboports
from draftsman.prototypes.rocket_silo import RocketSilo, rocket_silos
from draftsman.prototypes.selector_combinator import SelectorCombinator, selector_combinators
from draftsman.prototypes.simple_entity_with_force import SimpleEntityWithForce, simple_entities_with_force
from draftsman.prototypes.simple_entity_with_owner import SimpleEntityWithOwner, simple_entities_with_owner
from draftsman.prototypes.solar_panel import SolarPanel, solar_panels
from draftsman.prototypes.space_platform_hub import SpacePlatformHub, space_platform_hubs
from draftsman.prototypes.spider_vehicle import SpiderVehicle, spider_vehicles
from draftsman.prototypes.splitter import Splitter, splitters
from draftsman.prototypes.storage_tank import StorageTank, storage_tanks
from draftsman.prototypes.straight_rail import StraightRail, straight_rails
from draftsman.prototypes.thruster import Thruster, thrusters
from draftsman.prototypes.train_stop import TrainStop, train_stops
from draftsman.prototypes.transport_belt import TransportBelt, transport_belts
from draftsman.prototypes.underground_belt import UndergroundBelt, underground_belts
from draftsman.prototypes.underground_pipe import UndergroundPipe, underground_pipes
from draftsman.prototypes.wall import Wall, walls
# fmt: on

from typing import Optional


def get_entity_class(name: str) -> type[Entity]:
    """
    Deduce the Draftsman :py:class:`Entity` subclass that this entity name would
    be an instance of. If Draftman cannot determine a subclass that this entity
    matches, it returns the base :py:class:`Entity` class itself.
    """
    # If input entity is entirely unknown, just return the base class
    if name not in raw:
        return Entity
    # d_type = (raw[d["name"]]["type"], raw[d["name"]].get("logistic_mode"))
    d_type = raw[name]["type"]
    if d_type == "logistic-container":
        d_type = (d_type, raw[name]["logistic_mode"])
    type_mappings = {
        "accumulator": Accumulator,
        "agricultural-tower": AgriculturalTower,
        "ammo-turret": AmmoTurret,
        "arithmetic-combinator": ArithmeticCombinator,
        "artillery-turret": ArtilleryTurret,
        "artillery-wagon": ArtilleryWagon,
        "assembling-machine": AssemblingMachine,
        "asteroid-collector": AsteroidCollector,
        "beacon": Beacon,
        "boiler": Boiler,
        "burner-generator": BurnerGenerator,
        "car": Car,
        "cargo-bay": CargoBay,
        "cargo-landing-pad": CargoLandingPad,
        "cargo-wagon": CargoWagon,
        "constant-combinator": ConstantCombinator,
        "container": Container,
        "curved-rail-a": CurvedRailA,
        "curved-rail-b": CurvedRailB,
        "decider-combinator": DeciderCombinator,
        "display-panel": DisplayPanel,
        "electric-energy-interface": ElectricEnergyInterface,
        "electric-pole": ElectricPole,
        "electric-turret": ElectricTurret,
        "elevated-curved-rail-a": ElevatedCurvedRailA,
        "elevated-curved-rail-b": ElevatedCurvedRailB,
        "elevated-half-diagonal-rail": ElevatedHalfDiagonalRail,
        "elevated-straight-rail": ElevatedStraightRail,
        "fluid-turret": FluidTurret,
        "fluid-wagon": FluidWagon,
        "furnace": Furnace,
        "fusion-generator": FusionGenerator,
        "fusion-reactor": FusionReactor,
        "gate": Gate,
        "generator": Generator,
        "half-diagonal-rail": HalfDiagonalRail,
        "heat-interface": HeatInterface,
        "heat-pipe": HeatPipe,
        "infinity-container": InfinityContainer,
        "infinity-pipe": InfinityPipe,
        "inserter": Inserter,
        "lab": Lab,
        "lamp": Lamp,
        "land-mine": LandMine,
        "legacy-curved-rail": LegacyCurvedRail,
        "legacy-straight-rail": LegacyStraightRail,
        "lightning-attractor": LightningAttractor,
        "linked-belt": LinkedBelt,
        "linked-container": LinkedContainer,
        "loader": Loader,
        "locomotive": Locomotive,
        ("logistic-container", "active-provider"): LogisticActiveContainer,
        ("logistic-container", "buffer"): LogisticBufferContainer,
        ("logistic-container", "passive-provider"): LogisticPassiveContainer,
        ("logistic-container", "requester"): LogisticRequestContainer,
        ("logistic-container", "storage"): LogisticStorageContainer,
        "mining-drill": MiningDrill,
        "offshore-pump": OffshorePump,
        "pipe": Pipe,
        "player-port": PlayerPort,
        "power-switch": PowerSwitch,
        "programmable-speaker": ProgrammableSpeaker,
        "pump": Pump,
        "radar": Radar,
        "rail-chain-signal": RailChainSignal,
        "rail-ramp": RailRamp,
        "rail-signal": RailSignal,
        "rail-support": RailSupport,
        "reactor": Reactor,
        "roboport": Roboport,
        "rocket-silo": RocketSilo,
        "selector-combinator": SelectorCombinator,
        "simple-entity-with-force": SimpleEntityWithForce,
        "simple-entity-with-owner": SimpleEntityWithOwner,
        "solar-panel": SolarPanel,
        "space-platform-hub": SpacePlatformHub,
        "spider-vehicle": SpiderVehicle,
        "splitter": Splitter,
        "storage-tank": StorageTank,
        "straight-rail": StraightRail,
        "train-stop": TrainStop,
        "transport-belt": TransportBelt,
        "underground-belt": UndergroundBelt,
        "pipe-to-ground": UndergroundPipe,
        "wall": Wall,
    }
    return type_mappings.get(d_type, Entity)


def new_entity(name: str, **kwargs) -> Entity:
    """
    Factory function for creating a new :py:class:`.Entity`. The class used will be
    based on the entity's name, so ``new_entity("wooden-chest")`` will return a
    :py:mod:`.Container` instance. Useful if you know the name of the Entity you
    want to make, but don't know what type it is.

    Any additional keyword arguments are passed to the entity's constructor,
    allowing you to specify the entity's position, ID, or any other relevant
    information during construction.

    Raises :py:class:`~draftsman.warning.DraftsmanWarning` if any keyword passed
    in is not recognized by that Entity's class constructor.

    :param name: The string name of an Entity.
    :param kwargs: A dict of all the keyword arguments to pass to the
        constructor.

    :returns: A new instance of a :py:class:`.Entity` subclass, or an instance
        of :py:class:`.Entity` if `name` could not be deduced under the current
        Factorio environment.
    """
    return get_entity_class(name)(name, **kwargs)


def new_entity_from_dict(
    d: dict,
    version: Optional[tuple[int]] = None,
    validation: ValidationMode = ValidationMode.NONE,
) -> Entity:
    """
    Factory function similar to :py:meth:`.new_entity`, but using `Entity.from_dict()`
    as opposed to the entity's constructor. Allows you to generically construct
    a Draftsman entity instance directly from raw JSON data, if convenient to do
    so.

    Which :py:class:`Entity` subclass instance this method returns is based off
    of the given dictionaries ``"name"`` key. If Draftsman cannot determine
    entity type off of this name, it returns a generic :py:class:`.Entity`
    instance instead.

    :param d: The dictionary object to construct the new entity from.
    :param version: The Factorio game version under which to interpret the data
        as. If ``None``, defaults to the game version of the current environment.
    :param validation: The validation level to run after entity construction.

    :returns: A new instance of a :py:class:`.Entity` subclass, or an instance
        of :py:class:`.Entity` if `name` could not be deduced under the current
        Factorio environment.
    """
    return get_entity_class(d.get("name", None)).from_dict(
        d, version=version, validation=validation
    )
