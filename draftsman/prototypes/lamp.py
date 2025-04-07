# lamp.py

from draftsman.classes.entity import Entity
from draftsman.classes.exportable import attempt_and_reissue
from draftsman.classes.mixins import (
    ColorMixin,
    CircuitConditionMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
)
from draftsman.classes.vector import Vector, PrimitiveVector
from draftsman.constants import ValidationMode, LampColorMode
from draftsman.serialization import draftsman_converters, finalize_fields
from draftsman.signatures import AttrsColor, Connections, DraftsmanBaseModel
from draftsman.utils import get_first

from draftsman.data.entities import lamps

import attrs
import cattrs
from pydantic import ConfigDict, Field
from typing import Any, Literal, Optional, Union


@attrs.define # (field_transformer=finalize_fields)
class Lamp(
    ColorMixin,
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

    use_colors: Optional[bool] = attrs.field(
        default=False,
        validator=attrs.validators.instance_of(bool),
        metadata={"location": ("control_behavior", "use_colors")},
    )
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
        validator=attrs.validators.instance_of(LampColorMode),
        metadata={"location": ("control_behavior", "color_mode")},
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

    always_on: Optional[bool] = attrs.field(
        default=False, validator=attrs.validators.instance_of(bool)
    )
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

    color: Optional[AttrsColor] = attrs.field(
        default=AttrsColor(r=1.0, g=1.0, b=191 / 255, a=1.0),
        converter=AttrsColor.converter,
        validator=attrs.validators.instance_of(AttrsColor),
    )
    """
    What (static) color should this lamp have. Setting the lamp's color via
    ``use_colors`` and ``color_mode`` overrides this value if both are present.
    """

    # @property
    # def color(self) -> Optional[Color]:
    #     """
    #     TODO
    #     """
    #     return self._root.color

    # @color.setter
    # def color(self, value: Optional[Color]):
    #     self._root.color = value

    # =========================================================================

    # __hash__ = Entity.__hash__


# draftsman_converters.register_unstructure_hook(
#     Lamp,
#     cattrs.gen.make_dict_unstructure_fn(
#         Lamp,
#         draftsman_converters[(1, 0)],
#         _cattrs_omit_if_default=True,
#         name=cattrs.gen.override(omit_if_default=False),
#         position=cattrs.gen.override(omit_if_default=False),
#         id=cattrs.gen.override(omit=True)
#     )
# )
# a = cattrs.gen.make_dict_unstructure_fn(
#         Lamp,
#         draftsman_converters[(2, 0)],
#         _cattrs_omit_if_default=False,
#         name=cattrs.gen.override(omit_if_default=False),
#         position=cattrs.gen.override(omit_if_default=False),
#         id=cattrs.gen.override(omit=True)
#     )
# draftsman_converters[(2, 0)].register_unstructure_hook(
#     Lamp,
#     a
# )

# @draftsman_converters[(1, 0)].register_structure_hook
# def structure_lamp(d: dict, t: type) -> Lamp:
#     print("a", d)
#     d.pop("entity_number")
#     return Lamp(
#         **d
#     )

# def unstructure_lamp(input: Lamp) -> dict:
#     return {}

# draftsman_converters[(1, 0)].register_structure_hook(
#     Lamp,
#     structure_lamp
# )
# draftsman_converters[(2, 0)].register_structure_hook(
#     Lamp,
#     structure_lamp
# )
