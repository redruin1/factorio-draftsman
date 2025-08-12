# extras.py

from draftsman.classes.collection import Collection
from draftsman.classes.entity_like import EntityLike
from draftsman.entity import TransportBelt, UndergroundBelt, Splitter

from typing import cast as typing_cast


def reverse_belts(collection: Collection) -> None:
    """
    Modifies the passed in blueprint or group in-place to swap the direction of
    all belts. Instead of just inverting the direction of each belt, this
    function properly inverts corners which have specific semantics.
    """
    # If a transport belt is pointed to by one other belt going in a different
    # direction, then that's a curved belt that has special behavior
    # Otherwise, the simple case is to just make the direction the opposite

    # We keep track of all belt entities (indexed by their position in
    # blueprint.entities) direction and which belt objects point to them
    direction_map = {}
    # The positional offset to check against when seeing if a belt points to
    # another
    belt_types = {"transport-belt", "underground-belt", "splitter"}
    for i, entity in enumerate(collection.entities):
        # If not a belt, ignore it
        if entity.type not in belt_types:
            continue

        entity = typing_cast(TransportBelt | UndergroundBelt | Splitter, entity)

        # If it's not in the direction map, add it
        if entity.type in belt_types and i not in direction_map:
            direction_map[i] = {"direction": entity.direction, "pointed_by": []}

        if entity.type == "transport-belt":
            entity: TransportBelt
            pointed = collection.find_entity_at_position(
                entity.position + entity.direction.to_vector()
            )
            if pointed and pointed.type in belt_types:
                # Update the pointed entity
                j = collection.entities.index(pointed)
                if j not in direction_map:
                    direction_map[j] = {
                        "direction": pointed.direction,
                        "pointed_by": [],
                    }
                direction_map[j]["pointed_by"].append(i)
        elif entity.type == "underground-belt":
            entity: UndergroundBelt
            # Underground belt outputs affect curves
            if entity.io_type == "output":
                pointed = collection.find_entity_at_position(
                    entity.position + entity.direction.to_vector()
                )
                if pointed:
                    # Update the pointed entity
                    j = collection.entities.index(pointed)
                    if j not in direction_map:
                        direction_map[j] = {
                            "direction": pointed.direction,
                            "pointed_by": [],
                        }
                    direction_map[j]["pointed_by"].append(i)
        elif entity.type == "splitter":
            entity: Splitter
            # Use the splitter's bounding box (offset by direction_delta) to get the
            # belts that it may be pointing at
            bbox = entity.get_world_collision_set().shapes[0]  # FIXME: this sucks
            bbox.position += entity.direction.to_vector()  # FIXME: this sucks
            bbox = bbox.get_bounding_box()  # FIXME: this sucks
            pointed_list = collection.find_entities_filtered(area=bbox, type=belt_types)
            for pointed in pointed_list:
                # Update the pointed entity
                j = collection.entities.index(pointed)
                if j not in direction_map:
                    direction_map[j] = {
                        "direction": pointed.direction,
                        "pointed_by": [],
                    }
                direction_map[j]["pointed_by"].append(i)

    # Then we iterate over once more and fix their directions, taking into
    # account
    for i, entity in enumerate(collection.entities):
        entity: EntityLike
        if entity.type == "transport-belt":
            entity: TransportBelt
            only_one_pointer = len(direction_map[i]["pointed_by"]) == 1
            # Try and get the single entity that points to the current one and
            # get it's direction
            try:
                single_belt_idx = direction_map[i]["pointed_by"][0]
                pointer_direction = direction_map[single_belt_idx]["direction"]
                pointer_diff_dir = entity.direction != pointer_direction
            except (IndexError, KeyError):
                pointer_diff_dir = False
            # Flip
            if only_one_pointer and pointer_diff_dir:
                entity.direction = pointer_direction.opposite()
            else:
                entity.direction = entity.direction.opposite()
        elif entity.type == "underground-belt":
            entity: UndergroundBelt
            entity.direction = entity.direction.opposite()
            if entity.io_type == "input":
                entity.io_type = "output"
            elif entity.io_type == "output":
                entity.io_type = "input"
        elif entity.type == "splitter":
            entity: Splitter
            entity.direction = entity.direction.opposite()
