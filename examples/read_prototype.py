# read_prototype.py

"""
Every entity recognized by draftsman has a `prototype` attribute, which contains
a reference to the associated prototype data of that entity directly from
Factorio's `data.raw`. With this, you're able to extract basically any
information you want from the entity in question and access it via Draftsman
script.
"""

from draftsman.constants import ValidationMode
from draftsman.entity import Inserter
from draftsman import validators


def main():
    inserter = Inserter("inserter")

    # For commonly accessed information, Draftsman provides first-class
    # attributes that return proper defaults as defined by the Factorio
    # Prototype API:
    print(inserter.collision_mask)
    print(inserter.circuit_wire_max_distance)
    print(inserter.filter_count)
    print(inserter.energy_source["type"])
    print(inserter.allowed_fuel_items)

    # These first class attributes will return `None` if the detected entity is
    # unrecognized in the current configuration:
    with validators.set_mode(ValidationMode.MINIMUM):
        unknown_inserter = Inserter("unknown")
    print(unknown_inserter.collision_mask)
    print(unknown_inserter.circuit_wire_max_distance)
    print(unknown_inserter.filter_count)
    print(unknown_inserter.energy_source)
    print(unknown_inserter.allowed_fuel_items)

    # Even if Draftsman doesn't supply it as a first-class attribute, you can
    # almost certainly grab that information using the `prototype` attribute,
    # which is equivalent to the raw `data.raw` dict:
    print(inserter.prototype.keys())

    # You can't get actual assets with the environment that ships with Draftsman,
    # but you can get metadata (including filepaths) of assets, which you can
    # then grab if you have a copy of the game installed
    print(Inserter("inserter").prototype.get("hand_closed_picture", None))


if __name__ == "__main__":
    main()
