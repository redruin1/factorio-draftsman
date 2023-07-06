# entities.py
# -*- encoding: utf-8 -*-

import pickle

try:  # pragma: no coverage
    import importlib.resources as pkg_resources  # type: ignore
except ImportError:  # pragma: no coverage
    # Try backported to PY<37 `importlib_resources`.
    import importlib_resources as pkg_resources  # type: ignore

from draftsman import data
from draftsman.classes.collision_set import CollisionSet
from draftsman.env import get_default_collision_mask
from draftsman.utils import PrimitiveAABB, AABB


with pkg_resources.open_binary(data, "entities.pkl") as inp:
    _data: dict = pickle.load(inp)

    # Aggregation of all the the entity dicts from data.raw collected in one
    # place.
    raw: dict[str, dict] = _data["raw"]

    # Whether or not each entity is flippable, indexed by their name.
    flippable: dict[str, bool] = _data["flippable"]

    # Indexes of unique collision sets for each entity. Shared between all
    # entity instances, so we save memory by not including it in each Entity
    # instance.
    collision_sets: dict[str, CollisionSet] = _data["collision_sets"]

    # Lists of strings, each containing a valid name for that entity type,
    # sorted by their Factorio order strings.
    containers: list[str] = _data["containers"]
    storage_tanks: list[str] = _data["storage_tanks"]
    transport_belts: list[str] = _data["transport_belts"]
    underground_belts: list[str] = _data["underground_belts"]
    splitters: list[str] = _data["splitters"]
    inserters: list[str] = _data["inserters"]
    filter_inserters: list[str] = _data["filter_inserters"]
    loaders: list[str] = _data["loaders"]
    electric_poles: list[str] = _data["electric_poles"]
    pipes: list[str] = _data["pipes"]
    underground_pipes: list[str] = _data["underground_pipes"]
    pumps: list[str] = _data["pumps"]
    straight_rails: list[str] = _data["straight_rails"]
    curved_rails: list[str] = _data["curved_rails"]
    train_stops: list[str] = _data["train_stops"]
    rail_signals: list[str] = _data["rail_signals"]
    rail_chain_signals: list[str] = _data["rail_chain_signals"]
    locomotives: list[str] = _data["locomotives"]
    cargo_wagons: list[str] = _data["cargo_wagons"]
    fluid_wagons: list[str] = _data["fluid_wagons"]
    artillery_wagons: list[str] = _data["artillery_wagons"]
    logistic_passive_containers: list[str] = _data["logistic_passive_containers"]
    logistic_active_containers: list[str] = _data["logistic_active_containers"]
    logistic_storage_containers: list[str] = _data["logistic_storage_containers"]
    logistic_buffer_containers: list[str] = _data["logistic_buffer_containers"]
    logistic_request_containers: list[str] = _data["logistic_request_containers"]
    roboports: list[str] = _data["roboports"]
    lamps: list[str] = _data["lamps"]
    arithmetic_combinators: list[str] = _data["arithmetic_combinators"]
    decider_combinators: list[str] = _data["decider_combinators"]
    constant_combinators: list[str] = _data["constant_combinators"]
    power_switches: list[str] = _data["power_switches"]
    programmable_speakers: list[str] = _data["programmable_speakers"]
    boilers: list[str] = _data["boilers"]
    generators: list[str] = _data["generators"]
    solar_panels: list[str] = _data["solar_panels"]
    accumulators: list[str] = _data["accumulators"]
    reactors: list[str] = _data["reactors"]
    heat_pipes: list[str] = _data["heat_pipes"]
    mining_drills: list[str] = _data["mining_drills"]
    offshore_pumps: list[str] = _data["offshore_pumps"]
    furnaces: list[str] = _data["furnaces"]
    assembling_machines: list[str] = _data["assembling_machines"]
    labs: list[str] = _data["labs"]
    beacons: list[str] = _data["beacons"]
    rocket_silos: list[str] = _data["rocket_silos"]
    land_mines: list[str] = _data["land_mines"]
    walls: list[str] = _data["walls"]
    gates: list[str] = _data["gates"]
    turrets: list[str] = _data["turrets"]
    radars: list[str] = _data["radars"]
    simple_entities_with_owner: list[str] = _data["simple_entities_with_owner"]
    simple_entities_with_force: list[str] = _data["simple_entities_with_force"]
    electric_energy_interfaces: list[str] = _data["electric_energy_interfaces"]
    linked_containers: list[str] = _data["linked_containers"]
    heat_interfaces: list[str] = _data["heat_interfaces"]
    linked_belts: list[str] = _data["linked_belts"]
    infinity_containers: list[str] = _data["infinity_containers"]
    infinity_pipes: list[str] = _data["infinity_pipes"]
    burner_generators: list[str] = _data["burner_generators"]
    player_ports: list[str] = _data["player_ports"]


