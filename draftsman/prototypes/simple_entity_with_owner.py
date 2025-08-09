# simple_entity_with_owner.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import DirectionalMixin, VariationMixin
from draftsman.serialization import draftsman_converters
from draftsman.utils import fix_incorrect_pre_init

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


draftsman_converters.add_hook_fns(
    SimpleEntityWithOwner, lambda fields: {"variation": fields.variation.name}
)
