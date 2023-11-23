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
    ValidationResult,
    attempt_and_reissue,
)
from draftsman.classes.spatial_like import SpatialLike
from draftsman.classes.vector import Vector, PrimitiveVector
from draftsman.constants import ValidationMode
from draftsman.error import DataFormatError, DraftsmanError
from draftsman.signatures import DraftsmanBaseModel, IntPosition, TileName
from draftsman.utils import AABB

import draftsman.data.tiles as tiles

from pydantic import (
    ConfigDict,
    GetCoreSchemaHandler,
    Field,
    PrivateAttr,
    ValidationError,
    field_serializer,
)
from pydantic_core import CoreSchema, core_schema
from typing import Any, Literal, Optional, Union, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no coverage
    from draftsman.classes.collection import TileCollection

_TILE_COLLISION_SET = CollisionSet([AABB(0, 0, 1, 1)])

_TILE_COLLISION_SET = CollisionSet([AABB(0, 0, 1, 1)])


class Tile(SpatialLike, Exportable):
    """
    Tile class. Used for keeping track of tiles in Blueprints.
    """

    class Format(DraftsmanBaseModel):
        _position: Vector = PrivateAttr()

        name: TileName = Field(..., description="""The Factorio ID of the tile.""")
        position: IntPosition = Field(
            IntPosition(x=0, y=0),
            description="""
            The position of the tile in the blueprint. Specified in integer, 
            tile coordinates.
            """,
        )

        @field_serializer("position")
        def serialize_position(self, _):
            # TODO: make this use global position for when we add this to groups
            return self._position.to_dict()

        model_config = ConfigDict(
            title="Tile",
        )

    def __init__(
        self,
        name: str,
        position=(0, 0),
        validate: Union[
            ValidationMode, Literal["none", "minimum", "strict", "pedantic"]
        ] = ValidationMode.STRICT,
        validate_assignment: Union[
            ValidationMode, Literal["none", "minimum", "strict", "pedantic"]
        ] = ValidationMode.STRICT,
    ):
        """
        Create a new Tile with ``name`` at ``position``. ``position`` defaults
        to ``(0, 0)``.

        :param name: Name of the Tile to create.
        :param position: Position of the tile, in grid-coordinates.

        :exception InvalidTileError: If the name is not a valid Factorio tile id.
        :exception IndexError: If the position does not match the correct
            specification.
        """
        self._root: __class__.Format

        super().__init__()

        self._root = __class__.Format.model_construct()

        # Setup private attributes
        self._root._position = Vector(0, 0)

        # Reference to parent blueprint
        self._parent = None

        # Tile name
        self.name = name

        # Tile positions are in integer grid coordinates
        self.position = position

        self.validate_assignment = validate_assignment

        self.validate(mode=validate).reissue_all(stacklevel=3)

    # =========================================================================

    @property
    def parent(self) -> Optional["TileCollection"]:
        return self._parent

    # =========================================================================

    @property
    def name(self) -> str:
        """
        The name of the Tile.

        Must be a string representing the name of a valid Factorio tile. If the
        name is not recognized in :py:data:`.draftsman.data.tiles.raw`, then
        ``Tile().validate()`` will return errors.

        :getter: Gets the name of the Tile.
        :setter: Sest the name of the Tile.
        :type: ``str``

        :exception InvalidTileError: If the set name is not a valid Factorio
            tile id.
        """
        return self._root.name

    @name.setter
    def name(self, value: str):
        if self.validate_assignment:
            result = attempt_and_reissue(
                self, type(self).Format, self._root, "name", value
            )
            self._root.name = result
        else:
            self._root.name = value

    # =========================================================================

    @property
    def position(self) -> Vector:
        """
        The position of the tile, in tile-grid coordinates.

        ``position`` can be specified as a ``dict`` with ``"x"`` and
        ``"y"`` keys, or more succinctly as a sequence of floats, usually a
        ``list`` or ``tuple``.

        This property is updated in tandem with ``position``, so using them both
        interchangeably is both allowed and encouraged.

        :getter: Gets the position of the Entity.
        :setter: Sets the position of the Entity.
        :type: ``dict{"x": int, "y": int}``

        :exception IndexError: If the set value does not match the above
            specification.
        """
        return self._root._position

    @position.setter
    def position(self, value: Union[PrimitiveVector, Vector]):
        if self.parent:
            raise DraftsmanError("Cannot move tile while it's inside a TileCollection")

        self._root._position.update_from_other(value, int)

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

    # def to_dict(self) -> dict:
    #     """
    #     Converts the Tile to its JSON-dict representation.

    #     :returns: The exported JSON-dict representation of the Tile.
    #     """
    #     return {"name": self.name, "position": self.position.to_dict()}

    def validate(
        self, mode: ValidationMode = ValidationMode.STRICT, force: bool = False
    ) -> ValidationResult:  # TODO: defer to parent
        mode = ValidationMode(mode)

        output = ValidationResult([], [])

        if mode is ValidationMode.NONE or (self.is_valid and not force):
            return output

        context = {
            "mode": mode,
            "object": self,
            "warning_list": [],
            "assignment": False,
        }

        try:
            result = self.Format.model_validate(
                self._root, strict=False, context=context
            )
            # Reassign private attributes
            result._position = self._root._position
            # Acquire the newly converted data
            self._root = result
        except ValidationError as e:
            output.error_list.append(DataFormatError(e))

        output.warning_list += context["warning_list"]

        return output

    # =========================================================================

    def __eq__(self, other):
        return (
            isinstance(other, Tile)
            and self.name == other.name
            and self.position == other.position
        )

    def __repr__(self) -> str:  # pragma: no coverage
        return "<Tile>{}".format(self.to_dict())

    @classmethod
    def __get_pydantic_core_schema__(
        cls, _, handler: GetCoreSchemaHandler
    ) -> CoreSchema:  # pragma: no coverage
        return core_schema.no_info_after_validator_function(cls, handler(Tile.Format))
