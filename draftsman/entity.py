# entity.py

"""
Entity alias module. Imports the base-class :py:class:`.Entity`, as well as
all the prototypes in :py:mod:`draftsman.prototypes`.
"""

from draftsman.classes.entity import Entity
from draftsman.error import InvalidEntityError


# fmt: off
from draftsman.prototypes.container import Container, containers
from draftsman.prototypes.storage_tank import StorageTank, storage_tanks
from draftsman.prototypes.transport_belt import TransportBelt, transport_belts
from draftsman.prototypes.underground_belt import UndergroundBelt, underground_belts
from draftsman.prototypes.splitter import Splitter, splitters
from draftsman.prototypes.inserter import Inserter, inserters
from draftsman.prototypes.filter_inserter import FilterInserter, filter_inserters
from draftsman.prototypes.loader import Loader, loaders
from draftsman.prototypes.electric_pole import ElectricPole, electric_poles
from draftsman.prototypes.pipe import Pipe, pipes
from draftsman.prototypes.underground_pipe import UndergroundPipe, underground_pipes
from draftsman.prototypes.pump import Pump, pumps
from draftsman.prototypes.straight_rail import StraightRail, straight_rails
from draftsman.prototypes.curved_rail import CurvedRail, curved_rails
from draftsman.prototypes.train_stop import TrainStop, train_stops
from draftsman.prototypes.rail_signal import RailSignal, rail_signals
from draftsman.prototypes.rail_chain_signal import RailChainSignal, rail_chain_signals
from draftsman.prototypes.locomotive import Locomotive, locomotives
from draftsman.prototypes.cargo_wagon import CargoWagon, cargo_wagons
from draftsman.prototypes.fluid_wagon import FluidWagon, fluid_wagons
from draftsman.prototypes.artillery_wagon import ArtilleryWagon, artillery_wagons
from draftsman.prototypes.logistic_passive_container import LogisticPassiveContainer, logistic_passive_containers
from draftsman.prototypes.logistic_active_container import LogisticActiveContainer, logistic_active_containers
from draftsman.prototypes.logistic_storage_container import LogisticStorageContainer, logistic_storage_containers
from draftsman.prototypes.logistic_buffer_container import LogisticBufferContainer, logistic_buffer_containers
from draftsman.prototypes.logistic_request_container import LogisticRequestContainer, logistic_request_containers
from draftsman.prototypes.roboport import Roboport, roboports
from draftsman.prototypes.lamp import Lamp, lamps
from draftsman.prototypes.arithmetic_combinator import ArithmeticCombinator, arithmetic_combinators
from draftsman.prototypes.decider_combinator import DeciderCombinator, decider_combinators
from draftsman.prototypes.constant_combinator import ConstantCombinator, constant_combinators
from draftsman.prototypes.power_switch import PowerSwitch, power_switches
from draftsman.prototypes.programmable_speaker import ProgrammableSpeaker, programmable_speakers
from draftsman.prototypes.boiler import Boiler, boilers
from draftsman.prototypes.generator import Generator, generators
from draftsman.prototypes.solar_panel import SolarPanel, solar_panels
from draftsman.prototypes.accumulator import Accumulator, accumulators
from draftsman.prototypes.reactor import Reactor, reactors
from draftsman.prototypes.heat_pipe import HeatPipe, heat_pipes
from draftsman.prototypes.mining_drill import MiningDrill, mining_drills
from draftsman.prototypes.offshore_pump import OffshorePump, offshore_pumps
from draftsman.prototypes.furnace import Furnace, furnaces
from draftsman.prototypes.assembling_machine import AssemblingMachine, assembling_machines
from draftsman.prototypes.lab import Lab, labs
from draftsman.prototypes.beacon import Beacon, beacons
from draftsman.prototypes.rocket_silo import RocketSilo, rocket_silos
from draftsman.prototypes.land_mine import LandMine, land_mines
from draftsman.prototypes.wall import Wall, walls
from draftsman.prototypes.gate import Gate, gates
from draftsman.prototypes.turret import Turret, turrets
from draftsman.prototypes.radar import Radar, radars
from draftsman.prototypes.electric_energy_interface import ElectricEnergyInterface, electric_energy_interfaces
from draftsman.prototypes.linked_container import LinkedContainer, linked_containers
from draftsman.prototypes.heat_interface import HeatInterface, heat_interfaces
from draftsman.prototypes.linked_belt import LinkedBelt, linked_belts
from draftsman.prototypes.infinity_container import InfinityContainer, infinity_containers
from draftsman.prototypes.infinity_pipe import InfinityPipe, infinity_pipes
from draftsman.prototypes.burner_generator import BurnerGenerator, burner_generators
# fmt: on


