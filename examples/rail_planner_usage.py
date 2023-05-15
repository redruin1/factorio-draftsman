# rail_planner_usage.py

"""
Illustation of the RailPlanner class, which is currently unimplemented.
"""

from draftsman.classes.blueprint import Blueprint
from draftsman.classes.rail_planner import RailPlanner
from draftsman.constants import Direction


def main():
    blueprint = Blueprint()

    rail_planner = RailPlanner()

    # for i in range(8):
    #     rail_planner.head_position = (0, 0)
    #     rail_planner.head_direction = i
    #     rail_planner.move_forward(10)

    # rail_planner.head_position = (0, 0)         # implicit
    # rail_planner.direction = Direction.NORTH    # implicit
    # # rail_planner.move_forward(10)
    # for i in range(8):
    #     rail_planner.turn_left(1)
    #     rail_planner.move_forward(2)
    # for i in range(8):
    #     rail_planner.turn_right(1)
    #     rail_planner.move_forward(2)
    # # rail_planner.turn_right()
    # # rail_planner.move_forward(10)
    # # rail_planner.turn_left(2)

    # rail_planner.head_position = (20, 20)
    # rail_planner.head_direction = Direction.EAST

    # # You can turn multiple times by specifing amount=number of times to turn
    # # both `turn_left` and `turn_right` properly handle straight rails in 90
    # # degree bends, so you don't have to worry about doing that yourself
    # rail_planner.turn_left()
    # rail_planner.turn_right(6)
    # rail_planner.turn_left()

    # for i in range(4):
    #     rail_planner.head_direction = i * 2
    #     rail_planner.head_position = (i * 10, 0)
    #     rail_planner.turn_left()
    #     rail_planner.add_signal()
    #     rail_planner.add_signal(right_side=False, entity="rail-chain-signal")
    #     rail_planner.add_signal(front=False)
    #     rail_planner.add_signal(right_side=False, front=False, entity="rail-chain-signal")
        

    # # FIXME vvvv
    # rail_planner.turn_right()
    # rail_planner.add_signal()
    # rail_planner.turn_right()
    # rail_planner.add_signal()

    for i in range(4):
        rail_planner.head_position = (i * 4, 0)
        rail_planner.head_direction = i * 2
        rail_planner.move_forward()
        rail_planner.add_station()

    # rail_planner.turn_left(4)  # Pick up from where we left off
    # rail_planner.move_forward(20)

    # Add the RailPlanner to the blueprint
    blueprint.entities.append(rail_planner)

    # print(blueprint)
    print(blueprint.to_string())


if __name__ == "__main__":
    main()
