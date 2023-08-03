# filtered_train.py

"""
Creates a 1-N train that filters its cargo inventories based on a set of inputs.
Input is provided by dict `contents`, where each key is an item to filter and 
its value is a positive integer indicating the number of inventory slots to 
filter with that item.

Slots are filled sequentially starting in the top left and working across. If
the total number of slots cannot fit in the current cargo wagon(s), new wagons
are added as necessary in order to satisfy `contents`.

Can be used to dynamically create specifically designed supply trains for 
specific purposes, such as building, defense repair, ammo supply, and so on.
Care should be taken across train boundaries however as this script makes no 
attempt to organize the entries by train, and as a result item slots can be 
split across multiple trains which is probably undesirable for this purpose.
"""

from draftsman.blueprintable import Blueprint
from draftsman.entity import CargoWagon
from draftsman.constants import Orientation


def main():
    # Train contents we want to filter
    # item name: amount of wagon slots
    contents = {
        "stone": 10,
        "coal": 10,
        "iron-ore": 10,
        "copper-ore": 5,
        "uranium-ore": 5,
    }

    blueprint = Blueprint()
    # Locomotive
    blueprint.entities.append("locomotive", position=[0, 0], orientation=Orientation.WEST)
    # Offset the position to account for the Locomotive
    train_car_position = 1

    # Create the cargo wagons
    cargo_wagon = CargoWagon("cargo-wagon", orientation=Orientation.WEST)
    slot_count = 0  # because inventory slot indexing starts at 1 instead of 0

    for item, slots in contents.items():
        # Set the filters
        for _ in range(slots):
            # Check to see if we've exceeded the current wagon's size
            if slot_count >= 40:
                # Add a new wagon
                cargo_wagon.position = (7 * train_car_position, 0)
                blueprint.entities.append(cargo_wagon)
                # Reset
                cargo_wagon = CargoWagon("cargo-wagon", orientation=Orientation.WEST)
                slot_count = 0
                train_car_position += 1

            cargo_wagon.set_inventory_filter(slot_count, item)
            slot_count += 1

    # Add the last wagon if we didn't exceed the inventory
    cargo_wagon.position = (7 * train_car_position, 0)
    blueprint.entities.append(cargo_wagon)

    # Add a fancy title
    blueprint.label = "1-{} Filtered Train".format(train_car_position)
    blueprint.label_color = (1.0, 0.0, 0.0)  # because why not

    # print(blueprint)
    print(blueprint.to_string())


if __name__ == "__main__":  # pragma: no coverage
    main()
