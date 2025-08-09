# train_configuration_usage.py

from draftsman.blueprintable import Blueprint
from draftsman.classes.train_configuration import TrainConfiguration
from draftsman.constants import Direction, InventoryType
from draftsman.data import mods, entities


def main():
    blueprint = Blueprint()

    # In order to specify a specific train format, we construct a helper object
    # called `TrainConfiguration`
    # The notable thing about TrainConfiguration is that you can specify your
    # overall train format in a variant of the common community-accepted syntax:

    # 1 Locomotive followed by 4 cargo wagons
    config = TrainConfiguration("1-4")

    # Same as above
    config = TrainConfiguration("1-4-0")

    # 1 Locomotive pointing forward, 4 cargo wagons, and 1 loco pointing backwards
    config = TrainConfiguration("1-4-1")

    # Same as above, but explicit loco direction
    config = TrainConfiguration("1<-4-1>")

    # Same as above, but both locomotives are pointing forward
    config = TrainConfiguration("1<-4-1<")

    # Same as above, but cargo wagons are explicitly specified
    config = TrainConfiguration("1<-4C-1<")

    # Same as above, but each cargo wagon is instead a fluid wagon
    config = TrainConfiguration("1<-4F-1<")

    # Same as above, converts all non-locomotive cars to cars of that type
    config = TrainConfiguration("1<-4-<1", wagons="fluid")

    # Specify that all locomotive should point forward regardless of order
    config = TrainConfiguration("1-4-1", direction="forward")

    # In this case all locomotives point "forward" when there's more than 2 locomotive cells
    # More specifically, "dual" direction is only used when there's only 2 locomotive blocks and they exist at the start and end
    config = TrainConfiguration("1-4-1-4-1")

    # Unless, of course, you manually specify their directions
    config = TrainConfiguration("<-4-<-4->")

    # Configurations can also be entirely explicit, no hyphens necessary
    config = TrainConfiguration("<<<FFFCCCAAA<<<")

    # Or you can add hyphens just for clarity
    config = TrainConfiguration("<<<-FFFCCCAAA-<<<")
    # C is for cargo wagons, F is for fluid wagons, A for artillery, and can be
    # specified in either upper or lowercase

    # With the syntax explained, let's create a final configuration: a dual-
    # headed train with one of each wagon type
    config = TrainConfiguration("1-CFA-1")

    # `config` contains a list of rolling stock under the attribute `cars`:
    assert len(config.cars) == 5

    # The benefit of this is that you can customize any properties about the
    # config even further before adding it to a blueprint. For example:
    # Fuel the first locomotive
    config.cars[0].set_item_request("nuclear-fuel", 3)
    # Set cargo filters
    config.cars[1].inventory_filters = ["iron-ore", "copper-ore", "stone", "coal"]
    # Set the modding tags for them
    config.cars[2].tags = {"some": "stuff"}
    # Even preload the artillery wagons on construction
    config.cars[3].set_item_request(
        "artillery-shell", 25, inventory=InventoryType.ARTILLERY_WAGON_AMMO
    )

    # Cars are specified from the left of the right, so the 0th
    # car is the leftmost character in the string.
    # Modifying position or orientation are redundant in this case, as they're
    # overwritten when they're added to a blueprint.

    # We can add a station at a particular position and direction, which is the
    # simplest method of adding it to a blueprint:
    if False:
        blueprint.add_train_at_position(
            (3, 0), Direction.WEST, config=config, schedule=None
        )

    # For more information on the `schedule` parameter, see `train_schedule_usage.py`

    # Specifying by position is acceptable for some blueprints, but 90 percent
    # of the time users want to put their blueprints behind stations.
    # Let's create a station (with some rails) and place the train there instead:

    # Configs have a `rail_length` which is the number of straight-rails needed
    # on the ground in order to place the full train
    # You can multiply this value by 2 to get the length of the train in regular
    # units for rail-network calculations
    for i in range(config.rail_length):
        blueprint.entities.append(
            "straight-rail", tile_position=(i * 2, 4), direction=Direction.WEST
        )

    # Add station with name
    blueprint.entities.append(
        "train-stop",
        tile_position=(0, 2),
        direction=Direction.WEST,
        station="A",
        id="station_A",
    )

    # Note that we use the station's ID, not it's name. This is because there
    # can be multiple stations with the name "A", and how would we discern
    # between them?
    blueprint.add_train_at_station(config, "station_A")

    # Side note: for both `add_train_at_position` and `add_train_at_station`,
    # you can also just pass the train configuration string which will be auto-
    # converted to a full TrainConfiguration object:
    if False:
        blueprint.add_train_at_station("2-4", ...)
        blueprint.add_train_at_position("2-4-2", ...)
    # Doing this, you of course lose the added customization options at the
    # benefit of brevity.

    print(blueprint.to_string())

    # By default, train configurations only map to vanilla train cars. However,
    # this of course can be customized to instead point to modded rail entities
    # (or whatever you want I guess)
    # Let's check to see if the FactorioExtended mod is installed in draftsman,
    # and then upgrade our current train configuration to use the mk3 train
    # variants:
    if "FactorioExtended-Plus-Transport" in mods.versions:  # pragma: no coverage
        assert "locomotive-mk3" in entities.locomotives
        assert "cargo-wagon-mk3" in entities.cargo_wagons
        assert "fluid-wagon-mk3" in entities.fluid_wagons

        # A mapping dict is a correspondence between a string character and a
        # dict of keyword arguments to pass when constructing the next entity:
        modded_mapping = {
            "<": {"name": "locomotive-mk3"},  # Forward loco
            ">": {  # Reverse loco
                "name": "locomotive-mk3",
                "orientation": 0.5,  # 180 degrees offset from whatever is set
                # Could even make it perpendicular if you're bonkers
            },
            "C": {  # Note the capitalization
                "name": "cargo-wagon-mk3",
            },
            "F": {"name": "fluid-wagon-mk3"},
            "A": {"name": "artillery-wagon"},  # No boosted artillery wagon :(
            # There's also nothing stopping you from adding other symbols that
            # point to different wagons of any type. Any symbol should work
            # provided that they're:
            #   * 1 character long, and
            #   * they're the uppercase equivalent, since the string is
            #     normalized to uppercase
        }

        # Now we can re-use the same string from earlier to get an upgraded
        # result:
        config.from_string("1-CFA-1", mapping=modded_mapping)
        mod_blueprint = Blueprint()
        mod_blueprint.add_train_at_position((0, 0), Direction.WEST, config)

        print(mod_blueprint.to_string())

        # You can also change the default mapping in TrainConfiguration so that
        # this only has to be done once on setup:
        TrainConfiguration.default_mapping = modded_mapping

        # Then any subsequent calls to `TrainConfiguration("...")` or
        # `TrainConfiguration.from_string("...")` will use the modded mapping.


if __name__ == "__main__":  # pragma: no coverage
    main()
