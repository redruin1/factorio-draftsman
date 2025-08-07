# color.py

from draftsman.classes.exportable import Exportable
from draftsman.serialization import draftsman_converters
from draftsman.signatures import Color
from draftsman.validators import instance_of

import attrs
from typing import Optional


@attrs.define(slots=False)
class ColorMixin(Exportable):
    """
    Gives the entity an editable color.
    """

    color: Optional[Color] = attrs.field(
        default=Color(r=1.0, g=1.0, b=1.0, a=1.0),
        converter=Color.converter,
        validator=instance_of(Optional[Color]),
    )
    """
    .. serialized::

        This attribute is imported/exported from blueprint strings.

    The :py:attr:`.Color` of the Entity.
    """

    # =========================================================================

    def merge(self, other: "ColorMixin"):
        super().merge(other)

        self.color = other.color


draftsman_converters.add_hook_fns(
    ColorMixin,
    lambda fields: {"color": fields.color.name},
)
