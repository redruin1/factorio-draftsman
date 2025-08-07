# simple_entity_with_force.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import DirectionalMixin, VariationMixin
from draftsman.serialization import draftsman_converters
from draftsman.utils import fix_incorrect_pre_init

from draftsman.data.entities import simple_entities_with_force

import attrs


@fix_incorrect_pre_init
@attrs.define
class SimpleEntityWithForce(VariationMixin, DirectionalMixin, Entity):
    """
    A generic entity associated with friends or foes.
    """

    @property
    def similar_entities(self) -> list[str]:
        return simple_entities_with_force


draftsman_converters.add_hook_fns(
    SimpleEntityWithForce, lambda fields: {"variation": fields.variation.name}
)
