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

    # =========================================================================

    def merge(self, other: "ColorMixin"):
        super().merge(other)

        self.color = other.color


ColorMixin.add_schema({"properties": {"color": {"$ref": "urn:factorio:color"}}})

draftsman_converters.add_hook_fns(
    ColorMixin,
    lambda fields: {"color": fields.color.name},
)
