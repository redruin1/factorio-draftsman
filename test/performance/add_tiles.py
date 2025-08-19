# add_tiles.py

from draftsman.blueprintable import Blueprint


def main():
    blueprint = Blueprint()
    for y in range(100):
        for x in range(100):
            blueprint.tiles.append("landfill", position=(x, y))


if __name__ == "__main__":
    main()
