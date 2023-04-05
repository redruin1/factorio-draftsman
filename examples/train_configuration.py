# train_schedules.py

from draftsman.blueprintable import Blueprint
from draftsman.classes.train_configuration import TrainConfiguration
from draftsman.constants import Direction
from draftsman.data import mods, entities


def main():
    # Import a rail oval with a train stop with name "A" and name "B"
    blueprint = Blueprint()

    # In order to specify a specific train format, we construct a helper object
    # called `TrainConfiguration`
    # The notable thing about TrainConfiguration is that you can specify your
    # overall train format in a variant of the community-accepted syntax:
    config = TrainConfiguration("1-4")  # 1 Locomotive followed by 4 cargo wagons
    config = TrainConfiguration("1-4-0")  # Same as above
    config = TrainConfiguration("1-4-1")  # 1 Locomotive pointing forward, 4 cargo wagons, and 1 loco pointing backwards
    config = TrainConfiguration("1<-4-1>")  # Same as above, but explicit
    config = TrainConfiguration("1<-4-<1")  # Two loco's on each end, both pointing forward between 4 cargo wagons
    config = TrainConfiguration("1<-4C-<1")  # Same as above, but explicitly cargo wagons are specified
    config = TrainConfiguration("1<-4F-<1")  # Same as above, but each cargo wagon is now a fluid wagon
    config = TrainConfiguration("1<-4-<1", wagons="fluid")  # Same as above, converts all non-locomotive cars to cars of that type
    config = TrainConfiguration("1-4-1", direction="forward")  # Specify that all locomotive should point forward regardless of order
    config = TrainConfiguration("1-4-1-4-1")  # In this case all locomotives point "forward" when there's more than 2 locomotive cells
    # More specifically, "dual" direction is only used when there's only 2 locomotive blocks and they exist at the start and end
    config = TrainConfiguration("<-4-<-4->")  # unless, of course, you manually specify
    config = TrainConfiguration("<<<FFFCCCAAA<<<")  # Configurations can also be entirely explicit, no hyphens necessary
    config = TrainConfiguration("<<<-FFFCCCAAA-<<<")  # Same as above; hyphens can be added for clarity
    # C is for cargo wagons, F is for fluid wagons, A for artillery

    # With the syntax explained, let's create an final configuration, one loco
    # with one of each cargo wagon
    config = TrainConfiguration("1-CFA-1")

    # `config` contains a list of rolling stock under the attribute `cars`:
    assert len(config.cars) == 5

    # The benefit of this is that you can customize any properties about the 
    # config before adding it to a blueprint. For example:
    config.cars[0].set_item_request("nuclear-fuel", 3)  # Fuel the locomotive
    config.cars[1].set_inventory_filters(["iron-ore", "copper-ore", "stone", "coal"])  # Set cargo filters
    config.cars[2].tags = {"some": "stuff"}  # Set the modding tags for them
    config.cars[3].set_item_request("artillery-shell", 25)  # Even preload the artillery wagons on construction
    
    # Modifying position or orientation are redundant in this case, as they're
    # overwritten when they're added to a blueprint:
    #blueprint.add_train((3, 0), Direction.WEST, config=config, schedule=None)
    # For more information on the `schedule` parameter, see `train_schedules.py`

    # Specifying by position is acceptable for some blueprints, but 90 percent
    # of the time users want to put their blueprints behind stations.
    # Let's create a station (with some rails) and place another identical train

    # Configs have a `rail_length` which is the number of straight-rails needed
    # on the ground in order to place the full train
    # You can multiply this value by 2 to get the length of the train in regular
    # units for rail-network calculations
    for i in range(config.rail_length):
        blueprint.entities.append(
            "straight-rail", 
            tile_position=(i*2, 4), 
            direction=Direction.WEST
        )
    
    # Add station with name
    blueprint.entities.append(
        "train-stop", 
        tile_position = (0, 2), 
        direction=Direction.WEST,
        station="A",
        id="station_A"
    )

    blueprint.add_train_at_station("station_A", config)

    # print(blueprint)
    print(blueprint.to_string())

    # By default, train configurations only map to vanilla train cars. However,
    # this of course can be customized to instead point to modded rail entities
    # (or whatever you want I guess)
    # Let's check to see if the FactorioExtended mod is installed in draftsman, 
    # and then upgrade our current train configuration to use the mk3 train 
    # variants:
    if "FactorioExtended-Plus-Transport" in mods.mod_list:
        assert "locomotive-mk3" in entities.locomotives
        assert "cargo-wagon-mk3" in entities.cargo_wagons
        assert "fluid-wagon-mk3" in entities.fluid_wagons

        # A mapping dict is a correspondence between a string character and a
        # dict of keyword arguments to pass when constructing the next entity:
        modded_mapping = {
            "<": { # Forward loco
                "name": "locomotive-mk3"
            },
            ">": { # Reverse loco
                "name": "locomotive-mk3",
                "orientation": 0.5 # 180 degrees offset from whatever is set
                                   # Could even make it perpendicular if you're bonkers
            },
            "C": { # Note the capitalization
                "name": "cargo-wagon-mk3",
            },
            "F": {
                "name": "fluid-wagon-mk3"
            },
            "A": {
                "name": "artillery-wagon" # No boosted artillery wagon :(
            }
            # There's also nothing stopping you from adding other symbols that
            # point to different wagons of any type. Any symbol should work
            # provided that they're:
            #   * 1 character long, and
            #   * they're the uppercase equivalent, as mentioned before
        }

        # Now we can re-use the same string from earlier to get an upgraded
        # result:
        config.from_string("1-CFA-1", mapping=modded_mapping)
        mod_blueprint = Blueprint()
        mod_blueprint.add_train((0, 0), Direction.WEST, config)

        # print(mod_blueprint)
        print(mod_blueprint.to_string())

        # You can also change the default mapping in TrainConfiguration so that
        # this only has to be done once on setup:
        TrainConfiguration.default_mapping = modded_mapping


if __name__ == "__main__":
    main()
