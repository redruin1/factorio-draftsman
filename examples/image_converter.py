# image_converter.py

"""
Converts an image into a map-viewable blueprint. Uses partial Floyd-Steinberg
dithering to reduce banding. Much improvement could be made here:
    * Adding all possible colors, either statically or dynamically (dont think I 
        have all of them)
    * Add the dithering to all of the entities, not just the tiles
    * Improve the error metric tracking so that multi-tile entities error is 
        averaged across all tiles it covers, not just the top-left one
    * Handle different orientations of each entity and account for that in the 
        error metric
    * Handle rails: they offer a unique color, but they have a double-grid 
        placement restriction

Unfortunately, it doesn't seem like the `map_color`s for most entities are 
available, (possibly hardcoded?) which means that dynamically updating the 
palette with mods seems out of the question. :(

Let me know if I've missed them somewhere though.

Actually, I might have found it: 
https://github.com/wube/factorio-data/blob/master/core/prototypes/utility-constants.lua

Requirements:
    pillow
    numpy
    pyperclip (or you can just output the contents to a file)
"""

import math
from PIL import Image
import numpy as np
from draftsman.blueprint import Blueprint
from draftsman.entity import new_entity
from draftsman.data import entities
from draftsman.utils import aabb_to_dimensions
import pyperclip

def main():
    # Manually specify the color, whether its a tile or entity, and its name
    colors = [
        [(189, 203, 189), "entity", "stone-wall"],
        #[(140, 138, 140), "entity", "straight-rail"],
        #[(107, 105, 107), "entity", "accumulator"],
        [(99, 101, 99), "tile", "refined-concrete"],
        [(49, 48, 49), "tile", "stone-path"],
        #[(24, 32, 33), "entity", "solar-panel"],
        [(255, 211, 0), "entity", "splitter"],
        [(206, 166, 16), "entity", "gun-turret"],
        [(140, 117, 0), "entity", "underground-belt"],
        [(123, 125, 0), "tile", "refined-hazard-concrete-left"],
        [(206, 158, 66), "entity", "transport-belt"],
        [(239, 117, 24), "entity", "flamethrower-turret"],
        [(214, 44, 41), "entity", "laser-turret"],
        [(0, 93, 148), "entity", "small-lamp"]
    ]

    # Create a blueprint to hold everything
    blueprint = Blueprint()

    # Specify the size of the image
    # The example image is square, so we use one parameter for simplicity
    target_size = 200

    # open an image
    img = Image.open('examples/example.png')
    img = img.resize((target_size, target_size))

    img_data = np.array(img)[:,:,:3]

    # Keep track of occupied pixels
    occupied_pixels = np.empty(shape=(target_size, target_size))
    occupied_pixels.fill(False)

    def assert_entity_fits(color, x, y):
        if color[1] == "tile": return True # dont worry about tiles
        # Get the entity width and height
        # TODO: find a cleaner way to do this
        w, h = aabb_to_dimensions(entities.raw[color[2]]["collision_box"])
        # Check every pixel in the grid to see if there's room for this entity
        for j in range(y, y + h):
            for i in range(x, x + w):
                try:
                    if occupied_pixels[j][i]:
                        return False
                except IndexError:
                    pass
        return True

    def find_closest_color(target_color, x, y):
        r, g, b = target_color
        color_diffs = []
        available_colors = filter(lambda c: assert_entity_fits(c, x, y), colors)
        for color in available_colors:
            cr, cg, cb = color[0]
            color_diff = math.sqrt((r - cr)**2 + (g - cg)**2 + (b - cb)**2)
            color_diffs.append((color_diff, color))
        return min(color_diffs)[1]

    def push_error_to_neighbours(x, y, current_color, closest_color):
        error = current_color - closest_color
        #print(error)
        try:
            img_data[y    ][x + 1] += (error * (7/16)).astype("uint8")
        except IndexError:
            pass
        try:
            img_data[y + 1][x - 1] += (error * (3/16)).astype("uint8")
        except IndexError:
            pass
        try:
            img_data[y + 1][x    ] += (error * (5/16)).astype("uint8")
        except IndexError:
            pass
        try:
            img_data[y + 1][x + 1] += (error * (1/16)).astype("uint8")
        except IndexError:
            pass

    for y in range(target_size):
        for x in range(target_size):
            #print(x, y)
            if occupied_pixels[y][x]:
                continue
            # try to find the best color for the current_pixel
            current_color = img_data[y][x]
            closest_color = find_closest_color(current_color, x, y)
            #print(closest_color)
            if closest_color[1] == "entity":
                # We make a entity instance so we can query the width and height
                entity = new_entity(closest_color[2], position = [x, y])
                blueprint.add_entity(entity)
                #print(entity.tile_width, entity.tile_height)
                for j in range(entity.tile_height):
                    for i in range(entity.tile_width):
                        try:
                            occupied_pixels[y+j][x+i] = True
                        except IndexError:
                            pass

                #push_error_to_neighbours(x, y, current_color, closest_color[0])

            elif closest_color[1] == "tile":
                blueprint.add_tile(closest_color[2], x, y)
                #print("set {} {}".format(x, y))
                occupied_pixels[y][x] = True
                push_error_to_neighbours(x, y, current_color, closest_color[0])

    # Output the blueprint to a string    
    #print(blueprint.to_string())

    # Sometimes with such large blueprints the regular console might run out of
    # lines before displaying the entire blueprint. If that's the case, you can 
    # also output to a file:
    #with open("examples/image_blueprint.txt", "w") as file:
    #    file.write(blueprint.to_string())

    # Or, you can use a tool to output the contents directly into the user's
    # clipboard:
    pyperclip.copy(blueprint.to_string())

    print("done")


if __name__ == "__main__":
    main()