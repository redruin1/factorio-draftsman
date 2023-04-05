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
    _data = pickle.load(inp)

    # Aggregation of all the the entity dicts from data.raw collected in one
    # place.
    raw = _data["raw"]

    # Whether or not each entity is flippable, indexed by their name.
    flippable = _data["flippable"]
    collision_sets = _data["collision_sets"]

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
    simple_entities_with_owner = _data["simple_entities_with_owner"]
    simple_entities_with_force = _data["simple_entities_with_force"]
    electric_energy_interfaces = _data["electric_energy_interfaces"]
    linked_containers = _data["linked_containers"]
    heat_interfaces = _data["heat_interfaces"]
    linked_belts = _data["linked_belts"]
    infinity_containers = _data["infinity_containers"]
    infinity_pipes = _data["infinity_pipes"]
    burner_generators = _data["burner_generators"]
    player_ports = _data["player_ports"]


def add_entity(
    name, entity_type, collision_box, collision_mask=None, hidden=False, **kwargs
):
    # type: (str, str, PrimitiveAABB, set[str], bool, **dict) -> None
    """
    Temporarily adds an entity to :py:mod:`draftsman.data.entities`.

    This is useful if you want to temporarily add an entity to the load process
    to quickly simulate a mod being present when it currently isn't. For example,
    you might want to be able to load a blueprint with modded entities in order
    to replace them with regular ones, but want the benefit of error checking
    without having to install the associated mods.

    :param name: The Factorio ID of the entity to add.
    :param entity_type: The string type of the entity.
    :param collision_box: The AABB of the entity, to check for collisions.
    :param collision_mask: The collision layers that this entity uses, to check
        for collisions.
    :param kwargs: Any other entity specific data that you want to populate the
        new entity with.
    """
    # TODO: assert that `entity_type` is a valid entity_type
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

    if entity_type == "container":
        containers.append(name)
    elif entity_type == "storage-tank":
        storage_tanks.append(name)
    elif entity_type == "constant-combinator":
        constant_combinators.append(name)
    elif entity_type == "lamp":
        lamps.append(name)
    elif entity_type == "decider-combinator":
        decider_combinators.append(name)
    elif entity_type == "train-stop":
        train_stops.append(name)
    else:
        raise NotImplementedError  # TODO
