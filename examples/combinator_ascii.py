# combinator_ascii.py

"""
Creates two sets of constant combinators. The first one is a conversion of nixie
tube signals to ASCII codes, and the second one is a text string written in 
sequential numbers where the value of each number corresponds to a letter.
"""

from draftsman.blueprintable import Blueprint
from draftsman.entity import ConstantCombinator
from draftsman.error import MissingModError
from draftsman.data.mods import mod_list

import math


def main():

    # We need Nixie tubes in order for this script to work:
    # https://mods.factorio.com/mod/nixie-tubes
    if not mod_list.get("nixie-tubes", False):
        raise MissingModError("Nixie tubes")

    letters = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ[]{}()!.?@*-%+/"
    translations = {
        "(": "paropen",
        ")": "parclose",
        "[": "sqopen",
        "]": "sqclose",
        "{": "curopen",
        "}": "curclose",
        ".": "stop",
        "?": "qmark",
        "!": "exmark",
        "@": "at",
        "/": "slash",
        "*": "asterisk",
        "-": "minus",
        "+": "plus",
        "%": "percent",
    }

    for letter in letters:
        if letter.isalnum():
            translations[letter] = letter

    letter_list = list(letters)
    letter_list.sort()

    blueprint = Blueprint()

    combinator = ConstantCombinator("constant-combinator")
    num_combinators = math.ceil(len(letter_list) / combinator.item_slot_count)
    for i in range(num_combinators):
        combinator.tile_position = (i, 0)
        blueprint.entities.append(combinator)

    for i, letter in enumerate(letter_list):
        current_entity = int(i / combinator.item_slot_count)
        index = i % combinator.item_slot_count
        id = "signal-{}".format(translations[letter])
        value = ord(letter)
        blueprint.entities[current_entity].set_signal(index, id, value)

    print(blueprint.to_string(), "\n")

    blueprint.entities = None

    statement = "It works!"

    blueprint.entities.append(combinator)
    for i, letter in enumerate(statement.upper()):
        index = i
        id = "signal-{}".format(i)
        value = ord(letter)
        blueprint.entities[0].set_signal(index, id, value)

    print(blueprint.to_string())


if __name__ == "__main__":
    main()