def add_entity(
    name: str,
    entity_type: str,
    collision_box: PrimitiveAABB,
    collision_mask: set[str] = None,
    hidden: bool = False,
    **kwargs
):
    """
    Temporarily adds an entity to :py:mod:`draftsman.data.entities`.

    This is useful if you want to temporarily add an entity to the load process
    to quickly simulate a mod being present when it currently isn't. For example,
    you might want to be able to load a blueprint with modded entities in order
    to replace them with regular ones, but want the benefit of error checking
    without having to install the associated mods.

    :param name: The Factorio ID of the entity to add.
    :param entity_type: The type string of the entity.
    :param collision_box: The AABB of the entity, to check for collisions.
    :param collision_mask: The collision layers that this entity uses, to check
        for collisions.
    :param kwargs: Any other entity specific data that you want to populate the
        new entity with.
    """
    entity_map = {
        "container": containers,
        "storage-tank": storage_tanks,
        "transport-belt": transport_belts,
        "underground-belt": underground_belts,
        "splitter": splitters,
        "inserter": inserters,
        "filter-inserter": filter_inserters,
        "loader": loaders,
        "electric-pole": electric_poles,
        "pipe": pipes,
        "pipe-to-ground": underground_pipes,
        "pump": pumps,
        "straight-rail": straight_rails,
        "curved-rail": curved_rails,
        "train-stop": train_stops,
        "rail-signal": rail_signals,
        "rail-chain-signal": rail_chain_signals,
        "locomotive": locomotives,
        "cargo-wagon": cargo_wagons,
        "fluid-wagon": fluid_wagons,
        "artillery-wagon": artillery_wagons,
        "logistic-container": logistic_passive_containers,  # FIXME
        "roboport": roboports,
        "lamp": lamps,
        "arithmetic-combinator": arithmetic_combinators,
        "decider-combinator": decider_combinators,
        "constant-combinator": constant_combinators,
        "power-switch": power_switches,
        "programmable-speaker": programmable_speakers,
        "boiler": boilers,
        "generator": generators,
        "solar-panel": solar_panels,
        "accumulator": accumulators,
        "reactor": reactors,
        "heat-pipe": heat_pipes,
        "mining-drill": mining_drills,
        "offshore-pump": offshore_pumps,
        "furnace": furnaces,
        "assembling-machine": assembling_machines,
        "lab": labs,
        "beacon": beacons,
        "rocket-silo": rocket_silos,
        "land-mine": land_mines,
        "wall": walls,
        "gate": gates,
        "turret": turrets,  # FIXME
        "radar": radars,
        "electric-energy-interface": electric_energy_interfaces,
        "linked-container": linked_containers,
        "heat-interface": heat_interfaces,
        "linked-belt": linked_belts,
        "infinity-container": infinity_containers,
        "infinity-pipe": infinity_pipes,
        "burner-generator": burner_generators,
    }

    if entity_type not in entity_map:
        raise ValueError("Unrecognized 'entity_type' '{}'".format(entity_type))

    raw[name] = {
        "name": name,
        "type": entity_type,
        "collision_box": collision_box,
        "flags": set(),
    }

    if collision_mask is not None:
        raw[name]["collision_mask"] = set(collision_mask)
    else:
        raw[name]["collision_mask"] = get_default_collision_mask(entity_type)

    if hidden:
        raw[name]["flags"].add("hidden")

    # Add everything else
    raw[name].update(kwargs)

    # Update others
    collision_sets[name] = CollisionSet(
        [
            AABB(
                collision_box[0][0],
                collision_box[0][1],
                collision_box[1][0],
                collision_box[1][1],
            )
        ]
    )

    entity_map[entity_type].append(name)
