# orientation.py

from draftsman.classes.collision_set import CollisionSet
from draftsman.classes.exportable import Exportable
from draftsman.constants import Orientation
from draftsman.serialization import draftsman_converters
from draftsman.utils import Rectangle, get_first
from draftsman.validators import instance_of, try_convert

from draftsman.data import entities

import attrs
from typing import Optional


@attrs.define(slots=False)
class OrientationMixin(Exportable):
    """
    Used in trains and wagons to specify their direction.
    """

    def __attrs_pre_init__(self, name=attrs.NOTHING, *args, first_call=None, **kwargs):
        if not first_call:
            return

        name = name if name is not attrs.NOTHING else get_first(self.similar_entities)
        object.__setattr__(self, "name", name)
        object.__setattr__(
            self, "orientation", kwargs.get("orientation", Orientation.NORTH)
        )
        self._collision_set = self.get_default_collision_set()

    # =========================================================================

    @property
    def tile_width(self) -> int:
        # Tile width/height of orientable entities (vehicles/trains) is a little
        # less meaningful when the have non-cardinal orientations, and is
        # generally unintuitive. Therefore we override the tile width/height
        # to zero and have the `tile_position` be identical to `position`.
        return 0

    # =========================================================================

    @property
    def tile_height(self) -> int:
        return 0

    # =========================================================================

    def _set_orientation(self, attr: attrs.Attribute, value):
        # Convert
        value = attr.converter(value)
        # Validate
        attr.validator(self, attr, value)
        # instance_of(Orientation)(self, attr, value)
        if self.collision_set is not None:
            self._collision_set.shapes[0].angle = (value % 1.0) * 360.0
        return value

    orientation: Orientation = attrs.field(
        default=Orientation.NORTH,
        converter=try_convert(Orientation),
        on_setattr=_set_orientation,
        validator=instance_of(Orientation),
    )
    """
    .. serialized::

        This attribute is imported/exported from blueprint strings.

    The angle that the current Entity is facing, expressed as a ``float``
    in the range ``[0.0, 1.0)``, where ``0.0`` is North and increases
    clockwise.

    Raises :py:class:`.ValueWarning` if set to a value not in the range
    ``[0.0, 1.0)``.

    .. NOTE::

        This is distinct from ``direction``, which is used on grid-aligned
        entities and can only be a max of 16 possible rotations.
    """

    # =========================================================================

    _collision_set: Optional[CollisionSet] = attrs.field(
        init=False, repr=False, metadata={"omit": True}
    )

    @_collision_set.default
    def get_default_collision_set(self) -> CollisionSet:
        original = entities.collision_sets.get(self.name, None)
        if original is None:
            return None
        original = original.shapes[0]
        # TODO: why are we only grabbing a single rectangle? Shouldn't we be
        # grabbing the entire grabbed collision set and rotating it by orientation?
        width = original.bot_right[0] - original.top_left[0]
        height = original.bot_right[1] - original.top_left[1]
        # Orientation might not be valid, so we default to 0 if thats the case
        orientation = (
            self.orientation if isinstance(self.orientation, Orientation) else 0.0
        )
        return CollisionSet(
            [Rectangle((0, 0), width, height, (orientation % 1.0) * 360.0)]
        )

    @property
    def collision_set(self) -> Optional[CollisionSet]:
        return self._collision_set

    # =========================================================================

    def mergable_with(self, other: "OrientationMixin") -> bool:
        base_mergable = super().mergable_with(other)
        return base_mergable and self.orientation == other.orientation


draftsman_converters.add_hook_fns(
    OrientationMixin,
    lambda fields: {fields.orientation.name: "orientation"},
)
