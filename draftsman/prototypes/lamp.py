# lamp.py

from draftsman.classes.entity import Entity
from draftsman.classes.exportable import attempt_and_reissue
from draftsman.classes.mixins import (
    CircuitConditionMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
)
from draftsman.classes.vector import Vector, PrimitiveVector
from draftsman.constants import ValidationMode, LampColorMode
from draftsman.signatures import Color, Connections, DraftsmanBaseModel
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
            color_mode: Optional[LampColorMode] = Field(
                LampColorMode.COLOR_MAPPING,
                description="""
                How the lamp should interpret signals when specifying it's color.
                """
            )

        control_behavior: Optional[ControlBehavior] = ControlBehavior()

        color: Optional[Color] = Field(
            Color(r=1, g=1, b=1, a=1),
            description="""
            The constant color of the lamp. Superceeded by any dynamic value 
            given to the lamp, if configured as such.
            """
        )

        always_on: Optional[bool] = Field(
            False,
            description="""Whether or not this lamp is always on."""
        )

        model_config = ConfigDict(title="Lamp")

    def __init__(
        self,
        name: Optional[str] = get_first(lamps),
        position: Union[Vector, PrimitiveVector] = None,
        tile_position: Union[Vector, PrimitiveVector] = (0, 0),
        always_on: Optional[bool] = False,
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

        self.always_on = always_on

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

    @property
    def color_mode(self) -> Optional[LampColorMode]:
        return self.control_behavior.color_mode

    @color_mode.setter
    def color_mode(self, value: Optional[LampColorMode]) -> None:
        self.control_behavior.color_mode = value

    # =========================================================================

    @property
    def always_on(self) -> Optional[bool]:
        """
        Whether or not this entity should always be active, regardless of the 
        current day-night cycle. This option is superceeded by any condition
        specified.

        :getter: Gets whether or not this lamp is always on, or ``None`` if not
            set.
        :setter: Sets whether or not the lamp is always on. Removes the key if 
            set to ``None``.
        """
        return self._root.always_on
    
    @always_on.setter
    def always_on(self, value: Optional[bool]) -> None:
        self._root.always_on = value

    # =========================================================================

    @property
    def color(self) -> Optional[Color]:
        return self._root.color
    
    @color.setter
    def color(self, value: Optional[Color]):
        self._root.color = value

    # =========================================================================

    __hash__ = Entity.__hash__
