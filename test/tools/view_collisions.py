# view_collisions.py

"""
View the collision rectangles and entity positions of an input blueprint string.
Provides a simple GUI output scaled to the size of the blueprint using TKinter.
"""

from draftsman.blueprintable import Blueprint
from draftsman.classes.group import Group
from draftsman.utils import flatten_entities

from tkinter import *

import math


def main():
    bp_string = input()

    blueprint = Blueprint(bp_string)
    print(blueprint.area)

    entity_list = flatten_entities(blueprint.entities)

    print(entity_list)

    screen_size = 1000

    translation = blueprint.area.top_left

    root = Tk()
    root.title("test")
    root.geometry("{0}x{0}".format(screen_size))

    canvas = Canvas(root, width=screen_size, height=screen_size, bg="white")
    canvas.pack()

    scale = screen_size / max(blueprint.tile_width, blueprint.tile_height)

    grid_size = 1

    num_h_div = math.ceil(1000 / (scale * grid_size))
    num_v_div = math.ceil(1000 / (scale * grid_size))
    for i in range(num_h_div):
        canvas.create_line(
            i * grid_size * scale,
            0,
            i * grid_size * scale,
            screen_size,
            fill="lightgrey",
        )
    for i in range(num_v_div):
        canvas.create_line(
            0,
            i * grid_size * scale,
            screen_size,
            i * grid_size * scale,
            fill="lightgrey",
        )

    grid_size = 5

    num_h_div = math.ceil(1000 / (scale * grid_size))
    num_v_div = math.ceil(1000 / (scale * grid_size))
    for i in range(num_h_div):
        canvas.create_line(
            i * grid_size * scale, 0, i * grid_size * scale, screen_size, fill="grey"
        )
    for i in range(num_v_div):
        canvas.create_line(
            0, i * grid_size * scale, screen_size, i * grid_size * scale, fill="grey"
        )

    for entity in entity_list:
        g_pos = entity.global_position - translation
        canvas.create_rectangle(
            (g_pos.x - 0.1) * scale,
            (g_pos.y - 0.1) * scale,
            (g_pos.x + 0.1) * scale,
            (g_pos.y + 0.1) * scale,
            fill="",
            outline="green",
        )
        for shape in entity.collision_set.shapes:
            points = [
                [(point[0] + g_pos.x) * scale, (point[1] + g_pos.y) * scale]
                for point in shape.get_points()
            ]
            canvas.create_polygon(points, fill="", outline="red")

    root.mainloop()


if __name__ == "__main__":
    main()
