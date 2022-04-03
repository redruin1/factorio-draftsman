# draftsman_logo.py

"""
Script to generate the draftsman logo.
"""

from draftsman.blueprintable import Blueprint

from PIL import Image, ImageDraw, ImageFont
import numpy as np

from enum import IntEnum
import math


def draw_gear(draw, pos, size, fill_color, stroke_color, bg_color):
    def gear_point(angle, a_off, size, s_off):
        return (
            math.cos(angle + a_off) * (size / 2 + s_off) + pos[0],
            math.sin(angle + a_off) * (size / 2 + s_off) + pos[1]
        )

    gear_points = []
    for i in range(8):
        angle = (i / 8) * 2 * math.pi
        tooth_range = size / 8
        gear_points.append(gear_point(angle, -0.2, size, 0))
        gear_points.append(gear_point(angle, -0.12, size, tooth_range))
        gear_points.append(gear_point(angle, +0.12, size, tooth_range))
        gear_points.append(gear_point(angle, +0.2, size, 0))
        
    draw.polygon(gear_points, fill = fill_color, outline = stroke_color)
    internal_size = size / 2
    draw.ellipse(
        ((pos[0] - internal_size/2, pos[1] - internal_size/2),          
         (pos[0] + internal_size/2, pos[1] + internal_size/2)),
        fill = bg_color, outline = stroke_color
    )


def main():
    # Specify the colors and their corresponding tiles
    class Color(IntEnum):
        R_CONC = 0
        R_H_CONC = 60
        CONC = 127
        H_CONC = 200
        STONE = 255

    conversions = {
        0: "refined-concrete",
        60: "refined-hazard-concrete-left",
        127: "concrete",
        200: "hazard-concrete-left",
        255: "stone-path"
    }

    # Generate the image
    img_size = (128, 128)
    # Create the image
    im = Image.new(mode="L", size = img_size)
    draw = ImageDraw.Draw(im)
    draw.fontmode = "1"
    # Get the font
    font = ImageFont.truetype("examples/TitilliumWeb-SemiBold.ttf", 17)
    # checkered bg
    draw.rectangle(((0, 0), img_size), fill = 1)
    # checker_size = 16
    # extent_x = math.floor(img_size[0] / checker_size) + 2
    # extent_y = math.floor(img_size[1] / checker_size) + 2
    # for j in range(extent_y):
    #     for i in range(extent_x):
    #         if (i + j) % 2 == 0:
    #             checker_color = 60
    #         else:
    #             checker_color = 255
    #         draw.rectangle(
    #             (i * checker_size, 
    #              j * checker_size,
    #              i * checker_size + checker_size - 1, 
    #              j * checker_size + checker_size - 1),
    #             fill = checker_color
    #         )
    # Area
    border_dim = (110, 40)
    draw.rectangle(
        (img_size[0]//2 - border_dim[0]//2-1, img_size[1]//2 - border_dim[1]//2, 
         img_size[0]//2 + border_dim[0]//2, img_size[1]//2 + border_dim[1]//2), 
         fill = Color.H_CONC, outline = Color.R_CONC
    )
    # Text
    # Normally I'd use the outline keyword, but it antialiases which breaks my
    # hard equals method of specification
    # So instead, I'm just going to draw the text 4 times offset by a single 
    # pixel on every axis
    matrix = [
        (-1, 0),
        (0, -1),
        (1, 0),
        (0, 1)
    ]
    # for offset in matrix:
    #     draw.text(
    #         (img_size[0]/2 - 27 + offset[0], img_size[1]/2 - 14 + offset[1]), 
    #         "draftsman", fill = Color.R_CONC, font = font,
    #     )
    # Then I'm going to draw the text on top
    draw.text(
        (img_size[0]/2 - 27, img_size[1]/2 - 14), 
        "draftsman", fill = Color.R_CONC, font = font
    )
    # Gear
    draw_gear(draw, (img_size[0]/2 - 39, img_size[1]/2), 15, Color.R_H_CONC, Color.R_CONC, Color.H_CONC)

    #im.show()

    # Get image data
    img_data = np.array(im)
    #print(img_data)

    # Convert the image into a blueprint
    blueprint = Blueprint()
    # Set the snapping grid so that it binds to the chunk grid
    blueprint.snapping_grid_size = [32, 32]
    blueprint.absolute_snapping = True

    for j in range(img_size[1]):
        for i in range(img_size[0]):
            val = img_data[j][i]
            if val == Color.H_CONC:
                if (i + j) % 2 == 0:
                    tile_name = "hazard-concrete-left"
                else:
                    tile_name = "hazard-concrete-right"
                blueprint.tiles.append(tile_name, position = (i, j))
            elif val in conversions:
                blueprint.tiles.append(conversions[val], position = (i, j))

    print(blueprint.to_string())


if __name__ == "__main__":
    main()