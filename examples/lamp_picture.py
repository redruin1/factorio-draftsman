# lamp_picture.py

"""
Creates a grid of colored lamps to display a given image.

Requirements:
    pillow
    numpy
    [Optional] pyperclip
"""

from draftsman.blueprintable import Blueprint
from draftsman.entity import Lamp

from PIL import Image
import numpy as np

try:
    import pyperclip
except ImportError:
    pyperclip = None


def main():
    print("Filepath of image to convert:")
    img_path = input()

    target_width = 150
    target_height = None

    # open an image
    img = Image.open(img_path)
    width, height = img.size

    if target_height is None:
        aspect_rat = width / height
        target_height = int(target_width * aspect_rat)

    img = img.resize((target_width, target_height))

    # Unmodified images can look a little washed out, due to the nature in which
    # Factorio lamps don't occupy the entire tile area. Here we increase the
    # image contrast to make it pop a little more (particularly on regular
    # truecolor images):
    level = 100
    factor = (259 * (level + 255)) / (255 * (259 - level))

    def contrast(c):
        return 128 + factor * (c - 128)

    img = img.point(contrast)

    img_data = np.array(img)[:, :, :3]

    blueprint = Blueprint(validate_assignment="none")
    blueprint.label = img_path

    lamp = Lamp("signal-lamp")
    lamp.always_on = True

    for y in range(target_height):
        for x in range(target_width):
            lamp.tile_position = (x, y)
            lamp.color = {
                "r": int(img_data[y][x][0]),
                "g": int(img_data[y][x][1]),
                "b": int(img_data[y][x][2]),
                "a": 255,
            }
            blueprint.entities.append(lamp)

    # Output is usually too big for the console, so we just write it to a file
    if pyperclip is not None:
        pyperclip.copy(blueprint.to_string())
        print("Copied to clipboard.")
    else:
        with open("examples/output/lamp_image.blueprint", "w") as file:
            file.write(blueprint.to_string())
        print("Wrote 'examples/output/lamp_image.blueprint'")


if __name__ == "__main__":
    main()
