# lamp.py

from draftsman.classes.entity import Entity
from draftsman.classes.exportable import attempt_and_reissue
from draftsman.classes.mixins import (
    CircuitConditionMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
)
from draftsman.classes.vector import Vector, PrimitiveVector
from draftsman.constants import ValidationMode
from draftsman.signatures import Connections, DraftsmanBaseModel
from draftsman.utils import get_first

from draftsman.data.entities import lamps

from pydantic import ConfigDict, Field
from typing import Any, Literal, Optional, Union


class Lamp(
    CircuitConditionMixin, ControlBehaviorMixin, CircuitConnectableMixin, Entity
):
    """
    An entity that illuminates an area.
    """

    class Format(
        CircuitConditionMixin.Format,
        ControlBehaviorMixin.Format,
        CircuitConnectableMixin.Format,
        Entity.Format,
    ):
        class ControlBehavior(CircuitConditionMixin.ControlFormat, DraftsmanBaseModel):
            use_colors: Optional[bool] = Field(
                False,
                description="""
                Whether or not the presence of a color signal will affect the
                light that this lamp emits, if it's circuit condition is met.
                If multiple colors are passed to the lamp, the color with the
                first lexographical order is emitted.
                """,
            )

        control_behavior: Optional[ControlBehavior] = ControlBehavior()

        model_config = ConfigDict(title="Lamp")

    def __init__(
        self,
        name: Optional[str] = get_first(lamps),
        position: Union[Vector, PrimitiveVector] = None,
        tile_position: Union[Vector, PrimitiveVector] = (0, 0),
        connections: Connections = {},
        control_behavior: Format.ControlBehavior = {},
        tags: dict[str, Any] = {},
        validate_assignment: Union[
            ValidationMode, Literal["none", "minimum", "strict", "pedantic"]
        ] = ValidationMode.STRICT,
        **kwargs
    ):
        """
        TODO
        """

        self._root: __class__.Format
        self.control_behavior: __class__.Format.ControlBehavior

        super().__init__(
            name,
            lamps,
            position=position,
            tile_position=tile_position,
            connections=connections,
            control_behavior=control_behavior,
            tags=tags,
            **kwargs
        )

        self.validate_assignment = validate_assignment

    # =========================================================================

    @property
    def use_colors(self) -> Optional[bool]:
        """
        Whether or not this entity should use color signals to determine it's
        color.

        :getter: Gets whether or not to use colors, or ``None`` if not set.
        :setter: Sets whether or not to use colors. Removes the key if set to
            ``None``.

        :exception TypeError: If set to anything other than a ``bool`` or ``None``.
        """
        return self.control_behavior.use_colors

    @use_colors.setter
    def use_colors(self, value: Optional[bool]):
        if self.validate_assignment:
            result = attempt_and_reissue(
                self,
                type(self).Format.ControlBehavior,
                self.control_behavior,
                "use_colors",
                value,
            )
            self.control_behavior.use_colors = result
        else:
            self.control_behavior.use_colors = value

    # =========================================================================

    __hash__ = Entity.__hash__
