# orientation.py

from draftsman.classes.collision_set import CollisionSet
from draftsman.classes.exportable import attempt_and_reissue
from draftsman.constants import Orientation
from draftsman.utils import Rectangle

from draftsman.data import entities

from pydantic import BaseModel, Field
from typing import Optional, Union

from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no coverage
    from draftsman.classes.entity import Entity


class OrientationMixin:
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

    def __init__(self, name: str, similar_entities: list[str], **kwargs):
        self._root: __class__.Format

        # Get the (static) property attribute from data.raw
        # We do this before because we want to overwrite the `collision_set`
        # property in this class for convenience
        original = entities.collision_sets.get(name, None)
        if original is not None:
            original = original.shapes[0]
            width = original.bot_right[0] - original.top_left[0]
            height = original.bot_right[1] - original.top_left[1]

            # Make a per-instance copy specific to this rolling stock
            self._collision_set = CollisionSet([Rectangle((0, 0), width, height, 0)])
        else:
            self._collision_set = None

        super().__init__(name, similar_entities, **kwargs)

        self.orientation = kwargs.get("orientation", Orientation.NORTH)

    # =========================================================================

    @property
    def collision_set(self) -> CollisionSet:
        return self._collision_set

    # =========================================================================

    @property
    def orientation(self) -> Orientation:
        """
        The angle that the current Entity is facing, expressed as a ``float``
        in the range ``[0.0, 1.0)``, where ``0.0`` is North and increases
        clockwise. TODO: update

        Raises :py:class:`.ValueWarning` if set to a value not in the range
        ``[0.0, 1.0)``.

        .. NOTE::

            This is distinct from ``direction``, which is used on grid-aligned
            entities and can only be a max of 8 possible rotations.

        :getter: Gets the orientation of the Entity.
        :setter: Sets the orientation of the Entity. Orients the object to north
            (0.0) if set to ``None``.
        :type: ``float``
        """
        return self._root.orientation

    @orientation.setter
    def orientation(self, value: Union[float, Orientation, None]):
        if self.validate_assignment:
            value = attempt_and_reissue(
                self, type(self).Format, self._root, "orientation", value
            )

        if value is None:
            self._root.orientation = Orientation.NORTH
            if self.collision_set is not None:
                self._collision_set.shapes[0].angle = 0
        elif isinstance(value, (float, int)):
            self._root.orientation = Orientation(value)
            if self.collision_set is not None:
                self._collision_set.shapes[0].angle = (value % 1.0) * 360.0
        else:
            self._root.orientation = value
            # if self.collision_set is not None:
            #     self._collision_set.shapes[0].angle = (value % 1.0) * 360.0

    # =========================================================================

    def mergable_with(self, other: "Entity") -> bool:
        base_mergable = super().mergable_with(other)
        return base_mergable and self.orientation == other.orientation

    # =========================================================================

    def __eq__(self, other) -> bool:
        return super().__eq__(other) and self.orientation == other.orientation
