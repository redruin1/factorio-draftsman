# train_schedule_usage.py

"""
Illustrates how to use WaitCondition, WaitConditions, Schedule, and how to 
assign that schedule to a train, new or otherwise.
"""

from draftsman.blueprintable import Blueprint
from draftsman.constants import (
    Direction,
    Ticks,
    WaitConditionType,
    WaitConditionCompareType,
)
from draftsman.signatures import AttrsSimpleCondition
from draftsman.rail import Schedule, WaitConditions, WaitCondition


def main() -> None:
    # Let's import a normal 2-4 train from a blueprint string:
    blueprint = Blueprint.from_string(
        "0eNqtk91qhDAQRt9lrrPLGn8S8yqllKwNEogTidFWJO/e0b1ZiqAX3mWGb84JYbLA042mDxYjqAVs43EA9bHAYFvUbu3FuTegwEbTAQPU3Vo53/jORzsZSAwsfptfUFlih4ONDq2//ejW49skT58MDEYbrXn5t2L+wrF7mkDoXQCD3g80Q0fyEefGa3mvpCgZzKByKUjhgyWYfqUed16u1olaPlAGR+fWa//z8dO+7BJfftYni0t8xVmfEJf4yr3N2dM9DnU79OokvcqP6bSI28aqt5/BYDJh2DJcZoWo6VlyUZeySOkPzX4Oog=="
    )

    # Create a `Schedule` object
    schedule = Schedule()

    # Schedules have parameters in their constructors for you can supply their
    # locomotives and stops, but it's usually much more convenient to use the
    # utility functions like `append_stop()`:
    schedule.append_stop(
        name="Iron Ore Pickup",
        wait_conditions=WaitCondition(WaitConditionType.FULL_CARGO),
    )
    # Here we created a pickup stop with a single `WaitCondition` object, which
    # translates to 1 condition, the train waiting for full cargo.

    # Trains frequently have more than one condition associated with them though,
    # so let's create a `WaitConditions` object which has multiple criteria:
    dropoff_conditions = WaitConditions(
        [
            WaitCondition(
                WaitConditionType.EMPTY_CARGO,
            ),
            WaitCondition(
                WaitConditionType.INACTIVITY,
                compare_type=WaitConditionCompareType.AND,
                ticks=10 * Ticks.SECOND,
            ),
        ]
    )
    # Using the Enums is rather verbose, so if you want to be more terse you can
    # use the equivalent strings:
    dropoff_conditions = WaitConditions(
        [
            WaitCondition("empty"),
            WaitCondition("inactivity", compare_type="and", ticks=600),
        ]
    )

    # However, there's an even better way than these two. Both `WaitCondition`
    # and `WaitConditions` implement the bitwise AND and OR operators (`&` and
    # `|`) which work exactly as you expect:
    dropoff_conditions = WaitCondition("empty") & WaitCondition("inactivity", ticks=600)

    # The result of this operation is automatically converted to a plural
    # `WaitConditions` object with their compare types properly set, requiring
    # no further transformation:
    assert isinstance(dropoff_conditions, WaitConditions)
    assert dropoff_conditions[1].compare_type == "and"

    # `append_stop` handles both singular `WaitCondition` and `WaitConditions`
    # objects seamlessly:
    schedule.append_stop("Iron Ore Dropoff", dropoff_conditions)

    # Of course, we can also add more conditions once a `WaitConditions` object
    # is made:
    signal_condition = WaitCondition(
        WaitConditionType.CIRCUIT_CONDITION,
        condition=AttrsSimpleCondition(
            first_signal="signal-check", comparator=">", constant=0
        ),
    )
    dropoff_conditions_extra = dropoff_conditions | signal_condition

    # New stop with "all cargo empty AND inactive for 10s OR signal-check > 0":
    schedule.append_stop("Trash Dropoff", dropoff_conditions_extra)

    # Let's also insert a fuel stop inbetween the pickup and dropoff:
    # (if 'ticks' is omitted, it will default to the familar 5 seconds seen in
    # Factorio)
    schedule.insert_stop(1, "Refuel", WaitCondition("inactivity"))

    # And the trash stop doesn't make much sense, so let's remove it:
    schedule.remove_stop("Trash Dropoff")

    # Then we can add the schedule to the blueprint
    blueprint.schedules.append(schedule)
    assert len(blueprint.schedules) == 1

    # Now we need to indicate which train(s) should have that schedule. There
    # are two main ways to do this:

    # We could grab one or more of the locomotive entities and add them to the
    # schedule (since we know that both belong to the same train).
    locomotives = blueprint.find_entities_filtered(type="locomotive")
    blueprint.set_train_schedule(locomotives, schedule)

    # This mnemonic is also good if we wanted to say give all trains in a
    # blueprint the same schedule.
    # But, we also might want more fine grained control of which trains we
    # assign the schedule. So we can instead use `find_trains_filtered()` to
    # select trains of particular compositions, type, orientation, or even by
    # their current schedule:
    trains = blueprint.find_trains_filtered()
    assert len(trains) == 1  # Should only be 1 train
    train = trains[0]

    # Schedules can be assigned by passing a single locomotive, which will grab
    # all Locomotives in that train and assign them to that schedule...
    blueprint.set_train_schedule(train[0], schedule)

    # Or as a list of all wagons of a particular train, like the train variable
    # we just found; it will automatically search the list for just the
    # locomotives and add them under that particular schedule
    blueprint.set_train_schedule(train, schedule)

    # Let's also create a new, equivalent train just below it with the same
    # schedule:
    blueprint.add_train_at_position(
        "2-4",  # Gets auto-converted to a TrainConfiguration
        position=train[0].position + (0, 4),
        direction=Direction.EAST,
        schedule=schedule,
    )

    print(blueprint.to_string())


if __name__ == "__main__":
    main()
