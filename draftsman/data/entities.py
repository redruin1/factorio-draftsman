# entities.py

import pickle

import importlib.resources as pkg_resources

from draftsman import data
from draftsman.classes.collision_set import CollisionSet
from draftsman.utils import PrimitiveAABB, AABB

from typing import Optional


try:
    with pkg_resources.open_binary(data, "entities.pkl") as inp:
        _data: dict = pickle.load(inp)

        # Aggregation of all the the entity dicts from data.raw collected in one
        # place.
        raw: dict[str, dict] = _data["raw"]

        # A dictionary of entitiy names sorted by a particular prototype name,
        # such as "container" or "assembling-machine".
        of_type: dict[str, list[str]] = _data["of_type"]

        # Whether or not each entity is flippable, indexed by their name.
        flippable: dict[str, bool] = _data["flippable"]

        # Indexes of unique collision sets for each entity. Shared between all
        # entity instances, so we save memory by not including it in each Entity
        # instance.
        collision_sets: dict[str, CollisionSet] = _data["collision_sets"]

        # Lists of strings, each containing a valid name for that entity type,
        # sorted by their Factorio order strings.
        accumulators: list[str] = of_type["accumulator"]
        agricultural_towers: list[str] = of_type["agricultural-tower"]
        ammo_turrets: list[str] = of_type["ammo-turret"]
        arithmetic_combinators: list[str] = of_type["arithmetic-combinator"]
        artillery_turrets: list[str] = of_type["artillery-turret"]
        artillery_wagons: list[str] = of_type["artillery-wagon"]
        assembling_machines: list[str] = of_type["assembling-machine"]
        asteroid_collectors: list[str] = of_type["asteroid-collector"]
        beacons: list[str] = of_type["beacon"]
        boilers: list[str] = of_type["boiler"]
        burner_generators: list[str] = of_type["burner-generator"]
        cars: list[str] = of_type["car"]
        cargo_bays: list[str] = of_type["cargo-bay"]
        cargo_landing_pads: list[str] = of_type["cargo-landing-pad"]
        cargo_wagons: list[str] = of_type["cargo-wagon"]
        constant_combinators: list[str] = of_type["constant-combinator"]
        containers: list[str] = of_type["container"]
        curved_rails_a: list[str] = of_type["curved-rail-a"]
        curved_rails_b: list[str] = of_type["curved-rail-b"]
        decider_combinators: list[str] = of_type["decider-combinator"]
        display_panels: list[str] = of_type["display-panel"]
        electric_energy_interfaces: list[str] = of_type["electric-energy-interface"]
        electric_poles: list[str] = of_type["electric-pole"]
        electric_turrets: list[str] = of_type["electric-turret"]
        elevated_curved_rails_a: list[str] = of_type["elevated-curved-rail-a"]
        elevated_curved_rails_b: list[str] = of_type["elevated-curved-rail-b"]
        elevated_half_diagonal_rails: list[str] = of_type["elevated-half-diagonal-rail"]
        elevated_straight_rails: list[str] = of_type["elevated-straight-rail"]
        fluid_turrets: list[str] = of_type["fluid-turret"]
        fluid_wagons: list[str] = of_type["fluid-wagon"]
        furnaces: list[str] = of_type["furnace"]
        fusion_generators: list[str] = of_type["fusion-generator"]
        fusion_reactors: list[str] = of_type["fusion-reactor"]
        gates: list[str] = of_type["gate"]
        generators: list[str] = of_type["generator"]
        half_diagonal_rails: list[str] = of_type["half-diagonal-rail"]
        heat_interfaces: list[str] = of_type["heat-interface"]
        heat_pipes: list[str] = of_type["heat-pipe"]
        infinity_containers: list[str] = of_type["infinity-container"]
        infinity_pipes: list[str] = of_type["infinity-pipe"]
        inserters: list[str] = of_type["inserter"]
        labs: list[str] = of_type["lab"]
        lamps: list[str] = of_type["lamp"]
        land_mines: list[str] = of_type["land-mine"]
        legacy_straight_rails: list[str] = of_type["legacy-straight-rail"]
        legacy_curved_rails: list[str] = of_type["legacy-curved-rail"]
        lightning_attractors: list[str] = of_type["lightning-attractor"]
        linked_belts: list[str] = of_type["linked-belt"]
        linked_containers: list[str] = of_type["linked-container"]
        loaders: list[str] = of_type["loader"]
        loaders_1x1: list[str] = of_type["loader-1x1"]
        locomotives: list[str] = of_type["locomotive"]
        # logistic_containers: list[str] = of_type["logistic-container"]
        logistic_passive_containers: list[str] = of_type["logistic-container-passive"]
        logistic_active_containers: list[str] = of_type["logistic-container-active"]
        logistic_storage_containers: list[str] = of_type["logistic-container-storage"]
        logistic_buffer_containers: list[str] = of_type["logistic-container-buffer"]
        logistic_request_containers: list[str] = of_type["logistic-container-request"]
        markets: list[str] = of_type["market"]
        mining_drills: list[str] = of_type["mining-drill"]
        offshore_pumps: list[str] = of_type["offshore-pump"]
        pipes: list[str] = of_type["pipe"]
        player_ports: list[str] = of_type["player-port"]
        power_switches: list[str] = of_type["power-switch"]
        programmable_speakers: list[str] = of_type["programmable-speaker"]
        pumps: list[str] = of_type["pump"]
        radars: list[str] = of_type["radar"]
        rail_chain_signals: list[str] = of_type["rail-chain-signal"]
        rail_ramps: list[str] = of_type["rail-ramp"]
        rail_signals: list[str] = of_type["rail-signal"]
        rail_supports: list[str] = of_type["rail-support"]
        reactors: list[str] = of_type["reactor"]
        roboports: list[str] = of_type["roboport"]
        rocket_silos: list[str] = of_type["rocket-silo"]
        selector_combinators: list[str] = of_type["selector-combinator"]
        simple_entities_with_force: list[str] = of_type["simple-entity-with-force"]
        simple_entities_with_owner: list[str] = of_type["simple-entity-with-owner"]
        solar_panels: list[str] = of_type["solar-panel"]
        space_platform_hubs: list[str] = of_type["space-platform-hub"]
        spider_vehicles: list[str] = of_type["spider-vehicle"]
        splitters: list[str] = of_type["splitter"]
        storage_tanks: list[str] = of_type["storage-tank"]
        straight_rails: list[str] = of_type["straight-rail"]
        thrusters: list[str] = of_type["thruster"]
        train_stops: list[str] = of_type["train-stop"]
        transport_belts: list[str] = of_type["transport-belt"]
        turrets: list[str] = of_type["turret"]
        underground_belts: list[str] = of_type["underground-belt"]
        underground_pipes: list[str] = of_type["pipe-to-ground"]
        walls: list[str] = of_type["wall"]


