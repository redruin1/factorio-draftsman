# heat_pipe.py

from draftsman.classes.entity import Entity

from draftsman.data.entities import heat_pipes

import attrs


@attrs.define
class HeatPipe(Entity):
    """
    An entity used to transfer thermal energy.
    """

    @property
    def similar_entities(self) -> list[str]:
        return heat_pipes

    # =========================================================================

    __hash__ = Entity.__hash__


HeatPipe.add_schema({"$id": "urn:factorio:entity:heat-pipe"})
