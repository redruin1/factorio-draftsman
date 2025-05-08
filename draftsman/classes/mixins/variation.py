# variation.py

from draftsman.serialization import draftsman_converters
from draftsman.signatures import uint16
from draftsman.validators import instance_of

import attrs


@attrs.define(slots=False)
class VariationMixin:
    """
    Mixin that gives the entity a graphical variation index. Used for decorative
    entities like text-plates.
    """

    variation: uint16 = attrs.field(default=1, validator=instance_of(uint16))
    """
    The graphical variation of the entity.
    """


draftsman_converters.add_hook_fns(
    # {"$id": "factorio:simple_entity_with_owner"},
    VariationMixin,
    lambda fields: {"variation": fields.variation.name},
)
