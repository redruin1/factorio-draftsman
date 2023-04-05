# rail_planner_usage.py

"""
Illustation of the RailPlanner class, which is currently unimplemented.
"""

from draftsman.classes.blueprint import Blueprint
from draftsman.classes.rail_planner import RailPlanner
from draftsman.constants import Direction


def main():
    blueprint = Blueprint()

    rail_planner = RailPlanner("rail")

    for i in range(3):
        rail_planner.head_position = (0, 0)
        rail_planner.head_direction = (i * 2) + 1
        rail_planner.move_forward(10)

    # rail_planner.head_position = (0, 0)   # implicit
    # rail_planner.direction = 0            # implicit
    # rail_planner.move_forward(10)
    # rail_planner.turn_left()
    # rail_planner.turn_right()
    # rail_planner.move_forward(10)

    # Add the RailPlanner to the blueprint, but don't copy it so we can modify
    # it outside of the blueprint
    blueprint.entities.append(rail_planner, copy=False)

    # rail_planner.turn_left(4)  # Pick up from where we left off
    # rail_planner.move_forward(20)

    # print(blueprint)
    print(blueprint.to_string())


if __name__ == "__main__":
    main()
