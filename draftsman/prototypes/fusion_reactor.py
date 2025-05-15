# fusion_reactor.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import EnergySourceMixin, DirectionalMixin

from draftsman.data.entities import fusion_reactors

import attrs


@attrs.define
class FusionReactor(EnergySourceMixin, DirectionalMixin, Entity):
    """
    A reactor which produces hot plasma.
    """

    @property
    def similar_entities(self) -> list[str]:
        return fusion_reactors

    # =========================================================================

    __hash__ = Entity.__hash__


FusionReactor.add_schema(None, version=(1, 0))

FusionReactor.add_schema({"$id": "urn:factorio:entity:fusion-reactor"}, version=(2, 0))
