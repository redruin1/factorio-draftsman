# io_type.py

# TODO: make this an enum?

from draftsman.classes.exportable import Exportable
from draftsman.serialization import draftsman_converters
from draftsman.validators import one_of

import attrs
from typing import Literal


@attrs.define(slots=False)
class IOTypeMixin(Exportable):
    """
    Gives an entity a Input/Output type.
    """

    io_type: Literal["input", "output", None] = attrs.field(
        default="input", validator=one_of("input", "output", None)
    )
    """
    Whether this entity is set to recieve or send items. Used to
    differentiate between input and output underground belts/pipes, as well as
    whether or not a loader inserts or removes items from an adjacent
    container. Can be one of ``"input"`` or ``"output"``.
    """

    # =========================================================================

    def merge(self, other: "IOTypeMixin"):
        super().merge(other)

        self.io_type = other.io_type


draftsman_converters.add_hook_fns(
    # {"$id": "factorio:io_type_mixin"},
    IOTypeMixin,
    lambda fields: {"type": fields.io_type.name},
)
