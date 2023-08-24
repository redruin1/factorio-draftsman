# extras.py

from draftsman.classes.blueprint import Blueprint
from draftsman.constants import Direction


def reverse_belts(blueprint):
    # type: (Blueprint) -> None
    """
    Modifies the passed in blueprintable in place to swap the direction of all
    belts.
    """
    if blueprint.item not in {"blueprint"}:
        return

    # If a transport belt is pointed to by one other belt going in a different
    # direction, then that's a curved belt that has special behavior
    # Otherwise, the simple case is to just make the direction the opposite

    # We keep track of all belt entities (indexed by their position in
    # blueprint.entities) direction and which belt objects point to them
    direction_map = {}
    # The positional offset to check against when seeing if a belt points to
    # another
    belt_types = {"transport-belt", "underground-belt", "splitter"}
    for i, entity in enumerate(blueprint.entities):
        # If it's a belt and not in the direction map, add it
        if entity.type in belt_types and i not in direction_map:
            direction_map[i] = {"direction": entity.direction, "pointed_by": []}

        if entity.type == "transport-belt":
            pointed = blueprint.find_entity_at_position(
                entity.position + entity.direction.to_vector()
            )
            if pointed and pointed.type in belt_types:
                # Update the pointed entity
                j = blueprint.entities.index(pointed)
                if j not in direction_map:
                    direction_map[j] = {
                        "direction": pointed.direction,
                        "pointed_by": [],
                    }
                direction_map[j]["pointed_by"].append(i)
        elif entity.type == "underground-belt":
            # Underground belt outputs affect curves
            if entity.io_type == "output":
                pointed = blueprint.find_entity_at_position(
                    entity.position + entity.direction.to_vector()
                )
                if pointed:
                    # Update the pointed entity
                    j = blueprint.entities.index(pointed)
                    if j not in direction_map:
                        direction_map[j] = {
                            "direction": pointed.direction,
                            "pointed_by": [],
                        }
                    direction_map[j]["pointed_by"].append(i)
        elif entity.type == "splitter":
            # Use the splitter's bounding box (offset by direction_delta) to get the
            # belts that it may be pointing at
            bbox = entity.get_world_collision_set().shapes[0]  # FIXME: this sucks
            bbox.position += entity.direction.to_vector()  # FIXME: this sucks
            bbox = bbox.get_bounding_box()  # FIXME: this sucks
            pointed_list = blueprint.find_entities_filtered(area=bbox, type=belt_types)
            for pointed in pointed_list:
                # Update the pointed entity
                j = blueprint.entities.index(pointed)
                if j not in direction_map:
                    direction_map[j] = {
                        "direction": pointed.direction,
                        "pointed_by": [],
                    }
                direction_map[j]["pointed_by"].append(i)

    # Then we iterate over once more and fix their directions, taking into
    # account
    for i, entity in enumerate(blueprint.entities):
        if entity.type == "transport-belt":
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
            entity.direction = entity.direction.opposite()
            if entity.io_type == "input":
                entity.io_type = "output"
            elif entity.io_type == "output":
                entity.io_type = "input"
        elif entity.type == "splitter":
            entity.direction = entity.direction.opposite()