def new_entity(name, **kwargs):
    # type: (str, **dict) -> Entity
    """
    Factory function for creating a new ``Entity``. The class used will be based
    on the entity's name, so ``new_entity("wooden-chest")`` will return a
    ``Container`` instance. Useful if you know the name of the Entity you want
    to make, but don't know what type it is.

    Any additional keyword arguments are passed to the entity's constructor,
    allowing you to specify the entity's position, ID, or any other relevant
    information during construction.

    Raises :py:class:`~draftsman.warning.DraftsmanWarning` if any keyword passed
    in is not recognized by that Entity's class constructor.

    :param name: The string name of an Entity.
    :param kwargs: A dict of all the keyword arguments to pass to the
        constructor.

    :exception InvalidEntityID: If the name passed in is not recognized as any
        valid entity name.
    """
    if name in containers:
        return Container(name, **kwargs)
    if name in storage_tanks:
        return StorageTank(name, **kwargs)
    if name in transport_belts:
        return TransportBelt(name, **kwargs)
    if name in underground_belts:
        return UndergroundBelt(name, **kwargs)
    if name in splitters:
        return Splitter(name, **kwargs)
    if name in inserters:
        return Inserter(name, **kwargs)
    if name in filter_inserters:
        return FilterInserter(name, **kwargs)
    if name in loaders:
        return Loader(name, **kwargs)
    if name in electric_poles:
        return ElectricPole(name, **kwargs)
    if name in pipes:
        return Pipe(name, **kwargs)
    if name in underground_pipes:
        return UndergroundPipe(name, **kwargs)
    if name in pumps:
        return Pump(name, **kwargs)
    if name in straight_rails:
        return StraightRail(name, **kwargs)
    if name in curved_rails:
        return CurvedRail(name, **kwargs)
    if name in train_stops:
        return TrainStop(name, **kwargs)
    if name in rail_signals:
        return RailSignal(name, **kwargs)
    if name in rail_chain_signals:
        return RailChainSignal(name, **kwargs)
    if name in locomotives:
        return Locomotive(name, **kwargs)
    if name in cargo_wagons:
        return CargoWagon(name, **kwargs)
    if name in fluid_wagons:
        return FluidWagon(name, **kwargs)
    if name in artillery_wagons:
        return ArtilleryWagon(name, **kwargs)
    if name in logistic_passive_containers:
        return LogisticPassiveContainer(name, **kwargs)
    if name in logistic_active_containers:
        return LogisticActiveContainer(name, **kwargs)
    if name in logistic_storage_containers:
        return LogisticStorageContainer(name, **kwargs)
    if name in logistic_buffer_containers:
        return LogisticBufferContainer(name, **kwargs)
    if name in logistic_request_containers:
        return LogisticRequestContainer(name, **kwargs)
    if name in roboports:
        return Roboport(name, **kwargs)
    if name in lamps:
        return Lamp(name, **kwargs)
    if name in arithmetic_combinators:
        return ArithmeticCombinator(name, **kwargs)
    if name in decider_combinators:
        return DeciderCombinator(name, **kwargs)
    if name in constant_combinators:
        return ConstantCombinator(name, **kwargs)
    if name in power_switches:
        return PowerSwitch(name, **kwargs)
    if name in programmable_speakers:
        return ProgrammableSpeaker(name, **kwargs)
    if name in boilers:
        return Boiler(name, **kwargs)
    if name in generators:
        return Generator(name, **kwargs)
    if name in solar_panels:
        return SolarPanel(name, **kwargs)
    if name in accumulators:
        return Accumulator(name, **kwargs)
    if name in reactors:
        return Reactor(name, **kwargs)
    if name in heat_pipes:
        return HeatPipe(name, **kwargs)
    if name in mining_drills:
        return MiningDrill(name, **kwargs)
    if name in offshore_pumps:
        return OffshorePump(name, **kwargs)
    if name in furnaces:
        return Furnace(name, **kwargs)
    if name in assembling_machines:
        return AssemblingMachine(name, **kwargs)
    if name in labs:
        return Lab(name, **kwargs)
    if name in beacons:
        return Beacon(name, **kwargs)
    if name in rocket_silos:
        return RocketSilo(name, **kwargs)
    if name in land_mines:
        return LandMine(name, **kwargs)
    if name in walls:
        return Wall(name, **kwargs)
    if name in gates:
        return Gate(name, **kwargs)
    if name in turrets:
        return Turret(name, **kwargs)
    if name in radars:
        return Radar(name, **kwargs)
    if name in electric_energy_interfaces:
        return ElectricEnergyInterface(name, **kwargs)
    if name in linked_containers:
        return LinkedContainer(name, **kwargs)
    if name in heat_interfaces:
        return HeatInterface(name, **kwargs)
    if name in linked_belts:
        return LinkedBelt(name, **kwargs)
    if name in infinity_containers:
        return InfinityContainer(name, **kwargs)
    if name in infinity_pipes:
        return InfinityPipe(name, **kwargs)
    if name in burner_generators:
        return BurnerGenerator(name, **kwargs)

    raise InvalidEntityError("'{}'".format(name))
