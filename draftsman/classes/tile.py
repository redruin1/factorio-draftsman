# tile.py

"""
.. code-block:: python

    {
        "name": str, # Name of the tile
        "position": {"x": int, "y": int} # Position of the tile
    }
"""

from draftsman import DEFAULT_FACTORIO_VERSION
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

from draftsman.data import mods, tiles

import attrs
from typing import Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no coverage
    from draftsman.classes.collection import Collection

_TILE_COLLISION_SET = CollisionSet([AABB(0, 0, 1, 1)])


@attrs.define
class Tile(SpatialLike, Exportable):
    """
    Tile class. Used for keeping track of tiles in Blueprints.
    """

    # =========================================================================

    _parent = attrs.field(
        default=None,
        init=False,
        repr=False,
        eq=False,
        metadata={"omit": True, "deepcopy_func": lambda value, memo: None},
    )

    @property
    def parent(self) -> Optional["Collection"]:
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

    position: Vector = attrs.field(  # TODO: maybe tile_position?
        factory=lambda: Vector(0, 0),
        converter=Vector.from_other,
        on_setattr=_set_position,
        metadata={"omit": False},
    )
    """
    

    The position of the tile, in integer tile-grid coordinates.
    """

    # =========================================================================

    @property
    def global_position(self) -> Vector:
        if self.parent and hasattr(self.parent, "global_position"):
            return self.parent.global_position + self.position
        else:
            return self.position

    # =========================================================================

    @property
    def collision_set(self) -> CollisionSet:
        return _TILE_COLLISION_SET

    # =========================================================================

    @property
    def collision_mask(self) -> Optional[set]:
        if mods.versions.get("base", DEFAULT_FACTORIO_VERSION) < (2, 0):
            return tiles.raw.get(self.name, {}).get("collision_mask", None)
        else:
            return (
                tiles.raw.get(self.name, {})
                .get("collision_mask", {})
                .get("layers", None)
            )

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
            and self.global_position == other.global_position
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


@attrs.define  # pragma: no coverage
class _Export:
    global_position: Vector = attrs.field(metadata={"omit": False})


_export_fields = attrs.fields(_Export)

draftsman_converters.add_hook_fns(
    Tile,
    lambda fields: {
        "name": fields.name.name,
        "position": fields.position.name,
    },
    lambda fields, converter: {
        "name": fields.name.name,
        "position": _export_fields.global_position,
    },
)
