# simple_entity_with_owner.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import DirectionalMixin, VariationMixin
from draftsman.serialization import draftsman_converters
from draftsman.signatures import uint16
from draftsman.utils import fix_incorrect_pre_init
from draftsman.validators import instance_of

from draftsman.data.entities import simple_entities_with_owner

import attrs


@fix_incorrect_pre_init
@attrs.define
class SimpleEntityWithOwner(VariationMixin, DirectionalMixin, Entity):
    """
    A generic entity owned by some other entity.
    """

    # =========================================================================

    @property
    def similar_entities(self) -> list[str]:
        return simple_entities_with_owner

    # =========================================================================

    variation: uint16 = attrs.field(default=1, validator=instance_of(uint16))
    """
    The graphical variation of the entity.
    """


SimpleEntityWithOwner.add_schema(
    {
        "$id": "urn:factorio:entity:simple-entity-with-force",
        "properties": {"variation": {"$ref": "urn:uint16", "default": 1}},
    }
)

draftsman_converters.add_hook_fns(
    SimpleEntityWithOwner, lambda fields: {"variation": fields.variation.name}
)
