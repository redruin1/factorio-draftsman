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
from draftsman.schemas import (
    schemas,
    add_schema,
    make_structure_from_JSON_schema,
    make_unstructure_from_JSON_schema,
)
from draftsman.serialization import (
    MASTER_CONVERTER_OMIT_NONE_DEFAULTS,
    draftsman_converters,
    finalize_fields,
)
from draftsman.signatures import AttrsColor, Connections, DraftsmanBaseModel
from draftsman.utils import get_first

from draftsman.data.entities import lamps

import attrs
import cattrs
from pydantic import ConfigDict, Field
from typing import Any, Literal, Optional, Union


@attrs.define  # (field_transformer=finalize_fields)
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


# class CircuitConditionMixin:
#     class ControlBehavior:
#         circuit_enabled = pass

entity_fields = Entity.__attrs_attrs__  # attrs.fields(Entity)
# entity_format = {
#     "entity_number": None,
#     "name": entity_fields.name,
#     "position": entity_fields.position,
#     "tags": entity_fields.tags
# }

lamp_fields = Lamp.__attrs_attrs__  # attrs.fields(Lamp)
# lamp_format = merge(dict(entity_format), {
#     "control_behavior": {
#         "circuit_enabled": lamp_fields.circuit_enabled,
#         "circuit_condition": lamp_fields.circuit_condition,
#         "connect_to_logistic_network": lamp_fields.connect_to_logistic_network,
#         # "logistic_condition": lamp_fields.logistic_condition,
#         "use_colors": lamp_fields.use_colors,
#         "color_mode": lamp_fields.color_mode
#     },
#     "always_on": lamp_fields.always_on,
#     "color": lamp_fields.color,
# })

add_schema(
    {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "$id": "factorio:entity_v2.0",
        "version": (2, 0),
        "type": "object",
        "properties": {
            "entity_number": {
                "type": "integer",
                "minimum": 0,
                "exclusiveMaximum": 2 ^ 64,
                "location": None,  # strip entity number on import
            },
            "name": {"type": "string", "location": entity_fields.name},
            "position": {
                "$ref": "factorio:position",
                "location": entity_fields.position,
            },
            "tags": {"type": "object", "location": entity_fields.tags},
        },
    },
    Entity
)

add_schema(
    {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "$id": "factorio:circuit_condition",
        "properties": {
            "control_behavior": {
                "type": "object",
                "properties": {
                    "circuit_enabled": {
                        "type": "boolean",
                        "default": "false",
                        "location": lamp_fields.circuit_enabled,
                    },
                    # "circuit_condition": {
                    # }
                },
            }
        },
    }
)

add_schema(
    {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "$id": "factorio:logistic_condition",
        "properties": {
            "control_behavior": {
                "type": "object",
                "properties": {
                    "connect_to_logistic_network": {
                        "type": "boolean",
                        "default": "false",
                        "location": lamp_fields.connect_to_logistic_network,
                    }
                },
            }
        },
    }
)

add_schema(
    {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "$id": "factorio:lamp_v2.0",
        "$ref": "factorio:entity_v2.0",
        "allOf": [
            {"$ref": "factorio:circuit_condition"},
            {"$ref": "factorio:logistic_condition"},
        ],
        "version": (2, 0),
        "type": "object",
        "properties": {
            "control_behavior": {
                "properties": {
                    "use_colors": {
                        "type": "boolean",
                        "default": "true",
                        "location": lamp_fields.use_colors,
                    },
                    "color_mode": {
                        "type": "integer",
                        "enum": [
                            LampColorMode.COLOR_MAPPING,
                            LampColorMode.COMPONENTS,
                            LampColorMode.PACKED_RGB,
                        ],
                        "default": LampColorMode.COLOR_MAPPING,
                        "location": lamp_fields.color_mode,
                    },
                }
            },
            "always_on": {
                "type": "boolean",
                "default": "false",
                "location": lamp_fields.always_on,
            },
            "color": {
                "$ref": "factorio:color",
                "default": {"r": 255, "g": 255, "b": 191, "a": 255},
                "location": lamp_fields.color,
            },
        },
    },
    Lamp,
)


def make_structure_function(cls, format_dict):
    def traverse_format(format: dict, input: dict):
        print("format:", format)
        print("d:", input)
        res = {}
        if "properties" in format:
            for property_name, property in format["properties"].items():
                print("\t", property_name, property)
                # location = property["location"]
                if "location" in property and property["location"] is None:
                    input.pop(property_name)
                    continue
                if property_name in input:
                    print(property)
                    # If "location" is detected, set the attribute and avoid
                    # travelling deeper into the tree
                    if "location" in property:
                        res[property["location"].name] = input[property_name]
                        input.pop(property_name)
                    elif property["type"] == "object":
                        res.update(traverse_format(property, input[property_name]))
                        # If the result dict becomes empty after traversal, delete it
                        if not input[property_name]:
                            input.pop(property_name)
                    # else:
                    #     res[property["location"].name] = input[property_name]
                    #     input.pop(property_name)
        print("d exit:", input)
        return res

    def structure_hook(d: dict, t: type):
        res = traverse_format(format_dict, d)

        print("test")
        print(res)
        print(d)

        # If there's anything left in d, that is our unknown keys
        if len(d) != 0:
            res["unknown"] = d

        return cls(**res)

    return structure_hook


draftsman_converters.register_structure_hook(
    Lamp, make_structure_from_JSON_schema(Lamp, schemas["factorio:lamp_v2.0"])
)

draftsman_converters.register_unstructure_hook(
    Lamp, make_unstructure_from_JSON_schema(Lamp, schemas["factorio:lamp_v2.0"])
)
