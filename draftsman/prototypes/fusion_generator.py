# fusion_generator.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import EnergySourceMixin, DirectionalMixin
from draftsman.utils import fix_incorrect_pre_init

from draftsman.data.entities import fusion_generators

import attrs


@fix_incorrect_pre_init
@attrs.define
class FusionGenerator(EnergySourceMixin, DirectionalMixin, Entity):
    """
    An entity which converts plasma into energy.
    """

    @property
    def similar_entities(self) -> list[str]:
        return fusion_generators

    # =========================================================================

    __hash__ = Entity.__hash__


FusionGenerator.add_schema(None, version=(1, 0))

FusionGenerator.add_schema(
    {
        "$id": "urn:factorio:entity:fusion-generator",
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "properties": {
            "entity_number": {"$ref": "urn:uint64"},
            "name": {"type": "string"},
            "position": {"$ref": "urn:factorio:position"},
            "quality": {"$ref": "urn:factorio:quality-name"},
            "tags": {"type": "object"},
        },
        "required": ["entity_number", "name", "position"],
    },
    version=(2, 0),
)
