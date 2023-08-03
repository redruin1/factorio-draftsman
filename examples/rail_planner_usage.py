# rail_planner_usage.py

"""
Illustation of how to use the RailPlanner class. It is a child class of Group,
which means it inherits all the same entity and query semantics. In addition, it
provides a set of turtle-like commands not unlike the in-game rail building GUI.
"""

# TODO: improve performance

from draftsman.blueprintable import Blueprint, BlueprintBook
from draftsman.rail import RailPlanner, TrainConfiguration
from draftsman.entity import RailSignal
from draftsman.constants import Direction


def main():
    # Let's create a blueprint book to store each of our illustrations
    rail_blueprints = BlueprintBook()
    blueprint = Blueprint()
    blueprint.label = "Straight rails in all 8 directions"

    # Constructs a rail planner with it's "head" at (0, 0) and pointed north
    rail_planner = RailPlanner()

    # Create rails going in every direction from the origin
    for direction in Direction:
        # (Re)set the position and direction of the starting rail
        rail_planner.head_position = (0, 0)
        rail_planner.head_direction = direction
        # Place 10 rails in that direction
        rail_planner.move_forward(10)

    # Add to the blueprint (same mechanics as adding a Group object)
    blueprint.entities.append(rail_planner)
    # Add the blueprint to the blueprint book
    rail_blueprints.blueprints.append(blueprint)

    # Note some peculiarities about the diagonal rails. For one, they're half as
    # long as the straight rails, due to the `amount` value being based off the
    # manhattan distance instead of the euclidean.

    # Another thing to note is that the diagonals going in opposite directions
    # don't line up with each other. This is because diagonals going in any
    # particular direction can actually occupy one of 2 different spots on the
    # same 2x2 tile "cell". RailPlanner prefers the "left" side based on it's
    # head direction, but can be changed by changing the `diagonal_side`
    # attribute to `1`:

    blueprint = Blueprint()
    blueprint.label = "Diagonal peculiarities"
    rail_planner = RailPlanner()

    rail_planner.head_position = (0, 0)
    rail_planner.head_direction = Direction.NORTHEAST
    rail_planner.diagonal_side = 0
    rail_planner.move_forward(5)

    rail_planner.head_position = (0, 0)
    rail_planner.head_direction = Direction.NORTHEAST
    rail_planner.diagonal_side = 1
    rail_planner.move_forward(10)  # different lengths so we can distinguish

    blueprint.entities.append(rail_planner)
    rail_blueprints.blueprints.append(blueprint)

    # Fortunately, this alignment issue is only a problem when connecting to
    # existing rails. RailPlanner will ensure that rails are contiguous when
    # placing and handles rail alignment automatically. For example, the
    # following figure-8 will place 2 straight rails on diagonals, and then 1
    # extra rail to fix the curve alignment required by Factorio:

    blueprint = Blueprint()
    blueprint.label = "2 rails on cardinal, 3 on diagonals"
    rail_planner = RailPlanner()

    for _ in range(8):
        rail_planner.turn_left()  # also accepts an `amount` argument
        rail_planner.move_forward(2)
    for _ in range(8):
        rail_planner.turn_right()  # also accepts an `amount` argument
        rail_planner.move_forward(2)

    blueprint.entities.append(rail_planner)
    rail_blueprints.blueprints.append(blueprint)

    # Rail signals of both types can also be placed alongside rails with the
    # `add_signal()` function. The first parameter is the string name of the
    # signal you want to place, and the `front` and `right_side` parameters
    # control where the signal ends up on the last placed rail.

    blueprint = Blueprint()
    blueprint.label = "All possible signal permutations"
    rail_planner = RailPlanner()

    # Create 4 separate circles. All regular signals are placed on the right
    # and chain signals on the left.
    for side in range(2):
        # Right turning circle on the right
        rail_planner.head_position = (2, side * 28)
        for _ in range(8):
            rail_planner.turn_right()
            rail_planner.add_signal("rail-signal", front=side)
            rail_planner.add_signal("rail-chain-signal", front=side, right_side=False)
            rail_planner.move_forward()
            rail_planner.add_signal("rail-signal", front=side)
            rail_planner.add_signal("rail-chain-signal", front=side, right_side=False)

        # Left turning circle on the left
        rail_planner.head_position = (-2, side * 28)
        for _ in range(8):
            rail_planner.turn_left()
            rail_planner.add_signal("rail-signal", front=side)
            rail_planner.add_signal("rail-chain-signal", front=side, right_side=False)
            rail_planner.move_forward()
            rail_planner.add_signal("rail-signal", front=side)
            rail_planner.add_signal("rail-chain-signal", front=side, right_side=False)

    # Note that diagonals continue to be strange in that they only have 2 valid
    # rail signal spots, so the `front` argument has no effect on them. Also
    # note that RailPlanner (currently) doesn't warn if rail signals are placed
    # too close together (like in this one), so that behavior has to be caught
    # manually by the user.

    blueprint.entities.append(rail_planner)
    rail_blueprints.blueprints.append(blueprint)

    # `add_signal()` also supports the ability to use an EntityLike prototype
    # instead of a string, so you can set any custom circuit conditions in a
    # "template" entity and just create a copy in the RailPlanner object:

    blueprint = Blueprint()
    blueprint.label = "Entity Template"
    rail_planner = RailPlanner()

    template = RailSignal("rail-signal", id="special_signal")
    template.set_circuit_condition("signal-A", ">", "signal-B")
    template.enable_disable = True

    rail_planner.head_direction = Direction.EAST
    rail_planner.move_forward()
    rail_planner.add_signal(template)

    # Technically, RailPlanners are just Groups with extra features, so let's
    # connect the signal to a pole and wire
    rail_planner.entities.append(
        "medium-electric-pole", tile_position=(1, 6), id="pole"
    )
    rail_planner.add_circuit_connection("red", "pole", "special_signal")

    blueprint.entities.append(rail_planner)
    rail_blueprints.blueprints.append(blueprint)

    # Adding stations to a RailPlanner is very similar, except that stations
    # have no `front` argument and cannot be placed on diagonal or curved rails:

    blueprint = Blueprint()
    blueprint.label = "Numbered Stations"
    rail_planner = RailPlanner()

    for i in range(4):
        rail_planner.head_position = (i * 4, 0)
        rail_planner.head_direction = i * 2  # only cardinal directions
        rail_planner.move_forward()  # only straight rails
        rail_planner.add_station(
            "train-stop", station="Right " + str(i), right_side=True
        )
        rail_planner.add_station(
            "train-stop", station="Left " + str(i), right_side=False
        )

    blueprint.entities.append(rail_planner)
    rail_blueprints.blueprints.append(blueprint)

    # `add_station()` also supports the same EntityLike templating that
    # `add_signal()` does.

    # And of course, perhaps most importantly you can also use the inherited
    # functions from EntityCollection to create trains:

    blueprint = Blueprint()
    blueprint.label = "Train creation!"
    rail_planner = RailPlanner()

    rail_planner.head_direction = Direction.EAST
    rail_planner.move_forward(18)
    rail_planner.add_station("train-stop")

    train_config = TrainConfiguration("1-4")
    rail_planner.add_train_at_station(train_config, rail_planner.entities[-1])

    blueprint.entities.append(rail_planner)
    rail_blueprints.blueprints.append(blueprint)

    # See `train_configuration_usage.py` for more information on train
    # configurations and `train_schedule_usage.py` for more information on
    # train schedules.

    return rail_blueprints.to_string()


if __name__ == "__main__":
    print(main())
