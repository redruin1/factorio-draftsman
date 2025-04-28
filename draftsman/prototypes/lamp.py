# lamp.py

from draftsman.classes.entity import Entity
from draftsman.classes.exportable import attempt_and_reissue
from draftsman.classes.mixins import (
    ColorMixin,
    LogisticConditionMixin,
    CircuitConditionMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
)
from draftsman.classes.vector import Vector, PrimitiveVector
from draftsman.constants import ValidationMode, LampColorMode
from draftsman.serialization import (
    draftsman_converters,
)
from draftsman.signatures import AttrsColor, Connections, DraftsmanBaseModel
from draftsman.utils import get_first
from draftsman.validators import instance_of

from draftsman.data.entities import lamps

import attrs
import cattrs
from pydantic import ConfigDict, Field
from typing import Any, Literal, Optional, Union


@attrs.define
class Lamp(
    ColorMixin,
    LogisticConditionMixin,
    CircuitConditionMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    Entity,
):
    """
    An entity that illuminates an area.
    """

    # class Format(
    #     CircuitConditionMixin.Format,
    #     ControlBehaviorMixin.Format,
    #     CircuitConnectableMixin.Format,
    #     Entity.Format,
    # ):
    #     class ControlBehavior(CircuitConditionMixin.ControlFormat, DraftsmanBaseModel):
    #         use_colors: Optional[bool] = Field(
    #             False,
    #             description="""
    #             Whether or not the presence of a color signal will affect the
    #             light that this lamp emits, if it's circuit condition is met.
    #             If multiple colors are passed to the lamp, the color with the
    #             first lexographical order is emitted.
    #             """,
    #         )
    #         color_mode: Optional[LampColorMode] = Field(
    #             LampColorMode.COLOR_MAPPING,
    #             description="""
    #             How the lamp should interpret signals when specifying it's color.
    #             """,
    #         )

    #     control_behavior: Optional[ControlBehavior] = ControlBehavior()

    #     # color: Optional[Color] = Field(
    #     #     Color(r=1, g=1, b=1, a=1),
    #     #     description="""
    #     #     The constant color of the lamp. Superceeded by any dynamic value
    #     #     given to the lamp, if configured as such.
    #     #     """,
    #     # )

    #     always_on: Optional[bool] = Field(
    #         False, description="""Whether or not this lamp is always on."""
    #     )

    #     model_config = ConfigDict(title="Lamp")

    # @attrs.define
    # class ControlBehavior: # TODO: inherit ConditionMixins
    #     circuit_enabled: bool = attrs.field(default=False, validator=attrs.validators.instance_of(bool))

    #     connect_to_logistics_network: bool = attrs.field(default=False, validator=attrs.validators.instance_of(bool))

    #     use_colors: bool = attrs.field(default=False, validator=attrs.validators.instance_of(bool))

    #     color_mode: LampColorMode = attrs.field(default=LampColorMode.COLOR_MAPPING, converter=LampColorMode, validator=attrs.validators.instance_of(LampColorMode))

    @property
    def similar_entities(self) -> list:
        return lamps

    # def __init__(
    #     self,
    #     name: Optional[str] = get_first(lamps),
    #     position: Union[Vector, PrimitiveVector] = None,
    #     tile_position: Union[Vector, PrimitiveVector] = (0, 0),
    #     always_on: Optional[bool] = False,
    #     control_behavior: Format.ControlBehavior = {},
    #     tags: dict[str, Any] = {},
    #     validate_assignment: Union[
    #         ValidationMode, Literal["none", "minimum", "strict", "pedantic"]
    #     ] = ValidationMode.STRICT,
    #     **kwargs
    # ):
    #     """
    #     TODO
    #     """

    #     self._root: __class__.Format
    #     self.control_behavior: __class__.Format.ControlBehavior

    #     super().__init__(
    #         name,
    #         lamps,
    #         position=position,
    #         tile_position=tile_position,
    #         control_behavior=control_behavior,
    #         tags=tags,
    #         **kwargs
    #     )

    #     self.always_on = always_on

    #     self.validate_assignment = validate_assignment

    # =========================================================================

    # control_behavior: Optional[ControlBehavior] = attrs.field(factory=ControlBehavior, validator=attrs.validators.instance_of(ControlBehavior))

    # =========================================================================

    use_colors: bool = attrs.field(default=False, validator=instance_of(bool))
    """
    Whether or not this entity should use color signals to determine it's
    color.

    :exception TypeError: If set to anything other than a ``bool`` or ``None``.
    """

    # @use_colors.unstructure

    # @property
    # def use_colors(self) -> Optional[bool]:
    #     """
    #     Whether or not this entity should use color signals to determine it's
    #     color.

    #     :getter: Gets whether or not to use colors, or ``None`` if not set.
    #     :setter: Sets whether or not to use colors. Removes the key if set to
    #         ``None``.

    #     :exception TypeError: If set to anything other than a ``bool`` or ``None``.
    #     """
    #     return self.control_behavior.use_colors

    # @use_colors.setter
    # def use_colors(self, value: Optional[bool]):
    #     self.control_behavior.use_colors = value

    # =========================================================================

    color_mode: Optional[LampColorMode] = attrs.field(
        default=LampColorMode.COLOR_MAPPING,
        converter=LampColorMode,
        validator=instance_of(LampColorMode),
    )
    """
    In what way to interpret signals given to the lamp if `use_colors` is 
    ``True``.
    """

    # @property
    # def color_mode(self) -> Optional[LampColorMode]:
    #     """
    #     In what way to interpret signals given to the lamp if `use_colors` is
    #     ``True``.
    #     """
    #     return self.control_behavior.color_mode

    # @color_mode.setter
    # def color_mode(self, value: Optional[LampColorMode]) -> None:
    #     self.control_behavior.color_mode = value

    # =========================================================================

    always_on: Optional[bool] = attrs.field(default=False, validator=instance_of(bool))
    """
    Whether or not this entity should always be active, regardless of the
    current day-night cycle. This option is superceeded by any condition
    simultaneously specified.
    """

    # @property
    # def always_on(self) -> Optional[bool]:
    #     """
    #     Whether or not this entity should always be active, regardless of the
    #     current day-night cycle. This option is superceeded by any condition
    #     specified.

    #     :getter: Gets whether or not this lamp is always on, or ``None`` if not
    #         set.
    #     :setter: Sets whether or not the lamp is always on. Removes the key if
    #         set to ``None``.
    #     """
    #     return self._root.always_on

    # @always_on.setter
    # def always_on(self, value: Optional[bool]) -> None:
    #     self._root.always_on = value

    # =========================================================================

    color: AttrsColor = attrs.field(
        default=AttrsColor(r=1.0, g=1.0, b=191 / 255, a=1.0),
        converter=AttrsColor.converter,
        validator=instance_of(AttrsColor),
    )
    """
    What (static) color should this lamp have. Setting the lamp's color via
    ``use_colors`` and ``color_mode`` overrides this value if either are present.
    """
    # TODO: different defaults for different Factorio versions
    # < 2.0: white
    # >= 2.0: off-white

    # =========================================================================

    def merge(self, other: "Lamp"):
        super().merge(other)

        self.use_colors = other.use_colors
        self.color_mode = other.color_mode
        self.always_on = other.always_on
        self.color = other.color

    # =========================================================================

    __hash__ = Entity.__hash__


# TODO: versioning
draftsman_converters.get_version((2, 0)).add_schema(
    {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "$id": "factorio:lamp_v2.0",
        "$ref": "factorio:entity_v2.0",
        "allOf": [
            {"$ref": "factorio:circuit_condition"},
            {"$ref": "factorio:logistic_condition"},
        ],
        "type": "object",
        "properties": {
            "control_behavior": {
                "properties": {
                    "use_colors": {
                        "type": "boolean",
                        "default": "true",
                    },
                    "color_mode": {
                        "type": "integer",
                        "enum": [
                            LampColorMode.COLOR_MAPPING,
                            LampColorMode.COMPONENTS,
                            LampColorMode.PACKED_RGB,
                        ],
                        "default": LampColorMode.COLOR_MAPPING,
                    },
                }
            },
            "always_on": {
                "type": "boolean",
                "default": "false",
            },
            "color": {
                "$ref": "factorio:color",
                "default": {"r": 255, "g": 255, "b": 191, "a": 255},
            },
        },
    },
    Lamp,
    lambda fields: {
        ("control_behavior", "use_colors"): fields.use_colors.name,
        ("control_behavior", "color_mode"): fields.color_mode.name,
        "always_on": fields.always_on.name,
        "color": fields.color.name,
    },
)
