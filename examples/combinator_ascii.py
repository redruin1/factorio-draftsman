# combinator_ascii.py

"""
Creates two sets of constant combinators. The first one is a conversion of nixie
tube signals to ASCII codes, where the signal ID is the symbol it represents and
the value is it's ASCII value.

The second one is a set of ordered unique signals where the value of each 
corresponds to the letter of some text phrase. Here the types of the signals are
arbitrary, and could be any signal as long as they're different from one another; 
their values are the only important factor in determining which letter they 
represent.

The purpose of these combinators would be to convert the values of a set of 
arbitrary signals into a set of ordered signals which could then be fed
to a Nixie-Tube array to display text. This way text could be stored in a very
dense, compressed signal frame instead of many duplicate frames, and perhaps
even multiple letters could be stored in a single 32-bit number.
"""

from draftsman.blueprintable import Blueprint
from draftsman.entity import ConstantCombinator
from draftsman.error import MissingModError
from draftsman.data.mods import mod_list

import math


def main():
    letters = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    translations = {}

    # We allow Nixie-tubes symbols as well, since we might want to make those
    # visible
    # https://mods.factorio.com/mod/nixie-tubes
    if mod_list.get("nixie-tubes", False):
        letters += "[]{}()!.?@*-%+/"
        translations.update(
            {
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
        )

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
        if letter not in translations:
            continue
        index = i
        id = "signal-{}".format(i)
        value = ord(letter)
        blueprint.entities[0].set_signal(index, id, value)

    print(blueprint.to_string())


if __name__ == "__main__":
    main()
