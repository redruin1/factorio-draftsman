# add_entities.py

from draftsman.blueprintable import Blueprint


def main():
    blueprint = Blueprint()
    for y in range(100):
        for x in range(100):
            blueprint.entities.append("wooden-chest", tile_position=(x, y))


if __name__ == "__main__":
    main()
