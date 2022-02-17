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

from factoriotools import Blueprint, CargoWagon

def main():
    # Train contents we want to filter
    # item name: amount of wagon slots
    contents = {
        "stone": 40,
        "coal": 40,
        "iron-ore": 40,
        "copper-ore": 40,
        "uranium-ore": 40
    }

    blueprint = Blueprint()
    # Locomotive
    blueprint.add_entity("locomotive", position = [0, 0], orientation = 0.75)
    # Offset the position to account for the Locomotive
    train_car_position = 1

    # Create the cargo wagons
    cargo_wagon = CargoWagon("cargo-wagon", orientation = 0.75)
    slot_count = 1 # because inventory slot indexing starts at 1 instead of 0
    
    for item, slots in contents.items():
        # Set the filters
        for _ in range(slots):
            # Check to see if we've exceeded the current wagon's size
            if slot_count > 40:
                # Add a new wagon
                cargo_wagon.set_grid_position(7 * train_car_position, 0)
                blueprint.add_entity(cargo_wagon)
                # Reset
                cargo_wagon = CargoWagon("cargo-wagon", orientation = 0.75)
                slot_count = 1
                train_car_position += 1
            
            cargo_wagon.set_inventory_filter(slot_count, item)
            slot_count += 1
    
    # Add the last wagon if we didn't exceed the inventory
    cargo_wagon.set_grid_position(7 * train_car_position, 0)
    blueprint.add_entity(cargo_wagon)

    # Add a fancy title
    blueprint.set_label("1-{} Filtered Train".format(train_car_position))
    blueprint.set_label_color(1.0, 0.0, 0.0) # because why not

    print(blueprint.to_string())
    

if __name__ == "__main__":
    main()