except FileNotFoundError:  # pragma: no coverage
    raw: dict[str, dict] = {}
    of_type: dict[str, list[dict]] = {}
    flippable: dict[str, bool] = {}
    collision_sets: dict[str, CollisionSet] = {}


ALL_EFFECTS = {"speed", "productivity", "consumption", "pollution", "quality"}
ALL_EFFECTS_EXCEPT_QUALITY = {
    "speed",
    "productivity",
    "consumption",
    "pollution",
    "quality",
}
NO_EFFECTS = set()


def get_allowed_effects(entity_name: str, default: set[str]) -> Optional[set[str]]:
    """
    Returns a set of all the effects that this entity can support, either coming
    from modules or beacons. Returns ``default`` if this entity is recognized
    under the current environment, but has no defined key. Returns ``None`` if
    the entity is unrecognized by the current environment.
    """
    # If name not known, return None
    entity = raw.get(entity_name, None)
    if entity is None:
        return None
    # If name known, but no key, then return default list
    result = entity.get("allowed_effects", default)
    # Normalize single string effect to a 1-length set
    return {result} if isinstance(result, str) else set(result)


def add_entity(
    name: str,
    type: str,
    collision_box: PrimitiveAABB,
    collision_mask: set[str] = None,
    hidden: bool = False,
    target: tuple[dict[str, dict], dict[str, list]] = (raw, of_type),
    **kwargs
):
    """
    Adds an entity to :py:mod:`draftsman.data.entities`.

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
    # entity_map = {
    #     "container": containers,
    #     "storage-tank": storage_tanks,
    #     "transport-belt": transport_belts,
    #     "underground-belt": underground_belts,
    #     "splitter": splitters,
    #     "inserter": inserters,
    #     "filter-inserter": filter_inserters,
    #     "loader": loaders,
    #     "electric-pole": electric_poles,
    #     "pipe": pipes,
    #     "pipe-to-ground": underground_pipes,
    #     "pump": pumps,
    #     "straight-rail": straight_rails,
    #     "curved-rail": curved_rails,
    #     "train-stop": train_stops,
    #     "rail-signal": rail_signals,
    #     "rail-chain-signal": rail_chain_signals,
    #     "locomotive": locomotives,
    #     "cargo-wagon": cargo_wagons,
    #     "fluid-wagon": fluid_wagons,
    #     "artillery-wagon": artillery_wagons,
    #     "logistic-container": logistic_passive_containers,  # FIXME
    #     "roboport": roboports,
    #     "lamp": lamps,
    #     "arithmetic-combinator": arithmetic_combinators,
    #     "decider-combinator": decider_combinators,
    #     "constant-combinator": constant_combinators,
    #     "power-switch": power_switches,
    #     "programmable-speaker": programmable_speakers,
    #     "boiler": boilers,
    #     "generator": generators,
    #     "solar-panel": solar_panels,
    #     "accumulator": accumulators,
    #     "reactor": reactors,
    #     "heat-pipe": heat_pipes,
    #     "mining-drill": mining_drills,
    #     "offshore-pump": offshore_pumps,
    #     "furnace": furnaces,
    #     "assembling-machine": assembling_machines,
    #     "lab": labs,
    #     "beacon": beacons,
    #     "rocket-silo": rocket_silos,
    #     "land-mine": land_mines,
    #     "wall": walls,
    #     "gate": gates,
    #     "turret": turrets,  # FIXME
    #     "radar": radars,
    #     "electric-energy-interface": electric_energy_interfaces,
    #     "linked-container": linked_containers,
    #     "heat-interface": heat_interfaces,
    #     "linked-belt": linked_belts,
    #     "infinity-container": infinity_containers,
    #     "infinity-pipe": infinity_pipes,
    #     "burner-generator": burner_generators,
    # }

    # if entity_type not in entity_map:
    #     raise ValueError("Unrecognized 'entity_type' '{}'".format(entity_type))

    raw, of_type = target

    raw[name] = {
        "name": name,
        "type": type,
        "collision_box": collision_box,
        "flags": set(),
    }

    if collision_mask is not None:
        raw[name]["collision_mask"] = collision_mask
        raw[name]["collision_mask"]["layers"] = set(collision_mask["layers"])
    # else:
    #     raw[name]["collision_mask"] = get_default_collision_mask(type)

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

    if type in of_type:
        of_type[type].append(name)  # FIXME
    else:  # pragma: no coverage
        of_type[type] = [name]
