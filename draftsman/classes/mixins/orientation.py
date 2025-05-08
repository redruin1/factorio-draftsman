# orientation.py

from draftsman.classes.collision_set import CollisionSet
from draftsman.classes.exportable import Exportable
from draftsman.constants import Orientation
from draftsman.serialization import draftsman_converters
from draftsman.utils import Rectangle
from draftsman.validators import instance_of, try_convert

from draftsman.data import entities

import attrs
from pydantic import BaseModel, Field
from typing import Optional


@attrs.define(slots=False)
class OrientationMixin(Exportable):
    """
    Used in trains and wagons to specify their direction.
    """

    class Format(BaseModel):
        orientation: Optional[Orientation] = Field(
            Orientation.NORTH,
            description="""
            The floating point rotation of the entity, used for RollingStock.
            Orientation is a continuous range between [0.0, 1.0), which differs
            from 'direction' which is used on all other entities.
            """,
        )

    # def __init__(self, name: str, similar_entities: list[str], **kwargs):
    #     self._root: __class__.Format

    #     # Get the (static) property attribute from data.raw
    #     # We do this before because we want to overwrite the `collision_set`
    #     # property in this class for convenience
    #     original = entities.collision_sets.get(name, None)
    #     if original is not None:
    #         original = original.shapes[0]
    #         width = original.bot_right[0] - original.top_left[0]
    #         height = original.bot_right[1] - original.top_left[1]

    #         # Make a per-instance copy specific to this rolling stock
    #         self._collision_set = CollisionSet([Rectangle((0, 0), width, height, 0)])
    #     else:
    #         self._collision_set = None

    #     super().__init__(name, similar_entities, **kwargs)

    #     self.orientation = kwargs.get("orientation", Orientation.NORTH)

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
    The angle that the current Entity is facing, expressed as a ``float``
    in the range ``[0.0, 1.0)``, where ``0.0`` is North and increases
    clockwise.

    Raises :py:class:`.ValueWarning` if set to a value not in the range
    ``[0.0, 1.0)``.

    .. NOTE::

        This is distinct from ``direction``, which is used on grid-aligned
        entities and can only be a max of 16 possible rotations.
    """

    # @property
    # def orientation(self) -> Orientation:
    #     """
    #     The angle that the current Entity is facing, expressed as a ``float``
    #     in the range ``[0.0, 1.0)``, where ``0.0`` is North and increases
    #     clockwise.

    #     Raises :py:class:`.ValueWarning` if set to a value not in the range
    #     ``[0.0, 1.0)``.

    #     .. NOTE::

    #         This is distinct from ``direction``, which is used on grid-aligned
    #         entities and can only be a max of 8 possible rotations.

    #     :getter: Gets the orientation of the Entity.
    #     :setter: Sets the orientation of the Entity. Orients the object to north
    #         (0.0) if set to ``None``.
    #     """
    #     return self._root.orientation

    # @orientation.setter
    # def orientation(self, value: Union[float, Orientation, None]):
    #     if self.validate_assignment:
    #         value = attempt_and_reissue(
    #             self, type(self).Format, self._root, "orientation", value
    #         )

    #     if value is None:
    #         self._root.orientation = Orientation.NORTH
    #         if self.collision_set is not None:
    #             self._collision_set.shapes[0].angle = 0
    #     elif isinstance(value, (float, int)):
    #         self._root.orientation = Orientation(value)
    #         if self.collision_set is not None:
    #             self._collision_set.shapes[0].angle = (value % 1.0) * 360.0
    #     else:
    #         self._root.orientation = value
    #         # if self.collision_set is not None:
    #         #     self._collision_set.shapes[0].angle = (value % 1.0) * 360.0

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

    # =========================================================================

    # def __eq__(self, other) -> bool:
    #     return super().__eq__(other) and self.orientation == other.orientation


draftsman_converters.add_hook_fns(
    # {"$id": "factorio:orientation_mixin"},
    OrientationMixin,
    lambda fields: {fields.orientation.name: "orientation"},
)
