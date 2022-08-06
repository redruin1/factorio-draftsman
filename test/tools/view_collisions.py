# view_collisions.py

from draftsman.blueprintable import Blueprint
from draftsman.classes.group import Group
from draftsman.utils import flatten_entities

from tkinter import *

import math


def main():
    bp_string = "0eNqdmt1u4jAQhd8l16Gyx7Ed8yqragU06kaiCQqh2qri3TcpPyplspyTS1ryceKZsY/H/szW20O16+qmz5afWb1pm322/PWZ7evXZrUd/9Z/7KpsmdV99ZblWbN6Gz91q3qbHfOsbl6qv9nSHp/zrGr6uq+r0/NfHz5+N4e3ddUNX7g+ue+HZ1//9IsvRJ7t2v3wVNuMPzWSUp59jMBjfgeRK2Rdvy6qbbXpu3qz2LXb6h4kcgYND1XDD67bQzdK8zEP7lmhO1Si+GmJBfmeToN4UokKCaQSr0EiqUSFlFfI5tC9Vy9TOsrTsJohYi91NwT3639eISby3aImyxpMlwRVV6EhLTleujAhXy+pFDafdQqb0FYtC8um9AQmgKl0rv1wGzLRkHCK27Mydwt1GrS8mSgXmz+rulmcp9R7cPF0RsuTv4VbDc5mv1XnBzFsSHQMnvJJHT+tvkWwODs9zlFDOiYkkiZDosVbilv4FLa8UP1Pqpaa4qksChw8UPB4gQ+5qqZBZJNSx1CFI8K9cmIzXtXoDKUxUhqdpeDhe1geLk9OGLjznHJ4vbEnagSY8OrjcCa8FHmcCZutiDPhiko4s4RjRAQJX4/wKBWGXZYRKL4LweNUsG7NqqavcDzmsTa4fgSPd4F7OSLegZ2bEWjkoRoGrhoh0iaxvgmAerhqHB5vD1eNw+Pt4apxeLw9XEMOD5TH1yAiUHANFUSg4BoqiEBFpulyEivmZ9NFcitWa7r4b4avXbe7tusVuReqBkjzfGzSfWww7DSsbpsD2wiYwAgyOuY/wxMcE75zXhDxC2x/QNSNfWD7AxOYMMs9i0Hcc4icwRX3uLpCyRlciJk4g4swo+EMLsS0VDNHisf78CicZ4ZkOtIzQ9CC9MwQ1JOeGYIG0jNDULZbIGrvKZY85rG2RHpmBFoa0jNDUHaRgaDCQzWMIz0zpK2g2oI/Z4ygIT1pwyGdgbThEDSSNhyClqQNh6CJtOEINBnShkNQS9pwCCqkDYegVPv60meWu7agVgOpYNeN+PiUIvlZvly87stTmNULBweAXo50jVzz2nIa2ea1rtEaw0548fHhijV2Vk8ce3VrZJ6t94itt8ZhhzfXfjiquqDOvZ3R4+VnHSWOQ4zEjb0lIBNH6ZE6S3cGOOY0JZvxE9rSrJO/+xH06ok/2zAQ/ZydvjowxWHb0U4/aaevD0xx6BsxTufQl2ImOGzGO30etWxveYrD7mGcnuWWXR8mOMLms9Pz8Nu9APyy1sBCb2tZYTcqo9Dn/HSPbfnt2luevVfd/uS8SlvEJNGHYUWzcjz+Az5/z8Y="

    blueprint = Blueprint(bp_string)

    entity_list = flatten_entities(blueprint.entities)

    screen_size = 1000

    root = Tk()
    root.title("test")
    root.geometry("{0}x{0}".format(screen_size))

    canvas = Canvas(root, width=screen_size, height=screen_size, bg="white")
    canvas.pack()

    scale = 1000 / max(blueprint.tile_width, blueprint.tile_height)

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
        g_pos = entity.global_position
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
