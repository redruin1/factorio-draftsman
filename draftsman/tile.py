# tile.py

"""
Alias module. Imports :py:class:`.Tile` under the namespace ``draftsman``.
"""

from draftsman.classes.tile import Tile
from draftsman.classes.exportable import ValidationMode


def new_tile(name: str, **kwargs):
    """
    Factory function for creating a new :py:class:`.Tile`.

    Currently, it's not required to construct a generic tile using this function,
    since there is only one kind of ``Tile`` class. However, this function has
    the same behavior as :py:func:`new_entity`, in that you can use it to quicky
    create a tile object with which to manipulate easily.

    :param name: The string name of a Tile.
    :param kwargs: A dict of all the keyword arguments to pass to the
        constructor.

    :returns: A new :py:class:`.Tile` instance.
    """
    return Tile(name=name, **kwargs)
