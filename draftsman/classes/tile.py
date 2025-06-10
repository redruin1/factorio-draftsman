# tile.py

"""
.. code-block:: python

    {
        "name": str, # Name of the tile
        "position": {"x": int, "y": int} # Position of the tile
    }
"""

from draftsman.classes.collision_set import CollisionSet
from draftsman.classes.exportable import (
    Exportable,
)
from draftsman.classes.spatial_like import SpatialLike
from draftsman.classes.vector import Vector
from draftsman.serialization import draftsman_converters
from draftsman.signatures import (
    TileID,
)
from draftsman.utils import AABB
from draftsman.validators import instance_of

import draftsman.data.tiles as tiles

import attrs
from typing import Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no coverage
    from draftsman.classes.collection import TileCollection

_TILE_COLLISION_SET = CollisionSet([AABB(0, 0, 1, 1)])


@attrs.define
class Tile(SpatialLike, Exportable):
    """
    Tile class. Used for keeping track of tiles in Blueprints.
    """

    # =========================================================================

    # FIXME: I would like to annotate this, but cattrs cannot find the location of `TileCollection`
    _parent = attrs.field(
        default=None, init=False, repr=False, eq=False, metadata={"omit": True}
    )

    @property
    def parent(self) -> Optional["TileCollection"]:
        return self._parent

    # =========================================================================

    name: TileID = attrs.field(
        validator=instance_of(TileID),
        metadata={"omit": False},
    )
    """
    The name of the Tile.

    Must be a string representing the name of a valid Factorio tile. If the
    name is not recognized in :py:data:`.draftsman.data.tiles.raw`, then
    ``Tile().validate()`` will return errors.
    """

    # =========================================================================

    def _set_position(self, _: attrs.Attribute, value: Any):
        self.position.update_from_other(value, int)

        return self.position

    position: Vector = attrs.field(
        factory=lambda: Vector(0, 0),
        converter=Vector.from_other,
        on_setattr=_set_position,
        metadata={"omit": False},
    )
    """
    The position of the tile, in tile-grid coordinates.

    ``position`` can be specified as a ``dict`` with ``"x"`` and
    ``"y"`` keys, or more succinctly as a sequence of floats, usually a
    ``list`` or ``tuple``.
    """

    # =========================================================================

    @property
    def global_position(self) -> Vector:
        # This is redundant in this case because tiles cannot be placed inside
        # of Groups (yet)
        # However, it's still necessary.
        return self.position

    # =========================================================================

    @property
    def collision_set(self) -> CollisionSet:
        return _TILE_COLLISION_SET

    # =========================================================================

    @property
    def collision_mask(self) -> Optional[set]:
        return tiles.raw.get(self.name, {"collision_mask": None})["collision_mask"]

    # =========================================================================

    def mergable_with(self, other: "Tile") -> bool:
        """
        Determines if two entities are mergeable, or that they can be combined
        into a single tile. Two tiles are considered mergable if they have the
        same ``name`` and exist at the same ``position``

        :param other: The other ``Tile`` to check against.

        :returns: ``True`` if the tiles are mergable, ``False`` otherwise.
        """
        return (
            isinstance(other, Tile)
            and self.name == other.name
            and self.position == other.position
        )

    def merge(self, other: "Tile"):
        """
        Merges this tile with another one. Due to the simplicity of tiles, this
        does nothing as long as the merged tiles are of the same name. Allows
        you to overlap areas of concrete and landfill without issuing
        :py:class:`.OverlappingObjectsWarning`s.

        :param other: The other tile underneath this one.
        """
        pass

    def __repr__(self) -> str:  # pragma: no coverage
        return "<Tile>{}".format(self.to_dict())


draftsman_converters.add_hook_fns(
    Tile,
    lambda fields: {
        "name": fields.name.name,
        "position": fields.position.name,  # TODO: global_position
    },
)
