# color.py

from draftsman.classes.exportable import Exportable
from draftsman.serialization import draftsman_converters
from draftsman.signatures import AttrsColor
from draftsman.validators import instance_of

import attrs
from typing import Optional


@attrs.define(slots=False)
class ColorMixin(Exportable):
    """
    Gives the entity an editable color.
    """

    # class Format(BaseModel):
    #     color: Optional[Color] = Field(
    #         None,
    #         description="""
    #         The color modifier used to alter this entity's appearence.
    #         """,
    #     )

    # def __init__(self, name: str, similar_entities: list[str], **kwargs):
    #     self._root: __class__.Format

    #     super().__init__(name, similar_entities, **kwargs)

    #     self.color = kwargs.get("color", None)

    # =========================================================================

    color: Optional[AttrsColor] = attrs.field(
        default=AttrsColor(r=1.0, g=1.0, b=1.0, a=1.0),
        converter=AttrsColor.converter,
        validator=instance_of(Optional[AttrsColor]),
    )
    """
    The color of the Entity.

    The ``color`` attribute exists in a dict format with the "r", "g",
    "b", and an optional "a" keys. The color can be specified like that, or
    it can be specified more succinctly as a sequence of 3-4 numbers,
    representing the colors in that order.

    The value of each of the numbers (according to Factorio spec) can be
    either in the range of [0.0, 1.0] or [0, 255]; if all the numbers are
    <= 1.0, the former range is used, otherwise the latter. If "a" is
    omitted, it defaults to 1.0 or 255 when imported, depending on the
    range of the other numbers.
    """

    # @property
    # def color(self) -> Color:
    #     """
    #     The color of the Entity.

    #     The ``color`` attribute exists in a dict format with the "r", "g",
    #     "b", and an optional "a" keys. The color can be specified like that, or
    #     it can be specified more succinctly as a sequence of 3-4 numbers,
    #     representing the colors in that order.

    #     The value of each of the numbers (according to Factorio spec) can be
    #     either in the range of [0.0, 1.0] or [0, 255]; if all the numbers are
    #     <= 1.0, the former range is used, and the latter otherwise. If "a" is
    #     omitted, it defaults to 1.0 or 255 when imported, depending on the
    #     range of the other numbers.

    #     :getter: Gets the color of the Entity, or ``None`` if not set.
    #     :setter: Sets the color of the Entity.

    #     :exception DataFormatError: If the set ``color`` does not match the
    #         above specification.
    #     """
    #     return self._root.color

    # @color.setter
    # def color(self, value: Union[list[float], Color]):
    #     # value = normalize_color(value)
    #     test_replace_me(
    #         self,
    #         type(self).Format,
    #         self._root,
    #         "color",
    #         value,
    #         self.validate_assignment,
    #     )
    #     # if self.validate_assignment:
    #     #     result = attempt_and_reissue(
    #     #         self, type(self).Format, self._root, "color", value
    #     #     )
    #     #     self._root.color = result
    #     # else:
    #     #     self._root.color = value

    # =========================================================================

    def merge(self, other: "ColorMixin"):
        super().merge(other)

        self.color = other.color

    # =========================================================================

    # def __eq__(self, other) -> bool:
    #     return super().__eq__(other) and self.color == other.color


draftsman_converters.add_hook_fns(
    # {"$id": "factorio:color_mixin"},
    ColorMixin,
    lambda fields: {"color": fields.color.name},
)
