# entities.py
# -*- encoding: utf-8 -*-

import pickle

try:  # pragma: no coverage
    import importlib.resources as pkg_resources  # type: ignore
except ImportError:  # pragma: no coverage
    # Try backported to PY<37 `importlib_resources`.
    import importlib_resources as pkg_resources  # type: ignore

from draftsman import data


with pkg_resources.open_binary(data, "entities.pkl") as inp:
    _data = pickle.load(inp)

    # Aggregation of all the the entity dicts from data.raw collected in one
    # place.
    raw = _data["raw"]

    # Whether or not each entity is flippable, indexed by their name.
    flippable = _data["flippable"]

    # Ordered lists of strings, each containing a valid name for that entity
    # type, sorted by their Factorio order strings.
    containers = _data["containers"]
    storage_tanks = _data["storage_tanks"]
    transport_belts = _data["transport_belts"]
    underground_belts = _data["underground_belts"]
    splitters = _data["splitters"]
    inserters = _data["inserters"]
    filter_inserters = _data["filter_inserters"]
    loaders = _data["loaders"]
    electric_poles = _data["electric_poles"]
    pipes = _data["pipes"]
    underground_pipes = _data["underground_pipes"]
    pumps = _data["pumps"]
    straight_rails = _data["straight_rails"]
    curved_rails = _data["curved_rails"]
    train_stops = _data["train_stops"]
    rail_signals = _data["rail_signals"]
    rail_chain_signals = _data["rail_chain_signals"]
    locomotives = _data["locomotives"]
    cargo_wagons = _data["cargo_wagons"]
    fluid_wagons = _data["fluid_wagons"]
    artillery_wagons = _data["artillery_wagons"]
    logistic_passive_containers = _data["logistic_passive_containers"]
    logistic_active_containers = _data["logistic_active_containers"]
    logistic_storage_containers = _data["logistic_storage_containers"]
    logistic_buffer_containers = _data["logistic_buffer_containers"]
    logistic_request_containers = _data["logistic_request_containers"]
    roboports = _data["roboports"]
    lamps = _data["lamps"]
    arithmetic_combinators = _data["arithmetic_combinators"]
    decider_combinators = _data["decider_combinators"]
    constant_combinators = _data["constant_combinators"]
    power_switches = _data["power_switches"]
    programmable_speakers = _data["programmable_speakers"]
    boilers = _data["boilers"]
    generators = _data["generators"]
    solar_panels = _data["solar_panels"]
    accumulators = _data["accumulators"]
    reactors = _data["reactors"]
    heat_pipes = _data["heat_pipes"]
    mining_drills = _data["mining_drills"]
    offshore_pumps = _data["offshore_pumps"]
    furnaces = _data["furnaces"]
    assembling_machines = _data["assembling_machines"]
    labs = _data["labs"]
    beacons = _data["beacons"]
    rocket_silos = _data["rocket_silos"]
    land_mines = _data["land_mines"]
    walls = _data["walls"]
    gates = _data["gates"]
    turrets = _data["turrets"]
    radars = _data["radars"]
    electric_energy_interfaces = _data["electric_energy_interfaces"]
    linked_containers = _data["linked_containers"]
    heat_interfaces = _data["heat_interfaces"]
    linked_belts = _data["linked_belts"]
    infinity_containers = _data["infinity_containers"]
    infinity_pipes = _data["infinity_pipes"]
    burner_generators = _data["burner_generators"]
