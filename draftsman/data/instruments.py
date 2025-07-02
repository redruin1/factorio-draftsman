# instruments.py

import pickle

import importlib.resources as pkg_resources

from draftsman import data
from draftsman.data.entities import of_type

# from draftsman.data.entities import programmable_speakers


with pkg_resources.open_binary(data, "instruments.pkl") as inp:
    _data: list = pickle.load(inp)
    raw: dict[str, list[dict]] = _data[0]
    index_of: dict[str, dict[str, dict[str, int]]] = _data[1]
    name_of: dict[str, dict[int, dict[int, str]]] = _data[2]


def add_instrument(
    instrument_name: str,
    notes: list[str],
    instrument_index: int = None,
    entity_name: str = "programmable-speaker",
):
    """
    Adds a new instrument to Draftsman's environment, which persists until the
    end of the session.
    """
    if entity_name not in of_type["programmable-speaker"]:
        raise TypeError(
            "Cannot add instrument to unknown programmable speaker '{}'".format(
                entity_name
            )
        )

    # Add to the end of the instruments list if index is omitted
    instrument_index = (
        len(raw[entity_name]) if instrument_index is None else instrument_index
    )

    # Update `raw`
    new_entry = {"name": instrument_name, "notes": [{"name": note} for note in notes]}
    raw[entity_name].insert(instrument_index, new_entry)

    # Update `index`
    index_entry = {notes[i]: i for i in range(len(notes))}
    index_of[entity_name][instrument_name] = {"self": instrument_index, **index_entry}

    # Update `names`
    names_entry = {i: notes[i] for i in range(len(notes))}
    name_of[entity_name][instrument_index] = {"self": instrument_name, **names_entry}
