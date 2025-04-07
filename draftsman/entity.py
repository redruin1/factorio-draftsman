# entity.py

"""
Entity alias module. Imports the base-class :py:class:`.Entity`, as well as
all the prototypes in :py:mod:`draftsman.prototypes`.
"""

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

from typing import Literal


def new_entity(name: str, **kwargs):
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

    :returns: A new :py:class:`.Entity` subclass, or an instance of
        :py:class:`.Entity` if `name` could not be deduced under the current
        Factorio environment.
    """
    # Remove entity_number from an input dict, as it is only meaningful when
    # exporting
    # TODO: this should probably be done elsewhere
    kwargs.pop("entity_number", None)
    # TODO: this would be better as a dict
    if name in of_type["accumulator"]:
        return Accumulator(name, **kwargs)
    if name in of_type["agricultural-tower"]:
        return AgriculturalTower(name, **kwargs)
    if name in of_type["ammo-turret"]:
        return AmmoTurret(name, **kwargs)
    if name in of_type["arithmetic-combinator"]:
        return ArithmeticCombinator(name, **kwargs)
    if name in of_type["artillery-turret"]:
        return ArtilleryTurret(name, **kwargs)
    if name in of_type["artillery-wagon"]:
        return ArtilleryWagon(name, **kwargs)
    if name in of_type["assembling-machine"]:
        return AssemblingMachine(name, **kwargs)
    if name in of_type["beacon"]:
        return Beacon(name, **kwargs)
    if name in of_type["boiler"]:
        return Boiler(name, **kwargs)
    if name in of_type["burner-generator"]:
        return BurnerGenerator(name, **kwargs)
    if name in of_type["car"]:
        return Car(name, **kwargs)
    if name in of_type["cargo-bay"]:
        return CargoBay(name, **kwargs)
    if name in of_type["cargo-landing-pad"]:
        return CargoLandingPad(name, **kwargs)
    if name in of_type["cargo-wagon"]:
        return CargoWagon(name, **kwargs)
    if name in of_type["constant-combinator"]:
        return ConstantCombinator(name, **kwargs)
    if name in of_type["container"]:
        return Container(name, **kwargs)
    if name in of_type["curved-rail-a"]:
        return CurvedRailA(name, **kwargs)
    if name in of_type["curved-rail-b"]:
        return CurvedRailB(name, **kwargs)
    if name in of_type["decider-combinator"]:
        return DeciderCombinator(name, **kwargs)
    if name in of_type["display-panel"]:
        return DisplayPanel(name, **kwargs)
    if name in of_type["electric-energy-interface"]:
        return ElectricEnergyInterface(name, **kwargs)
    if name in of_type["electric-pole"]:
        return ElectricPole(name, **kwargs)
    if name in of_type["electric-turret"]:
        return ElectricTurret(name, **kwargs)
    if name in of_type["elevated-curved-rail-a"]:
        return ElevatedCurvedRailA(name, **kwargs)
    if name in of_type["elevated-curved-rail-b"]:
        return ElevatedCurvedRailB(name, **kwargs)
    if name in of_type["elevated-half-diagonal-rail"]:
        return ElevatedHalfDiagonalRail(name, **kwargs)
    if name in of_type["elevated-straight-rail"]:
        return ElevatedStraightRail(name, **kwargs)
    if name in of_type["fluid-turret"]:
        return FluidTurret(name, **kwargs)
    if name in of_type["fluid-wagon"]:
        return FluidWagon(name, **kwargs)
    if name in of_type["furnace"]:
        return Furnace(name, **kwargs)
    if name in of_type["fusion-generator"]:
        return FusionGenerator(name, **kwargs)
    if name in of_type["fusion-reactor"]:
        return FusionReactor(name, **kwargs)
    if name in of_type["gate"]:
        return Gate.from_dict({"name": name, **kwargs})
    if name in of_type["generator"]:
        return Generator(name, **kwargs)
    if name in of_type["half-diagonal-rail"]:
        return HalfDiagonalRail(name, **kwargs)
    if name in of_type["heat-interface"]:
        return HeatInterface(name, **kwargs)
    if name in of_type["heat-pipe"]:
        return HeatPipe(name, **kwargs)
    if name in of_type["infinity-container"]:
        return InfinityContainer(name, **kwargs)
    if name in of_type["infinity-pipe"]:
        return InfinityPipe(name, **kwargs)
    if name in of_type["inserter"]:
        return Inserter(name, **kwargs)
    if name in of_type["lab"]:
        return Lab(name, **kwargs)
    if name in of_type["lamp"]:
        return Lamp(name, **kwargs)
    if name in of_type["land-mine"]:
        return LandMine(name, **kwargs)
    if name in of_type["legacy-curved-rail"]:
        return LegacyCurvedRail(name, **kwargs)
    if name in of_type["legacy-straight-rail"]:
        return LegacyStraightRail(name, **kwargs)
    if name in of_type["lightning-attractor"]:
        return LightningAttractor(name, **kwargs)
    if name in of_type["linked-belt"]:
        return LinkedBelt(name, **kwargs)
    if name in of_type["linked-container"]:
        return LinkedContainer(name, **kwargs)
    if name in of_type["loader"]:
        return Loader(name, **kwargs)
    if name in of_type["locomotive"]:
        return Locomotive(name, **kwargs)
    if name in of_type["logistic-container-active"]:
        return LogisticActiveContainer.from_dict({"name": name, **kwargs})
    if name in of_type["logistic-container-buffer"]:
        return LogisticBufferContainer.from_dict({"name": name, **kwargs})
    if name in of_type["logistic-container-passive"]:
        return LogisticPassiveContainer.from_dict({"name": name, **kwargs})
    if name in of_type["logistic-container-request"]:
        return LogisticRequestContainer.from_dict({"name": name, **kwargs})
    if name in of_type["logistic-container-storage"]:
        return LogisticStorageContainer.from_dict({"name": name, **kwargs})
    if name in of_type["mining-drill"]:
        return MiningDrill(name, **kwargs)
    if name in of_type["offshore-pump"]:
        return OffshorePump(name, **kwargs)
    if name in of_type["pipe"]:
        return Pipe(name, **kwargs)
    if name in of_type["player-port"]:
        return PlayerPort(name, **kwargs)
    if name in of_type["power-switch"]:
        return PowerSwitch(name, **kwargs)
    if name in of_type["programmable-speaker"]:
        return ProgrammableSpeaker(name, **kwargs)
    if name in of_type["pump"]:
        return Pump(name, **kwargs)
    if name in of_type["radar"]:
        return Radar(name, **kwargs)
    if name in of_type["rail-chain-signal"]:
        return RailChainSignal(name, **kwargs)
    if name in of_type["rail-ramp"]:
        return RailRamp(name, **kwargs)
    if name in of_type["rail-signal"]:
        return RailSignal.from_dict({"name": name, **kwargs})
    if name in of_type["rail-support"]:
        return RailSupport(name, **kwargs)
    if name in of_type["reactor"]:
        return Reactor(name, **kwargs)
    if name in of_type["roboport"]:
        return Roboport(name, **kwargs)
    if name in of_type["rocket-silo"]:
        return RocketSilo(name, **kwargs)
    if name in of_type["selector-combinator"]:
        return SelectorCombinator(name, **kwargs)
    if name in of_type["simple-entity-with-force"]:
        return SimpleEntityWithForce(name, **kwargs)
    if name in of_type["simple-entity-with-owner"]:
        return SimpleEntityWithOwner(name, **kwargs)
    if name in of_type["solar-panel"]:
        return SolarPanel(name, **kwargs)
    if name in of_type["space-platform-hub"]:
        return SpacePlatformHub(name, **kwargs)
    if name in of_type["spider-vehicle"]:
        return SpiderVehicle(name, **kwargs)
    if name in of_type["splitter"]:
        return Splitter(name, **kwargs)
    if name in of_type["storage-tank"]:
        return StorageTank(name, **kwargs)
    if name in of_type["straight-rail"]:
        return StraightRail(name, **kwargs)
    if name in of_type["thruster"]:
        return Thruster(name, **kwargs)
    if name in of_type["train-stop"]:
        return TrainStop(name, **kwargs)
    if name in of_type["transport-belt"]:
        return TransportBelt(name, **kwargs)
    if name in of_type["underground-belt"]:
        return UndergroundBelt(name, **kwargs)
    if name in of_type["pipe-to-ground"]:
        return UndergroundPipe(name, **kwargs)
    if name in of_type["wall"]:
        return Wall.from_dict({"name": name, **kwargs})

    # At this point, the name is unrecognized by the current environment.
    # We want Draftsman to at least try to parse it and serialize it, if not
    # entirely validate it. Thus, we construct a generic instance of `Entity`
    # and return that.
    result = Entity(name, similar_entities=None, **kwargs)

    # Mark this class as unknown format, so some validation checks are
    # omitted
    # TODO: is this necessary?
    result._unknown = True

    # Of course, since entity is normally a base class, we have to do a
    # little magic to make it behave similar to all other classes
    validate_assignment = kwargs.get("validate_assignment", ValidationMode.STRICT)
    result.validation = validate_assignment

    return result


def get_class(d: dict):
    """
    Returns the Draftsman class that the input entity JSON dict would be
    resolved to if imported with ``from_dict()``.
    """
    # If input entity is entirely unknown, just return the base class
    if d["name"] not in raw:
        return Entity
    # d_type = (raw[d["name"]]["type"], raw[d["name"]].get("logistic_mode"))
    d_type = raw[d["name"]]["type"]
    if d_type == "logistic-container":
        d_type = (d_type, raw[d["name"]]["logistic_mode"])
    type_mappings = {
        "accumulator": Accumulator,
        "agricultural-tower": AgriculturalTower,
        "ammo-turret": AmmoTurret,
        "arithmetic-combinator": ArithmeticCombinator,
        "artillery-turret": ArtilleryTurret,
        "artillery-wagon": ArtilleryWagon,
        "cargo-wagon": CargoWagon,
        "constant-combinator": ConstantCombinator,
        "container": Container,
        "decider-combinator": DeciderCombinator,
        "electric-pole": ElectricPole,
        "electric-turret": ElectricTurret,
        "fluid-turret": FluidTurret,
        "fluid-wagon": FluidWagon,
        "gate": Gate,
        "inserter": Inserter,
        "lamp": Lamp,
        "landmine": LandMine,
        "legacy-curved-rail": LegacyCurvedRail,
        "legacy-straight-rail": LegacyStraightRail,
        "locomotive": Locomotive,
        ("logistic-container", "active-provider"): LogisticActiveContainer,
        ("logistic-container", "buffer"): LogisticBufferContainer,
        ("logistic-container", "passive-provider"): LogisticPassiveContainer,
        ("logistic-container", "requester"): LogisticRequestContainer,
        ("logistic-container", "storage"): LogisticStorageContainer,
        "pipe": Pipe,
        "power-switch": PowerSwitch,
        "programmable-speaker": ProgrammableSpeaker,
        "pump": Pump,
        "solar-panel": SolarPanel,
        "storage-tank": StorageTank,
        "radar": Radar,
        "rail-chain-signal": RailChainSignal,
        "rail-signal": RailSignal,
        "roboport": Roboport,
        "splitter": Splitter,
        "train-stop": TrainStop,
        "transport-belt": TransportBelt,
        "underground-belt": UndergroundBelt,
        "pipe-to-ground": UndergroundPipe,
        "wall": Wall,
    }
    return type_mappings.get(d_type, Entity)
