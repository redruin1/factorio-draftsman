# rail_planner_usage.py

"""
Illustation of the RailPlanner class, which is currently unimplemented.
"""

from draftsman.classes.blueprint import Blueprint
from draftsman.classes.railplanner import RailPlanner


def main():
    blueprint = Blueprint()

    rail_planner = RailPlanner("rail")

    # rail_planner.position = (0, 0) # implicit
    rail_planner.move_forward(1)  # tile
    rail_planner.turn_left()
    rail_planner.turn_right()
    rail_planner.move_forward(10)

    blueprint.entities.append(rail_planner)

    # Get the rail-planner stored in the blueprint
    # This is just to show that the RailPlanner can be modified even when inside
    # a blueprint
    rail_planner = blueprint.entities[0]

    rail_planner.turn_left(4)  # Pick up from where we left off
    rail_planner.move_forward(20)

    # print(blueprint)
    print(blueprint.to_string())


if __name__ == "__main__":
    main()
